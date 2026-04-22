import Link from "next/link";
import { ReactNode } from "react";
import { NavLink } from "@/components/nav-link";

type SiteShellProps = {
  children: ReactNode;
};

const navItems = [
  { href: "/", label: "Overview" },
  { href: "/explore", label: "Explore" },
  { href: "/value-for-money", label: "Value" },
  { href: "/fairness", label: "Fairness" },
  { href: "/advanced", label: "Advanced" },
];

export function SiteShell({ children }: SiteShellProps) {
  return (
    <div className="shell-grid min-h-screen px-5 py-6 md:px-8">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col gap-6">
        <header className="surface rounded-[2rem] px-5 py-4 md:px-7">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex items-start justify-between gap-4">
              <div>
                <Link href="/" className="display-font text-2xl font-bold tracking-tight">
                  FIFA Player Data Analysis System
                </Link>
                <p className="mt-1 text-sm muted">
                  SDS-driven scaffold for FastAPI + Next.js delivery
                </p>
              </div>
              <span className="tag">Week 1 scaffold</span>
            </div>
            <nav className="flex flex-wrap gap-2">
              {navItems.map((item) => (
                <NavLink key={item.href} href={item.href} label={item.label} />
              ))}
            </nav>
          </div>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="px-1 pb-2 text-sm muted">
          Powered by the SDS, the April 22 meeting note, and the FIFA dataset archive.
        </footer>
      </div>
    </div>
  );
}

