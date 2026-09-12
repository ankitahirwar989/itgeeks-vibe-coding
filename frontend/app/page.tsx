import { Scale } from "lucide-react";
import { QueryForm } from "@/components/query-form";

export default function Home() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-10">
      <header className="mb-8 flex items-start gap-3">
        <Scale className="mt-1 h-8 w-8 shrink-0" />
        <div>
          <h1 className="text-2xl font-bold tracking-tight">The Rulebook That Argues With Itself</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            An evidence-first university regulation QA system that knows when the rulebook
            answers, stays silent, or contradicts itself.
          </p>
        </div>
      </header>
      <QueryForm />
    </main>
  );
}
