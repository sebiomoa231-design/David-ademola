import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "David AI · Command Center",
  description: "A human-guided intelligence workspace for David AI.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
