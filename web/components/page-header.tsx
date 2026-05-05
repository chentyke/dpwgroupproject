import { Badge } from "@/components/ui/badge";

type PageHeaderProps = {
  eyebrow: string;
  title: string;
  description: string;
  aside?: string;
};

export function PageHeader({
  eyebrow,
  title,
  description,
  aside,
}: PageHeaderProps) {
  return (
    <section className="border-b border-border pb-5">
      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.3fr)_minmax(280px,0.7fr)] xl:items-end">
        <div className="flex flex-col gap-3">
          <Badge className="w-fit border border-primary/20 bg-primary/10 text-primary hover:bg-primary/10">
            {eyebrow}
          </Badge>
          <h1 className="max-w-5xl text-3xl font-semibold tracking-tight md:text-4xl">
            {title}
          </h1>
          <p className="max-w-4xl text-base leading-7 text-muted-foreground">
            {description}
          </p>
        </div>
        {aside ? (
          <div className="rounded-lg border border-border bg-muted p-4 text-sm leading-6 text-foreground">
            {aside}
          </div>
        ) : null}
      </div>
    </section>
  );
}
