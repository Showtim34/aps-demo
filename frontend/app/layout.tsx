import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "APS Lab Monitor",
  description: "Industrial monitoring demo built with Next.js and FastAPI.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
