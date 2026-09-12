"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Search } from "lucide-react";
import type { Citation } from "@/types/api";

export function RetrievedContext({ items }: { items: Citation[] }) {
  const [open, setOpen] = useState(false);

  if (items.length === 0) return null;

  return (
    <div className="rounded-md border border-border">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-4 py-3 text-sm font-medium"
      >
        <span className="flex items-center gap-2">
          <Search className="h-4 w-4" />
          Retrieved context ({items.length} passages considered)
        </span>
        {open ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
      </button>
      {open && (
        <div className="space-y-2 border-t border-border p-4">
          {items.map((c) => (
            <div key={c.citation} className="rounded-md bg-muted/40 p-3 text-sm">
              <div className="font-mono text-xs font-semibold text-muted-foreground">
                {c.citation}
                {c.page ? ` (page ${c.page})` : ""}
              </div>
              <p className="mt-1 line-clamp-3 text-muted-foreground">{c.text}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
