import type { Metadata } from "next";
import Link from "next/link";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const navItems = [
  { href: "/", label: "Mission Control" },
  { href: "/expeditions", label: "Expeditions" },
  { href: "/cargo", label: "Cargo" },
  { href: "/inventory", label: "Inventory" },
  { href: "/assets", label: "Assets" },
  { href: "/personnel", label: "Personnel" },
  { href: "/transport", label: "Transport" },
  { href: "/missions", label: "Missions" },
  { href: "/intelligence", label: "AI Center" },
  { href: "/risk-center", label: "Risk Center" },
  { href: "/emergency-center", label: "Emergency Center" },
  { href: "/demo", label: "Judge Demo" },
  { href: "/demo-mode", label: "Demo Mode" },
];

export const metadata: Metadata = {
  title: "POLARIS Phase 4",
  description: "Mission-control platform for polar expedition logistics, asset, inventory, and risk intelligence.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-slate-950 text-slate-50">
        <nav className="border-b border-slate-800 bg-slate-950/95 sticky top-0 z-20 backdrop-blur">
          <div className="mx-auto flex max-w-7xl flex-wrap items-center gap-2 px-4 py-3">
            <div className="mr-4 text-xs font-bold uppercase tracking-[0.3em] text-cyan-400">POLARIS</div>
            {navItems.map((item) => (
              <Link key={item.href} href={item.href} className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-200 transition hover:border-cyan-500 hover:text-cyan-300">
                {item.label}
              </Link>
            ))}
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
