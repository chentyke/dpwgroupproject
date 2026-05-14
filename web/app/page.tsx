import Link from "next/link";
import { PageHeader } from "@/components/page-header";
import { StatCard } from "@/components/stat-card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { fetchApi } from "@/lib/api";
import { fallbackSummary } from "@/lib/fallback-data";
import { formatCompactNumber } from "@/lib/format";

const routes = [
  {
    href: "/explore",
    label: "Data Loading and Exploration",
    detail: "Shape, schema preview, cleaning steps, null hotspots.",
  },
  {
    href: "/value-for-money",
    label: "Player Value-for-Money",
    detail: "VfM ranking, candidate radar, value scatter.",
  },
  {
    href: "/fairness",
    label: "Salary Fairness",
    detail: "League wage distribution and nationality pay heatmap.",
  },
  {
    href: "/injury",
    label: "Injury & Solid Projection",
    detail: "Future trait risk, feature importance, validation timelines.",
  },
  {
    href: "/advanced",
    label: "Advanced Analysis",
    detail: "Playing-style clusters and value prediction report.",
  },
];

export default async function HomePage() {
  const summary = await fetchApi("/api/dataset/summary", fallbackSummary);

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="FIFA Analysis"
        title="Player value, wage fairness, and playing-style intelligence"
        description="Interactive dashboards for the five analysis scenarios defined in the project document: exploration and cleaning, value-for-money ranking, salary fairness testing, future trait projection, and advanced clustering with value prediction."
        aside={`Current sample: ${formatCompactNumber(summary.total_rows)} snapshots, ${summary.total_columns} fields, ${summary.seasons.length} FIFA editions.`}
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Snapshots"
          value={formatCompactNumber(summary.total_rows)}
          caption="Player-season records available for analysis"
        />
        <StatCard
          label="Attributes"
          value={String(summary.total_columns)}
          caption="Ratings, wages, identities, positions"
        />
        <StatCard
          label="Editions"
          value={summary.seasons.length ? summary.seasons.join(", ") : "0"}
          caption="FIFA editions represented in the dataset"
        />
        <StatCard
          label="Genders"
          value={summary.genders.length ? summary.genders.join(", ") : "0"}
          caption="Dataset coverage for player groups"
        />
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
        {routes.map((route, index) => (
          <Card key={route.href} className="rounded-lg">
            <CardHeader>
              <CardTitle>{route.label}</CardTitle>
              <CardDescription>{route.detail}</CardDescription>
              <CardAction>
                <Badge variant="outline">Scenario {index + 1}</Badge>
              </CardAction>
            </CardHeader>
            <CardContent>
              <Button asChild className="w-full">
                <Link href={route.href}>Open analysis</Link>
              </Button>
            </CardContent>
          </Card>
        ))}
      </section>
    </div>
  );
}
