import { useState, useEffect, useCallback } from "react";
import { analyzeTicket, listTickets, deleteTicket } from "./api";
import type { TicketInput, TicketAnalysisResponse, StoredTicket } from "./types";
import "./App.css";

const SEVERITY_CLASS: Record<string, string> = {
  low: "badge-low",
  medium: "badge-medium",
  high: "badge-high",
  critical: "badge-critical",
};

const EMPTY_FORM: TicketInput = {
  title: "",
  description: "",
  reported_by: "",
  environment: "",
  logs: "",
};

function App() {
  const [form, setForm] = useState<TicketInput>(EMPTY_FORM);
  const [result, setResult] = useState<TicketAnalysisResponse | null>(null);
  const [tickets, setTickets] = useState<StoredTicket[]>([]);
  const [selectedTicketId, setSelectedTicketId] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTickets = useCallback(async () => {
    try {
      setTickets(await listTickets());
    } catch {
      // silently ignore list errors on startup
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadTickets();
  }, [loadTickets]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await analyzeTicket(form);
      setResult(res);
      setSelectedTicketId(res.ticket_id);
      await loadTickets();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    await deleteTicket(id);
    if (result?.ticket_id === id) {
      setResult(null);
      setSelectedTicketId(null);
    }
    await loadTickets();
  };

  const handleSelectTicket = (ticket: StoredTicket) => {
    setSelectedTicketId(ticket.id);
    setError(null);
    setResult({
      ticket_id: ticket.id,
      analysis: ticket.analysis,
    });
  };

  return (
    <div className="layout">
      <header>
        <h1>Ticket Triage</h1>
        <p className="subtitle">Analyze support tickets with a local LLM</p>
      </header>

      <main>
        <section className="panel form-panel">
          <h2>New Ticket</h2>
          <form onSubmit={handleSubmit}>
            <label>
              Title *
              <input
                required
                minLength={3}
                value={form.title}
                onChange={(e) => setForm({ ...form, title: e.target.value })}
                placeholder="e.g. Checkout fails when coupon is used"
              />
            </label>
            <label>
              Description *
              <textarea
                required
                minLength={10}
                rows={4}
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="Describe what happens, when it started, and who is affected."
              />
            </label>
            <div className="row">
              <label>
                Reported by
                <input
                  value={form.reported_by}
                  onChange={(e) => setForm({ ...form, reported_by: e.target.value })}
                  placeholder="e.g. customer-support"
                />
              </label>
              <label>
                Environment
                <input
                  value={form.environment}
                  onChange={(e) => setForm({ ...form, environment: e.target.value })}
                  placeholder="e.g. production"
                />
              </label>
            </div>
            <label>
              Logs
              <textarea
                rows={3}
                value={form.logs}
                onChange={(e) => setForm({ ...form, logs: e.target.value })}
                placeholder="Paste relevant error logs here."
              />
            </label>
            <button type="submit" disabled={loading}>
              {loading ? "Analyzing..." : "Analyze Ticket"}
            </button>
          </form>
        </section>

        <section className="panel result-panel">
          <h2>Analysis Result</h2>
          {error && <div className="error-box">{error}</div>}
          {!result && !error && <p className="muted">Submit a ticket to see the analysis.</p>}
          {result && (
            <div className="result">
              <div className="result-header">
                <span className="ticket-id">#{result.ticket_id}</span>
                <span className={`badge ${SEVERITY_CLASS[result.analysis.severity]}`}>
                  {result.analysis.severity}
                </span>
                <span className="category">{result.analysis.category}</span>
                <span className="component">{result.analysis.component}</span>
              </div>
              <p className="summary">{result.analysis.summary}</p>
              <div className="confidence">
                <span>Confidence</span>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${result.analysis.confidence * 100}%` }} />
                </div>
                <span>{Math.round(result.analysis.confidence * 100)}%</span>
              </div>
              <h3>Suspected Root Cause</h3>
              <p>{result.analysis.suspected_root_cause}</p>
              <h3>Reproduction Steps</h3>
              <ol>{result.analysis.reproduction_steps.map((s, i) => <li key={i}>{s}</li>)}</ol>
              <h3>Recommended Actions</h3>
              <ul>{result.analysis.recommended_actions.map((a, i) => <li key={i}>{a}</li>)}</ul>
              <h3>Test Ideas</h3>
              <ul>{result.analysis.test_ideas.map((t, i) => <li key={i}>{t}</li>)}</ul>
            </div>
          )}
        </section>
      </main>

      <section className="panel history-panel">
        <h2>Ticket History ({tickets.length})</h2>
        {tickets.length === 0 && <p className="muted">No tickets stored yet.</p>}
        <div className="ticket-list">
          {tickets.map((t) => (
            <div
              key={t.id}
              className={`ticket-card ${selectedTicketId === t.id ? "ticket-card-active" : ""}`}
              onClick={() => handleSelectTicket(t)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  handleSelectTicket(t);
                }
              }}
              title="Show ticket analysis"
            >
              <div className="ticket-card-header">
                <span className="ticket-id">#{t.id}</span>
                <span className={`badge ${SEVERITY_CLASS[t.analysis.severity]}`}>{t.analysis.severity}</span>
                <span className="category">{t.analysis.category}</span>
                <span className="muted ticket-date">{t.created_at.slice(0, 16)}</span>
                <button
                  className="delete-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    void handleDelete(t.id);
                  }}
                  title="Delete"
                >
                  x
                </button>
              </div>
              <p className="ticket-title">{t.title}</p>
              <p className="muted">{t.analysis.summary}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default App;
