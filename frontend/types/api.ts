export type AnswerState = "ANSWERABLE" | "UNKNOWN" | "CONTRADICTION";

export interface EvidenceItem {
  citation: string;
  quote: string;
  relevance?: string;
}

export interface ContradictionPair {
  claim_a: EvidenceItem;
  claim_b: EvidenceItem;
  explanation: string;
}

export interface Citation {
  citation: string;
  source_file: string;
  section_id: string;
  heading: string;
  page: number | null;
  text: string;
}

export interface QueryResponse {
  question: string;
  state: AnswerState;
  answer: string;
  evidence: EvidenceItem[];
  contradictions: ContradictionPair[];
  citations: string[];
  retrieved: Citation[];
  reasoning_notes: string;
}
