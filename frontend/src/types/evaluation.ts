export interface EvaluationCase {
  case_id: string;
  passed: boolean;
  root_cause_match: boolean;
  evidence_grounded: boolean;
  required_evidence_covered: boolean;
  forbidden_claim_detected: boolean;
  failures: string[];
}

export interface EvaluationDashboard {
  mode: string;
  total_cases: number;
  passed_cases: number;
  failed_cases: number;
  pass_rate: number;
  root_cause_accuracy: number;
  evidence_grounding_rate: number;
  average_duration_ms: number;
  average_tool_calls: number;
  cases: EvaluationCase[];
}