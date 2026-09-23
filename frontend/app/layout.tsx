import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SanjivaniAI — Knowledge Assistant for Sanjivani University",
  description:
    "AI-powered knowledge assistant for Sanjivani University, grounded in official university documents.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
