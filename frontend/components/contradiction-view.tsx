import { Scale } from "lucide-react";
import type { ContradictionPair } from "@/types/api";
import { EvidenceCard } from "@/components/evidence-card";

export function ContradictionView({ pair, index }: { pair: ContradictionPair; index: number }) {
  return (
    <div className="rounded-lg border-2 border-red-300 bg-red-50/50 p-4 dark:border-red-900 dark:bg-red-950/20">
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-red-800 dark:text-red-300">
        <Scale className="h-4 w-4" />
        Conflicting pair #{index + 1}
      </div>
      <div className="grid gap-3 sm:grid-cols-2">
        <div>
          <p className="mb-1 text-xs font-semibold uppercase text-muted-foreground">Passage A</p>
          <EvidenceCard item={pair.claim_a} />
        </div>
        <div>
          <p className="mb-1 text-xs font-semibold uppercase text-muted-foreground">Passage B</p>
          <EvidenceCard item={pair.claim_b} />
        </div>
      </div>
      <p className="mt-3 text-sm text-red-900 dark:text-red-200">
        <span className="font-semibold">Why this is a contradiction: </span>
        {pair.explanation}
      </p>
    </div>
  );
}
