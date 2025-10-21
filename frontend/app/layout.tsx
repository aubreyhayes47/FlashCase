import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FlashCase - Law School Flashcards",
  description: "Modern flashcard app tailored for law students with spaced repetition and AI-powered content.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
