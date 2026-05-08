import Link from "next/link";
import { ReactNode } from "react";
import { NavLink } from "@/components/nav-link";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

type SiteShellProps = {
  children: ReactNode;
};

const navItems = [
  { href: "/", label: "Overview" },
  { href: "/explore", label: "Data Exploration" },
  { href: "/value-for-money", label: "Value Index" },
  { href: "/fairness", label: "Wage Fairness" },
  { href: "/advanced", label: "Clusters & Prediction" },
  { href: "/injury", label: "Injury & Solid" },
];

export function SiteShell({ children }: SiteShellProps) {
  return (
    <div className="shell-grid min-h-screen bg-background text-foreground">
      <div className="mx-auto grid min-h-screen w-full max-w-[1680px] lg:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="border-b border-border bg-background/95 px-4 py-4 lg:sticky lg:top-0 lg:h-screen lg:border-r lg:border-b-0 lg:px-5 lg:py-6">
          <div className="flex h-full flex-col gap-5">
            <div className="flex flex-col gap-3">
              <Link href="/" className="display-font text-xl font-bold leading-tight">
                FIFA Player Data Analysis
              </Link>
              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary">FIFA 15-22</Badge>
                <Badge variant="outline">144k snapshots</Badge>
              </div>
            </div>

            <Separator />

            <nav className="flex flex-col gap-2">
              {navItems.map((item) => (
                <NavLink key={item.href} href={item.href} label={item.label} />
              ))}
            </nav>

            <div className="mt-auto hidden flex-col gap-3 rounded-lg border border-border bg-muted p-4 text-sm lg:flex">
              <div>
                <p className="display-font text-xs font-semibold uppercase tracking-[0.18em] text-primary">
                  Focus
                </p>
                <p className="mt-2 leading-6 text-muted-foreground">
                  Exploration, value discovery, wage fairness, playing-style and future trait modelling.
                </p>
              </div>
            </div>
          </div>
        </aside>

        <main className="min-w-0 px-4 py-4 md:px-6 lg:px-8 lg:py-6">
          {children}
        </main>
      </div>
    </div>
  );
}
