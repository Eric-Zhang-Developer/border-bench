import type { Metadata } from "next";
import { DM_Mono, Newsreader } from "next/font/google";
import "./globals.css";

// Both typefaces are fetched once at build time and served from this site: no request to Google at runtime.
const serif = Newsreader({
  subsets: ["latin"],
  style: ["normal", "italic"],
  axes: ["opsz"],
  variable: "--font-newsreader",
});
const mono = DM_Mono({ subsets: ["latin"], weight: ["400", "500"], variable: "--font-dm-mono" });

export const metadata: Metadata = {
  title: "BorderBench",
  description:
    "AI models draw countries from memory. Each drawing is laid over the real border.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${serif.variable} ${mono.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
