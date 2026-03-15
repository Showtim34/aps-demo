import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Factory Ops Console",
  description: "Operational console for creating machines and triggering alerts.",
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
