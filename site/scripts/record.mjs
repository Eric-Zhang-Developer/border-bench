// Turns the head-to-head page into a video file, frame by frame.
//
//   npm --prefix site run build                                   (the recorder films the built site, not the dev server)
//   npm --prefix site run record                                  (Indonesia, oldest model against newest)
//   npm --prefix site run record -- --target chile --still        (only the last frame, as a PNG)
//   npm --prefix site run record -- --target poland-1938 --left claude-haiku-5-5 --right claude-fable-5-2 --out clips/poland
//
// It serves site/out/ on a local port, opens /duel in the Chrome already on this machine (headless, dark, 1920 by
// 1080), and puts the page's clock at each sixtieth of a second in turn, taking a picture every time. The pictures
// go straight to ffmpeg. Nothing is filmed in real time, so the same pair always gives the same frames.
// No dependency: Chrome is driven over its DevTools protocol with Node's own WebSocket.
//
// Options: --target, --left, --right (ids from the results file; defaults are the page's own), --out (path without
// an extension, default clips/<target>), --still (last frame only), --at <ms> (a still at that moment instead).
// CHROME and FFMPEG name other binaries.
import { spawn } from "node:child_process";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { parseArgs } from "node:util";

const FPS = 60, WIDTH = 1920, HEIGHT = 1080;
const site = path.resolve(import.meta.dirname, "..");
const { values: opt } = parseArgs({
  options: {
    target: { type: "string" }, left: { type: "string" }, right: { type: "string" },
    out: { type: "string" }, still: { type: "boolean" }, at: { type: "string" },
  },
});
const out = path.resolve(site, opt.out ?? `clips/${opt.target ?? "indonesia"}`);
const say = (line) => process.stdout.write(line + "\n");

if (!fs.existsSync(path.join(site, "out", "duel.html"))) {
  process.stderr.write("record: site/out/duel.html is missing. Run `npm --prefix site run build` first.\n");
  process.exit(1);
}

// ---- the built site, on a local port ----------------------------------------------------------------------
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".css": "text/css", ".svg": "image/svg+xml", ".woff2": "font/woff2", ".txt": "text/plain" };
const server = http.createServer((req, res) => {
  const want = decodeURIComponent(new URL(req.url, "http://x").pathname);
  const file = path.join(site, "out", want === "/" ? "index.html" : path.extname(want) ? want : want + ".html");
  if (!file.startsWith(path.join(site, "out")) || !fs.existsSync(file)) return res.writeHead(404).end();
  res.writeHead(200, { "content-type": TYPES[path.extname(file)] ?? "application/octet-stream" }).end(fs.readFileSync(file));
});
await new Promise((ready) => server.listen(0, "127.0.0.1", ready));
const query = new URLSearchParams({ frame: "1" });
for (const key of ["target", "left", "right"]) if (opt[key]) query.set(key, opt[key]);
const url = `http://127.0.0.1:${server.address().port}/duel?${query}`;

// ---- Chrome, over its DevTools protocol --------------------------------------------------------------------
const profile = fs.mkdtempSync(path.join(os.tmpdir(), "borderbench-record-"));
const chrome = spawn(process.env.CHROME ?? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", [
  "--headless=new", "--remote-debugging-port=0", `--user-data-dir=${profile}`, `--window-size=${WIDTH},${HEIGHT}`,
  "--hide-scrollbars", "--no-first-run", "--no-default-browser-check", "--force-color-profile=srgb", "about:blank",
]);
const socketUrl = await new Promise((found, failed) => {
  let seen = "";
  chrome.stderr.on("data", (chunk) => {
    seen += chunk;
    const match = seen.match(/DevTools listening on (ws:\/\/\S+)/);
    if (match) found(match[1]);
  });
  chrome.on("exit", () => failed(new Error("record: Chrome exited before it could be reached\n" + seen)));
});
const socket = new WebSocket(socketUrl);
await new Promise((open) => socket.addEventListener("open", open, { once: true }));
const waiting = new Map();
let lastId = 0, session;
socket.addEventListener("message", ({ data }) => {
  const message = JSON.parse(data);
  const entry = waiting.get(message.id);
  if (!entry) return;
  waiting.delete(message.id);
  if (message.error) entry.failed(new Error(`record: ${entry.method}: ${message.error.message}`));
  else entry.done(message.result);
});
const send = (method, params = {}) =>
  new Promise((done, failed) => {
    waiting.set(++lastId, { done, failed, method });
    socket.send(JSON.stringify({ id: lastId, method, params, sessionId: session }));
  });
const run = async (expression) => {
  const { result, exceptionDetails } = await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
  if (exceptionDetails) throw new Error("record: the page threw: " + (exceptionDetails.exception?.description ?? exceptionDetails.text));
  return result.value;
};

let ffmpeg;
try {
  const { targetId } = await send("Target.createTarget", { url: "about:blank" });
  session = (await send("Target.attachToTarget", { targetId, flatten: true })).sessionId;
  await send("Emulation.setDeviceMetricsOverride", { width: WIDTH, height: HEIGHT, deviceScaleFactor: 1, mobile: false });
  // Headless Chrome is light by default; the clip is dark. Reduced motion would open on the last frame.
  await send("Emulation.setEmulatedMedia", {
    features: [{ name: "prefers-color-scheme", value: "dark" }, { name: "prefers-reduced-motion", value: "no-preference" }],
  });
  await send("Page.enable");
  await send("Page.navigate", { url });

  // Wait for the page to have the pair up and its typefaces loaded, then stop its own clock at zero.
  let pair;
  for (let tries = 0; !pair; tries++) {
    if (tries > 200) throw new Error("record: the page never became ready at " + url);
    await new Promise((later) => setTimeout(later, 50));
    pair = await run("document.fonts.ready.then(() => document.fonts.status === 'loaded' && window.duel ? window.duel : null)");
  }
  for (const [i, key] of ["target", "left", "right"].entries())
    if (opt[key] && pair.key.split("|")[i] !== opt[key]) throw new Error(`record: no ${key} called ${opt[key]} in the results`);
  if (await run("!!document.querySelector('.banner')"))
    throw new Error("record: this build is on the made-up sample data (no results/results.json). A clip of it would pass for a result, so none is made.");
  await run("window.duel.seek(0)");

  const shot = async (ms) => {
    await run(`window.duel.seek(${ms})`);
    return Buffer.from((await send("Page.captureScreenshot", { format: "png", optimizeForSpeed: true })).data, "base64");
  };

  fs.mkdirSync(path.dirname(out), { recursive: true });
  if (opt.at !== undefined || opt.still) {
    fs.writeFileSync(out + ".png", await shot(opt.at !== undefined ? Number(opt.at) : pair.duration));
    say(`record: ${path.relative(site, out)}.png (${pair.key.split("|").join(", ")})`);
  } else {
    ffmpeg = spawn(process.env.FFMPEG ?? "ffmpeg", [
      "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "png", "-i", "-",
      // H.264, 4:2:0, tagged BT.709: what QuickTime and X both expect of a 1080p file.
      "-vf", "scale=out_color_matrix=bt709:out_range=tv", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
      "-pix_fmt", "yuv420p", "-profile:v", "high", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
      "-color_range", "tv", "-r", String(FPS), "-movflags", "+faststart", out + ".mp4",
    ], { stdio: ["pipe", "inherit", "inherit"] });
    const frames = Math.ceil((pair.duration / 1000) * FPS);
    let last;
    for (let i = 0; i <= frames; i++) {
      last = await shot(Math.min(pair.duration, (i * 1000) / FPS));
      if (!ffmpeg.stdin.write(last)) await new Promise((drained) => ffmpeg.stdin.once("drain", drained));
      if (i % 120 === 0) say(`record: frame ${i} of ${frames}`);
    }
    ffmpeg.stdin.end();
    const code = await new Promise((closed) => ffmpeg.on("close", closed));
    if (code !== 0) throw new Error(`record: ffmpeg stopped with code ${code}`);
    fs.writeFileSync(out + ".png", last);
    say(`record: ${path.relative(site, out)}.mp4 and .png (${pair.key.split("|").join(", ")}; ${frames + 1} frames, ${(pair.duration / 1000).toFixed(1)} s)`);
  }
} finally {
  socket.close();
  chrome.kill();
  server.close();
  await new Promise((gone) => chrome.once("exit", gone));
  fs.rmSync(profile, { recursive: true, force: true });
}
