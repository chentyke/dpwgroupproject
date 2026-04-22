"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

type NavLinkProps = {
  href: string;
  label: string;
};

export function NavLink({ href, label }: NavLinkProps) {
  const pathname = usePathname();
  const active = pathname === href;

  return (
    <Link
      href={href}
      className={[
        "rounded-full px-4 py-2 text-sm transition",
        active
          ? "bg-[var(--accent)] text-white shadow-lg shadow-emerald-950/10"
          : "bg-white/40 text-[var(--ink)] hover:bg-white/70",
      ].join(" ")}
    >
      {label}
    </Link>
  );
}

