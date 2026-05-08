"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ActivityIcon,
  BadgeEuroIcon,
  BarChart3Icon,
  HeartPulseIcon,
  NetworkIcon,
  ScaleIcon,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type NavLinkProps = {
  href: string;
  label: string;
};

const icons = {
  "/": BarChart3Icon,
  "/explore": ActivityIcon,
  "/value-for-money": BadgeEuroIcon,
  "/fairness": ScaleIcon,
  "/advanced": NetworkIcon,
  "/injury": HeartPulseIcon,
};

export function NavLink({ href, label }: NavLinkProps) {
  const pathname = usePathname();
  const active = pathname === href;
  const Icon = icons[href as keyof typeof icons] ?? BarChart3Icon;

  return (
    <Button
      asChild
      variant={active ? "default" : "ghost"}
      className={cn("w-full justify-start", active ? "" : "text-foreground")}
    >
      <Link href={href} aria-current={active ? "page" : undefined}>
        <Icon data-icon="inline-start" />
        {label}
      </Link>
    </Button>
  );
}
