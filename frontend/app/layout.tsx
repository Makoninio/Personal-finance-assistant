import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import HealthBadge from "@/components/HealthBadge";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Finance Assistant",
  description: "Personal finance assistant — frontend vertical slice",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="flex h-full min-h-screen bg-slate-50 font-sans text-slate-900">
        <Sidebar />
        <div className="flex flex-1 flex-col min-w-0">
          <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
            <h1 className="text-base font-semibold text-slate-800">
              Personal Finance Assistant
            </h1>
            <HealthBadge />
          </header>
          <main className="flex-1 min-w-0 overflow-y-auto p-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
