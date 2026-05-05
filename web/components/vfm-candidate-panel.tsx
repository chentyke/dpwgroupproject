"use client";

import { useState } from "react";
import { DataTable } from "@/components/data-table";
import { RadarChart } from "@/components/radar-chart";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { formatCurrency } from "@/lib/format";
import type { RadarMetric, VfmCandidate } from "@/lib/types";

type VfmCandidatePanelProps = {
  benchmarkMetrics: RadarMetric[];
  benchmarkName: string;
  candidates: VfmCandidate[];
  position: string;
};

export function VfmCandidatePanel({
  benchmarkMetrics,
  benchmarkName,
  candidates,
  position,
}: VfmCandidatePanelProps) {
  const [selectedCandidateIndex, setSelectedCandidateIndex] = useState<
    number | null
  >(null);
  const selectedCandidate =
    selectedCandidateIndex == null
      ? null
      : candidates[selectedCandidateIndex] ?? null;
  const radarLabel = selectedCandidate?.short_name ?? benchmarkName;
  const radarMetrics = selectedCandidate?.metrics ?? benchmarkMetrics;

  return (
    <section className="grid gap-5 xl:grid-cols-[minmax(0,1.15fr)_minmax(360px,0.85fr)]">
      <Card className="rounded-lg">
        <CardHeader>
          <CardTitle>Top candidates for {position}</CardTitle>
          <CardDescription>Sorted by value-for-money index</CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable
            columns={[
              {
                key: "player",
                label: "Player",
                render: (row) => (
                  <div>
                    <p className="font-semibold">{row.short_name}</p>
                    <p className="text-xs text-muted-foreground">{row.club_name}</p>
                  </div>
                ),
              },
              {
                key: "positions",
                label: "Pos",
                render: (row) => row.player_positions,
              },
              { key: "overall", label: "Overall", render: (row) => row.overall },
              {
                key: "value",
                label: "Value",
                render: (row) => formatCurrency(row.value_eur),
              },
              {
                key: "vfm",
                label: "VfM",
                render: (row) => (
                  <Badge variant="secondary">{row.vfm_index.toFixed(3)}</Badge>
                ),
              },
            ]}
            getRowKey={(_, index) => index}
            onRowClick={(_, index) =>
              setSelectedCandidateIndex((current) =>
                current === index ? null : index,
              )
            }
            rowAriaLabel={(row) => `Show ${row.short_name} radar`}
            rows={candidates}
            selectedRowKey={selectedCandidateIndex}
          />
        </CardContent>
      </Card>

      <RadarChart metrics={radarMetrics} label={radarLabel} />
    </section>
  );
}
