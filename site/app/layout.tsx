import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BorderBench",
  description:
    "AI models draw countries from memory. Each drawing is laid over the real border.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
