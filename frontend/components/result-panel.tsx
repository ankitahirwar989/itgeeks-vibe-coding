import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StateBadge } from "@/components/state-badge";
import { EvidenceCard } from "@/components/evidence-card";
import { ContradictionView } from "@/components/contradiction-view";
import { RetrievedContext } from "@/components/retrieved-context";
import type { QueryResponse } from "@/types/api";

export function ResultPanel({ result }: { result: QueryResponse }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <CardTitle>Result</CardTitle>
          <StateBadge state={result.state} />
        </div>
      </CardHeader>
      <CardContent className="space-y-5">
        <div>
          <p className="text-xs font-semibold uppercase text-muted-foreground">Question</p>
          <p className="text-sm">{result.question}</p>
        </div>

        <div>
          <p className="text-xs font-semibold uppercase text-muted-foreground">Answer</p>
          <p className="text-sm leading-relaxed">{result.answer}</p>
        </div>

        {result.state === "CONTRADICTION" && result.contradictions.length > 0 && (
          <div className="space-y-3">
            <p className="text-xs font-semibold uppercase text-muted-foreground">
              Conflicting passages
            </p>
            {result.contradictions.map((pair, i) => (
              <ContradictionView key={i} pair={pair} index={i} />
            ))}
          </div>
        )}

        {result.state === "ANSWERABLE" && result.evidence.length > 0 && (
          <div className="space-y-2">
            <p className="text-xs font-semibold uppercase text-muted-foreground">Evidence</p>
            {result.evidence.map((item, i) => (
              <EvidenceCard key={i} item={item} />
            ))}
          </div>
        )}

        {result.reasoning_notes && (
          <div>
            <p className="text-xs font-semibold uppercase text-muted-foreground">Reasoning notes</p>
            <p className="text-xs text-muted-foreground">{result.reasoning_notes}</p>
          </div>
        )}

        <RetrievedContext items={result.retrieved} />
      </CardContent>
    </Card>
  );
}
