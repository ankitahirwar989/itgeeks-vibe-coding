import { AlertTriangle, CheckCircle2, HelpCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { AnswerState } from "@/types/api";

const CONFIG: Record<AnswerState, { label: string; classes: string; Icon: typeof CheckCircle2 }> = {
  ANSWERABLE: {
    label: "ANSWERABLE",
    classes: "bg-emerald-100 text-emerald-800 border-emerald-300 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800",
    Icon: CheckCircle2,
  },
  UNKNOWN: {
    label: "UNKNOWN",
    classes: "bg-amber-100 text-amber-800 border-amber-300 dark:bg-amber-950 dark:text-amber-300 dark:border-amber-800",
    Icon: HelpCircle,
  },
  CONTRADICTION: {
    label: "CONTRADICTION DETECTED",
    classes: "bg-red-100 text-red-800 border-red-300 dark:bg-red-950 dark:text-red-300 dark:border-red-800",
    Icon: AlertTriangle,
  },
};

export function StateBadge({ state }: { state: AnswerState }) {
  const { label, classes, Icon } = CONFIG[state];
  return (
    <div className={cn("inline-flex items-center gap-2 rounded-lg border-2 px-4 py-2 text-sm font-bold tracking-wide", classes)}>
      <Icon className="h-5 w-5" />
      {label}
    </div>
  );
}
