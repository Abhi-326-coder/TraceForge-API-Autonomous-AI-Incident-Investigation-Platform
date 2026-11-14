export type InvestigationEvent = {
  event_type: string;
  investigation_id: number;
  message: string;
  agent?: string | null;
  data: Record<string, unknown>;
  timestamp: string;
};

export type Evidence = {
  id: number;
  investigation_id: number;
  source_type: string;
  provider: string;
  title: string;
  content: string;
  source_reference?: string | null;
  created_at: string;
};

export type RootCause = {
  root_cause: string;
  explanation: string;
  confidence: number;
  evidence_ids: number[];
  alternative_causes: {
    cause: string;
    reason_not_primary: string;
  }[];
  uncertainty: string;
};
