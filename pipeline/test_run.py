"""The runner with the SDK mocked: no network, no key. Messages are built with the SDK's own types."""

import json
from datetime import datetime, timezone
from types import SimpleNamespace

import anthropic
import httpx2
import pytest
from anthropic.types import Message

from pipeline import run

HAIKU = {"id": "claude-haiku-4-5-20251001", "created_at": "2025-10-01T00:00:00+00:00"}
TARGETS = [{"id": "usa", "name": "the contiguous United States as of 1 January 2024"}]


def message(text='{"type": "MultiPolygon", "coordinates": [[[[-100.0, 40.0]]]]}', stop_reason="end_turn",
            stop_details=None, output_tokens=20000):
    content = [{"type": "text", "text": text}] if text else []
    return Message.model_validate({
        "id": "msg_test", "type": "message", "role": "assistant", "model": HAIKU["id"], "content": content,
        "stop_reason": stop_reason, "stop_sequence": None, "stop_details": stop_details,
        "usage": {"input_tokens": 100, "output_tokens": output_tokens},
    })


class FakeClient:
    """Stands in for anthropic.Anthropic: records every request and answers with one canned message."""

    def __init__(self, msg=None):
        self.requests, self.msg, self.messages = [], msg or message(), self

    def stream(self, **kwargs):
        self.requests.append(kwargs)
        return self

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def __iter__(self):
        """The stream's events: a thinking block first, then visible text if the canned message has any."""
        def delta(kind):
            return SimpleNamespace(type="content_block_delta", delta=SimpleNamespace(type=kind))
        yield SimpleNamespace(type="message_start")
        yield SimpleNamespace(type="content_block_start")
        yield delta("thinking_delta")
        if self.msg.content:
            yield delta("text_delta")
        yield SimpleNamespace(type="message_stop")

    def get_final_message(self):
        return self.msg


class FlakyClient(FakeClient):
    """Fails with `error` on the first request, then answers."""

    def __init__(self, error):
        super().__init__()
        self.error = error

    def stream(self, **kwargs):
        self.requests.append(kwargs)
        if len(self.requests) == 1:
            raise self.error
        return self


def saved_run(tmp_path):
    return json.loads((tmp_path / "runs/pilot/pilot-c" / HAIKU["id"] / "usa/1.json").read_text())


def go(tmp_path, client, **kw):
    prompt = tmp_path / "prompt.txt"
    if not prompt.exists():
        prompt.write_bytes(b"Draw {target}.\r\n  Keep  this spacing. \n\n")
    args = dict(prompt_file=prompt, prompt_id="pilot-c", set_name="pilot", targets=TARGETS, models=[HAIKU],
                samples=1, runs=tmp_path / "runs")
    return run.run(client, **{**args, **kw})


def test_the_prompt_sent_is_the_file_with_only_the_target_replaced_and_no_other_parameter(tmp_path):
    client = FakeClient()
    go(tmp_path, client)
    (request,) = client.requests
    # Exactly these three: no system prompt, tools, thinking, effort, sampling or fallback parameter.
    assert set(request) == {"model", "max_tokens", "messages"}
    assert request["model"] == HAIKU["id"] and request["max_tokens"] == 64000
    expected = b"Draw the contiguous United States as of 1 January 2024.\r\n  Keep  this spacing. \n\n"
    assert request["messages"] == [{"role": "user", "content": expected.decode()}]
    saved = json.loads((tmp_path / "runs/pilot/pilot-c" / HAIKU["id"] / "usa/1.json").read_text())
    assert saved["prompt"].encode() == expected
    assert saved["raw"] == client.msg.content[0].text  # the answer, exactly as returned
    assert saved["model_created_at"] == HAIKU["created_at"] and saved["target"] == TARGETS[0]["name"]
    assert saved["usage"]["output_tokens"] == 20000 and saved["cost_usd"] == 0.1001  # 100 in at $1, 20000 out at $5


def test_an_existing_run_file_is_never_overwritten_or_asked_for_again(tmp_path):
    existing = tmp_path / "runs/pilot/pilot-c" / HAIKU["id"] / "usa/1.json"
    existing.parent.mkdir(parents=True)
    existing.write_text('{"model": "claude-haiku-4-5", "usage": {"output_tokens": 1}, "raw": "the first answer"}')
    before = existing.read_bytes()
    client = FakeClient()
    result = go(tmp_path, client, samples=2)
    assert existing.read_bytes() == before
    assert len(client.requests) == 1 and result["made"] == 1 and result["skipped"] == 1  # only sample 2 was missing


def test_the_cap_stops_the_loop_before_spend_can_pass_it(tmp_path):
    # Each fake call costs $0.1001; a Haiku 4.5 call could cost up to about $0.32 (64000 tokens at $5 per million).
    client = FakeClient()
    result = go(tmp_path, client, samples=10, cap=0.50)
    assert len(client.requests) == 2  # a third could have reached $0.52
    assert "cap" in result["stopped"]
    assert run.spent(tmp_path / "runs") <= 0.50
    # Running again makes no call: the money is still spent.
    assert go(tmp_path, client, samples=10, cap=0.50)["made"] == 0 and len(client.requests) == 2


def test_a_refusal_is_saved_as_it_is_and_not_retried(tmp_path):
    refusal = message(text="", stop_reason="refusal", output_tokens=0,
                      stop_details={"type": "refusal", "category": None, "explanation": "declined"})
    client = FakeClient(refusal)
    go(tmp_path, client)
    saved = json.loads((tmp_path / "runs/pilot/pilot-c" / HAIKU["id"] / "usa/1.json").read_text())
    assert saved["raw"] == "" and saved["stop_reason"] == "refusal" and saved["stop_details"]["explanation"] == "declined"
    assert len(client.requests) == 1


def test_a_dry_run_makes_no_call_and_writes_nothing(tmp_path, capsys):
    result = go(tmp_path, None, dry_run=True, samples=3)  # client is None: any call would crash
    assert result["made"] == 3 and result["estimate"] > 0 and not (tmp_path / "runs").exists()
    assert capsys.readouterr().out.count("would call") == 3


def test_the_lineup_drops_mythos_and_preview_and_is_ordered_by_release_date():
    def m(id, day):
        return SimpleNamespace(id=id, created_at=day and datetime(2026, 1, day, tzinfo=timezone.utc), retires_at=None)

    api = SimpleNamespace(models=SimpleNamespace(list=lambda: [
        m("claude-b", 2), m("claude-mythos-5-1", 3), m("claude-undated", None), m("claude-a", 1),
        m("claude-mythos-preview", 4)]))
    assert [x["id"] for x in run.list_models(api)] == ["claude-a", "claude-b", "claude-undated"]


def test_prices_ignore_a_date_suffix_and_an_unknown_model_is_charged_at_the_dearest_rate():
    assert run.price("claude-sonnet-4-5-20250929") == run.price("claude-sonnet-4-5") == (3.0, 15.0)
    assert run.price("claude-opus-5-9") == (10.0, 50.0)  # not in the table: never priced as claude-opus-5


def test_targets_load_from_a_target_file_or_a_list_file(tmp_path):
    one, many = tmp_path / "target.toml", tmp_path / "targets.toml"
    one.write_text('id = "usa"\nname = "A as of 1 January 2024"\ndate = "2024-01-01"\n')
    many.write_text('[[target]]\nid = "b"\nname = "B"\n\n[[target]]\nid = "c"\nname = "C"\n')
    assert [t["id"] for t in run.load_targets([one, many])] == ["usa", "b", "c"]


def test_every_run_file_records_timing_full_usage_and_what_it_was_priced_with(tmp_path):
    client = FakeClient()
    go(tmp_path, client)
    saved = saved_run(tmp_path)
    assert datetime.fromisoformat(saved["started_at"]).tzinfo is not None
    assert 0 <= saved["first_token_ms"] <= saved["first_text_ms"] <= saved["duration_ms"]
    assert saved["attempts"] == 1
    assert saved["usage"] == client.msg.usage.model_dump(mode="json")  # every field the SDK returned, not a subset
    assert saved["sdk_version"] == anthropic.__version__ and saved["price_table_date"] == run.PRICE_TABLE_DATE


def test_an_answer_with_no_visible_text_has_no_first_text_time(tmp_path):
    go(tmp_path, FakeClient(message(text="", stop_reason="refusal", output_tokens=0)))
    saved = saved_run(tmp_path)
    assert saved["first_text_ms"] is None and 0 <= saved["first_token_ms"] <= saved["duration_ms"]


def test_a_dropped_connection_is_retried_and_the_retry_is_visible(tmp_path):
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    client = FlakyClient(anthropic.APIConnectionError(request=request))
    go(tmp_path, client, sleep=lambda seconds: None)
    assert len(client.requests) == 2 and saved_run(tmp_path)["attempts"] == 2


def test_a_rejected_request_is_not_retried(tmp_path):
    response = httpx2.Response(400, request=httpx2.Request("POST", "https://api.anthropic.com/v1/messages"))
    client = FlakyClient(anthropic.BadRequestError("bad request", response=response, body=None))
    with pytest.raises(anthropic.BadRequestError):
        go(tmp_path, client, sleep=lambda seconds: None)
    assert len(client.requests) == 1 and not (tmp_path / "runs").exists()


def test_a_stream_may_stay_silent_for_an_hour_and_the_sdk_does_not_retry_on_its_own(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "not-a-real-key")
    client = run.make_client()
    assert client.timeout.read == 3600.0 and client.timeout.connect == 30.0 and client.max_retries == 0


def test_a_stream_that_dies_mid_answer_is_not_asked_again_and_says_it_was_not_counted(tmp_path, capsys):
    class DiesMidStream(FakeClient):
        def __iter__(self):
            yield SimpleNamespace(type="message_start")
            raise httpx2.ReadTimeout("The read operation timed out")

    client = DiesMidStream()
    with pytest.raises(httpx2.ReadTimeout):
        go(tmp_path, client, sleep=lambda seconds: None)
    assert len(client.requests) == 1 and not (tmp_path / "runs").exists()  # asking again would be paid for again
    assert "NOT in the running total" in capsys.readouterr().out
