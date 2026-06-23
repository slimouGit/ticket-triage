import type { TicketAnalysisResponse, TicketInput, StoredTicket } from "./types";

const BASE = "http://127.0.0.1:8000";

export async function analyzeTicket(ticket: TicketInput): Promise<TicketAnalysisResponse> {
  const res = await fetch(`${BASE}/tickets/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(ticket),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Unknown error");
  }
  return res.json();
}

export async function listTickets(): Promise<StoredTicket[]> {
  const res = await fetch(`${BASE}/tickets`);
  if (!res.ok) throw new Error("Failed to load tickets");
  return res.json();
}

export async function deleteTicket(id: number): Promise<void> {
  const res = await fetch(`${BASE}/tickets/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete ticket");
}
