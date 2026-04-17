import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navigation from "@/components/Navigation";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "GRE Issue Writing Grader",
  description:
    "AI-powered multi-agent grading system for GRE Issue Writing essays",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Navigation />
        <main className="min-h-screen">{children}</main>
        <footer className="bg-gray-800 text-gray-300 py-8 mt-12">
          <div className="max-w-6xl mx-auto px-4 text-center">
            <p>GRE Issue Writing Grader • Powered by LangChain & LangGraph</p>
            <p className="text-sm text-gray-500 mt-2">
              Multi-agent grading with consensus building and personalized
              feedback
            </p>
          </div>
        </footer>
      </body>
    </html>
  );
}
