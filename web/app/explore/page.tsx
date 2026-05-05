import { DataTable } from "@/components/data-table";
import { PageHeader } from "@/components/page-header";
import { StatCard } from "@/components/stat-card";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { fetchApi } from "@/lib/api";
import { fallbackCleaningReport, fallbackSummary } from "@/lib/fallback-data";
import { formatCompactNumber } from "@/lib/format";

function displayCleaningDetail(detail: string) {
  if (
    detail.includes("pyarrow") ||
    detail.includes("fastparquet") ||
    detail.includes("optional dependency")
  ) {
    return "Tidy cache export is not complete yet; the cleaned in-memory dataset remains available for the analysis views.";
  }

  return detail;
}

export default async function ExplorePage() {
  const [summary, report] = await Promise.all([
    fetchApi("/api/dataset/summary", fallbackSummary),
    fetchApi(
      "/api/dataset/cleaning-report",
      fallbackCleaningReport,
    ),
  ]);

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        eyebrow="Usage Scenario 1"
        title="Data loading and cleaning"
        description="Inspect the unified FIFA archive, verify schema coverage, and track the cleaning rules that prepare the player snapshot table for downstream analysis."
        aside={`Source: ${summary.source}. Preview rows are sampled from the current player snapshot view.`}
      />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Rows" value={formatCompactNumber(summary.total_rows)} />
        <StatCard label="Columns" value={String(summary.total_columns)} />
        <StatCard
          label="Seasons"
          value={summary.seasons.length ? summary.seasons.join(", ") : "0"}
        />
        <StatCard
          label="Position fields"
          value={String(report.position_columns.length)}
          caption={report.tidy_cache_path ? "Tidy player snapshot cache" : "No cache path reported"}
        />
      </section>

      <section className="grid gap-5 xl:grid-cols-[minmax(0,1.25fr)_minmax(340px,0.75fr)]">
        <Card className="rounded-lg">
          <CardHeader>
            <CardTitle>Archive inspection</CardTitle>
            <CardDescription>Preview rows and column profile</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="preview" className="flex flex-col gap-4">
              <TabsList className="w-fit">
                <TabsTrigger value="preview">Preview</TabsTrigger>
                <TabsTrigger value="columns">Columns</TabsTrigger>
              </TabsList>
              <TabsContent value="preview" className="mt-0">
                <DataTable
                  columns={Object.keys(summary.preview[0] ?? {}).map((key) => ({
                    key,
                    label: key,
                    render: (row: Record<string, unknown>) =>
                      String(row[key] ?? "null"),
                  }))}
                  rows={summary.preview}
                />
              </TabsContent>
              <TabsContent value="columns" className="mt-0">
                <DataTable
                  columns={[
                    { key: "name", label: "Column", render: (row) => row.name },
                    { key: "dtype", label: "Type", render: (row) => row.dtype },
                    {
                      key: "null",
                      label: "Null count",
                      render: (row) => formatCompactNumber(row.null_count),
                    },
                  ]}
                  rows={summary.columns.slice(0, 12)}
                />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <div className="grid gap-5">
          <Card className="rounded-lg">
            <CardHeader>
              <CardTitle>Cleaning checklist</CardTitle>
              <CardDescription>Data preparation status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-3">
                {report.steps.map((step) => (
                  <article key={step.title} className="rounded-lg border border-border p-4">
                    <div className="flex items-center justify-between gap-3">
                      <p className="font-semibold">{step.title}</p>
                      <Badge variant="secondary">{step.status}</Badge>
                    </div>
                    <p className="mt-2 text-sm leading-6 text-muted-foreground">
                      {displayCleaningDetail(step.detail)}
                    </p>
                  </article>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card className="rounded-lg">
            <CardHeader>
              <CardTitle>Null hotspots</CardTitle>
              <CardDescription>Columns requiring special handling</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-4">
                {report.null_hotspots.map((item) => (
                  <article key={item.column} className="flex flex-col gap-2">
                    <div className="flex items-center justify-between gap-3">
                      <p className="font-medium">{item.column}</p>
                      <Badge variant="outline">{Math.round(item.null_rate * 100)}%</Badge>
                    </div>
                    <Progress value={Math.round(item.null_rate * 100)} />
                    <p className="text-sm leading-6 text-muted-foreground">{item.note}</p>
                  </article>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}
