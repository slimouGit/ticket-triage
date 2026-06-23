export interface TicketInput {
  title: string;
  description: string;
  reported_by?: string;
  environment?: string;
  logs?: string;
}

export interface TriageAnalysis {
  category: string;
  severity: "low" | "medium" | "high" | "critical";
  component: string;
  summary: string;
  reproduction_steps: string[];
  suspected_root_cause: string;
  recommended_actions: string[];
  test_ideas: string[];
  confidence: number;
}

export interface TicketAnalysisResponse {
  ticket_id: number;
  analysis: TriageAnalysis;
}

export interface StoredTicket {
  id: number;
  title: string;
  description: string;
  reported_by: string | null;
  environment: string | null;
  logs: string | null;
  analysis: TriageAnalysis;
  created_at: string;
}
