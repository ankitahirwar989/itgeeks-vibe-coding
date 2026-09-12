import { FileText, Quote } from "lucide-react";
import type { EvidenceItem } from "@/types/api";

export function EvidenceCard({ item }: { item: EvidenceItem }) {
  return (
    <div className="rounded-md border border-border bg-muted/40 p-3">
      <div className="flex items-center gap-2 text-xs font-mono font-semibold text-muted-foreground">
        <FileText className="h-3.5 w-3.5" />
        {item.citation}
      </div>
      <div className="mt-2 flex gap-2 text-sm">
        <Quote className="mt-0.5 h-3.5 w-3.5 shrink-0 text-muted-foreground" />
        <span className="italic">&ldquo;{item.quote}&rdquo;</span>
      </div>
      {item.relevance ? (
        <p className="mt-2 text-xs text-muted-foreground">{item.relevance}</p>
      ) : null}
    </div>
  );
}
