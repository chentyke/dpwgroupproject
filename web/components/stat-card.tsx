import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

type StatCardProps = {
  label: string;
  value: string;
  caption?: string;
};

export function StatCard({ label, value, caption }: StatCardProps) {
  return (
    <Card className="rounded-lg py-4">
      <CardHeader className="px-4">
        <CardTitle className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
          {label}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-2 px-4">
        <p className="display-font text-3xl font-bold leading-none">{value}</p>
        {caption ? (
          <p className="text-sm leading-5 text-muted-foreground">{caption}</p>
        ) : null}
      </CardContent>
    </Card>
  );
}
