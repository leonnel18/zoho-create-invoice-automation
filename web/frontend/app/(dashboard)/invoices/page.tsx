"use client";

import { useEffect, useState } from "react";
import { invoices as invoicesApi } from "@/lib/api";
import type { Invoice, InvoiceStats } from "@/lib/api";

const STATUS_STYLE: Record<string, { bg: string; color: string; dot: string }> = {
  pushed:  { bg: "rgba(34,211,165,0.12)",  color: "var(--green)",  dot: "dot-green"  },
  pending: { bg: "rgba(251,191,36,0.12)",  color: "var(--yellow)", dot: "dot-orange" },
  error:   { bg: "rgba(248,113,113,0.12)", color: "var(--red)",    dot: "dot-red"    },
};

const GCASH = { name: "Gideon Noel Valera", number: "09625408076" };
const BANK  = { bank: "Wise Pilipinas Inc.", name: "Gideon Noel Valera", account: "2005141027" };

function MatchaModal({ onClose }: { onClose: () => void }) {
  const [copied, setCopied] = useState<string | null>(null);
  function copy(text: string, key: string) {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(key);
      setTimeout(() => setCopied(null), 2000);
    });
  }
  const Row = ({ label, value, k }: { label: string; value: string; k: string }) => (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.5rem 0", borderBottom: "1px solid var(--border)" }}>
      <div>
        <div style={{ fontSize: "0.6875rem", color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.07em" }}>{label}</div>
        <div style={{ fontFamily: "var(--font-mono)", fontSize: "0.8125rem", color: "var(--text)", marginTop: "0.125rem" }}>{value}</div>
      </div>
      <button onClick={() => copy(value, k)} style={{ padding: "0.25rem 0.625rem", background: copied === k ? "rgba(34,211,165,0.15)" : "var(--surface)", border: "1px solid var(--border)", borderRadius: 6, color: copied === k ? "var(--green)" : "var(--muted)", fontSize: "0.75rem", cursor: "pointer", transition: "all 0.15s", flexShrink: 0, marginLeft: "0.75rem" }}>
        {copied === k ? "✓ Copied" : "Copy"}
      </button>
    </div>
  );
  return (
    <>
      <div onClick={onClose} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.55)", zIndex: 99, backdropFilter: "blur(2px)" }} />
      <div style={{ position: "fixed", top: "50%", left: "50%", transform: "translate(-50%,-50%)", zIndex: 100, width: 380, maxWidth: "calc(100vw - 2rem)", background: "var(--card)", border: "1px solid var(--border)", borderRadius: 16, padding: "1.5rem", boxShadow: "0 24px 64px rgba(0,0,0,0.5)" }}>
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: "1.25rem" }}>
          <div>
            <div style={{ fontFamily: "var(--font-syne, Syne, sans-serif)", fontWeight: 800, fontSize: "1.1rem", color: "var(--green)", letterSpacing: "-0.02em" }}>🍵 Buy me a Matcha</div>
            <div style={{ fontSize: "0.8rem", color: "var(--muted)", marginTop: "0.25rem" }}>If ZohoFlow saved you time, I&apos;d love a matcha!</div>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "var(--muted)", fontSize: "1.125rem", cursor: "pointer", minWidth: 44, minHeight: 44, display: "flex", alignItems: "center", justifyContent: "center" }}>✕</button>
        </div>
        <div style={{ marginBottom: "1rem" }}>
          <div style={{ fontSize: "0.7rem", color: "var(--green)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "0.5rem" }}>GCash</div>
          <Row label="Account Name" value={GCASH.name}   k="gcash-name" />
          <Row label="Number"       value={GCASH.number} k="gcash-num" />
        </div>
        <div>
          <div style={{ fontSize: "0.7rem", color: "var(--accent-hi)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "0.5rem" }}>Bank Transfer</div>
          <Row label="Bank"           value={BANK.bank}    k="bank-name" />
          <Row label="Account Name"   value={BANK.name}    k="bank-acct-name" />
          <Row label="Account Number" value={BANK.account} k="bank-acct-num" />
        </div>
      </div>
    </>
  );
}

// ── Invoice detail: slide-up sheet on mobile, right panel on tablet+ ──────────
function InvoiceDetailPanel({ invoice, onClose }: { invoice: Invoice; onClose: () => void }) {
  const s = STATUS_STYLE[invoice.status] ?? STATUS_STYLE.pending;
  return (
    <>
      <div className="invoice-detail-backdrop" onClick={onClose} />
      <div className="invoice-detail-panel">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.25rem" }}>
          <h2 style={{ fontFamily: "var(--font-syne, Syne, sans-serif)", fontWeight: 700, fontSize: "1rem", color: "var(--text)" }}>
            Invoice #{invoice.id}
          </h2>
          <button
            onClick={onClose}
            aria-label="Close detail"
            style={{ background: "none", border: "none", color: "var(--muted)", fontSize: "1.125rem", cursor: "pointer", minWidth: 44, minHeight: 44, display: "flex", alignItems: "center", justifyContent: "center", borderRadius: 8 }}
          >
            ✕
          </button>
        </div>

        {[
          { label: "Customer",     value: invoice.customer_name },
          { label: "Date",         value: invoice.invoice_date },
          { label: "Zoho ID",      value: invoice.zoho_invoice_id ?? "—" },
          { label: "Processed At", value: invoice.processed_at ? new Date(invoice.processed_at).toLocaleString() : "—" },
          { label: "Error",        value: invoice.error_message ?? "—" },
        ].map(({ label, value }) => (
          <div key={label} style={{ padding: "0.625rem 0", borderBottom: "1px solid var(--border)" }}>
            <div style={{ fontSize: "0.6875rem", color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: "0.25rem" }}>{label}</div>
            <div style={{ fontSize: "0.875rem", color: "var(--text)", fontFamily: label === "Zoho ID" ? "var(--font-mono)" : undefined }}>{value}</div>
          </div>
        ))}

        <div style={{ padding: "0.625rem 0", borderBottom: "1px solid var(--border)" }}>
          <div style={{ fontSize: "0.6875rem", color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: "0.375rem" }}>Status</div>
          <span style={{ display: "inline-flex", alignItems: "center", gap: "0.375rem", padding: "0.125rem 0.625rem", borderRadius: 20, fontSize: "0.75rem", fontWeight: 600, background: s.bg, color: s.color }}>
            <span className={`dot ${s.dot}`} style={{ width: 6, height: 6 }} />
            {invoice.status}
          </span>
        </div>

        {invoice.pdf_output_path && (
          <div style={{ marginTop: "1rem" }}>
            <button
              onClick={() => invoicesApi.downloadPdf(invoice.id, `${invoice.customer_name}_${invoice.invoice_date}.pdf`).catch((e) => alert(e.message))}
              style={{ display: "inline-flex", alignItems: "center", gap: "0.375rem", padding: "0.625rem 1.25rem", borderRadius: 8, background: "rgba(59,130,246,0.1)", border: "1px solid rgba(59,130,246,0.25)", color: "var(--accent-hi)", fontSize: "0.875rem", fontWeight: 600, cursor: "pointer", minHeight: 44 }}
            >
              ↓ Download PDF
            </button>
          </div>
        )}
      </div>
    </>
  );
}

export default function InvoicesPage() {
  const [items, setItems] = useState<Invoice[]>([]);
  const [stats, setStats] = useState<InvoiceStats | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "pending" | "pushed" | "error">("all");
  const [showMatcha, setShowMatcha] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null);
  const pageSize = 20;

  async function load(p: number) {
    setLoading(true);
    try {
      const [res, s] = await Promise.all([
        invoicesApi.list(p, pageSize),
        invoicesApi.stats(),
      ]);
      setItems(res.items);
      setTotal(res.total);
      setStats(s);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(page); }, [page]); // eslint-disable-line react-hooks/exhaustive-deps

  const filtered = filter === "all" ? items : items.filter((i) => i.status === filter);
  const totalPages = Math.ceil(total / pageSize);

  return (
    <div>
      {showMatcha && <MatchaModal onClose={() => setShowMatcha(false)} />}

      {/* Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: "1.5rem" }}>
        <div>
          <h1 style={{ fontFamily: "var(--font-syne, Syne, sans-serif)", fontSize: "1.75rem", fontWeight: 800, color: "var(--text)", letterSpacing: "-0.03em" }}>
            Invoices
          </h1>
          <p style={{ color: "var(--muted)", marginTop: "0.25rem" }}>
            All invoice records from the pipeline
          </p>
        </div>
        <button
          onClick={() => setShowMatcha(true)}
          style={{ padding: "0.5rem 1rem", background: "rgba(34,211,165,0.07)", border: "1px solid rgba(34,211,165,0.2)", borderRadius: 8, color: "var(--green)", fontSize: "0.8125rem", fontWeight: 600, cursor: "pointer", flexShrink: 0, whiteSpace: "nowrap", minHeight: 44 }}
        >
          🍵 Buy me a Matcha
        </button>
      </div>

      {/* Stats pills */}
      {stats && (
        <div style={{ display: "flex", gap: "0.625rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
          {(["all", "pushed", "pending", "error"] as const).map((s) => {
            const count = s === "all" ? stats.total : stats[s];
            const active = filter === s;
            const st = s !== "all" ? STATUS_STYLE[s] : null;
            return (
              <button
                key={s}
                onClick={() => setFilter(s)}
                style={{ padding: "0.375rem 0.875rem", borderRadius: 20, border: active ? "1px solid var(--accent)" : "1px solid var(--border)", background: active ? "rgba(59,130,246,0.12)" : "var(--card)", color: active ? "var(--accent-hi)" : "var(--muted-hi)", fontSize: "0.8125rem", fontWeight: active ? 600 : 400, cursor: "pointer", transition: "all 0.15s", display: "flex", alignItems: "center", gap: "0.375rem", minHeight: 44 }}
              >
                {st && <span className={`dot ${st.dot}`} style={{ width: 6, height: 6 }} />}
                {s.charAt(0).toUpperCase() + s.slice(1)}
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.75rem" }}>{count}</span>
              </button>
            );
          })}
        </div>
      )}

      {/* Split layout: list + detail */}
      <div className={`invoices-split${selectedInvoice ? " has-selection" : ""}`}>

        {/* List panel */}
        <div className="invoices-list-panel">
          <div className="card" style={{ padding: 0, overflow: "hidden" }}>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
                <thead>
                  <tr style={{ borderBottom: "1px solid var(--border)", background: "var(--surface)" }}>
                    <th style={{ textAlign: "left", padding: "0.75rem 1rem", color: "var(--muted)", fontWeight: 500, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.06em", whiteSpace: "nowrap" }}>#</th>
                    <th className="col-date" style={{ textAlign: "left", padding: "0.75rem 1rem", color: "var(--muted)", fontWeight: 500, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.06em", whiteSpace: "nowrap" }}>Date</th>
                    <th style={{ textAlign: "left", padding: "0.75rem 1rem", color: "var(--muted)", fontWeight: 500, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.06em", whiteSpace: "nowrap" }}>Customer</th>
                    <th style={{ textAlign: "left", padding: "0.75rem 1rem", color: "var(--muted)", fontWeight: 500, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.06em", whiteSpace: "nowrap" }}>Status</th>
                    <th className="col-zoho-id" style={{ textAlign: "left", padding: "0.75rem 1rem", color: "var(--muted)", fontWeight: 500, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.06em", whiteSpace: "nowrap" }}>Zoho ID</th>
                    <th className="col-processed-at" style={{ textAlign: "left", padding: "0.75rem 1rem", color: "var(--muted)", fontWeight: 500, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.06em", whiteSpace: "nowrap" }}>Processed At</th>
                    <th className="col-error" style={{ textAlign: "left", padding: "0.75rem 1rem", color: "var(--muted)", fontWeight: 500, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.06em", whiteSpace: "nowrap" }}>Error</th>
                    <th style={{ textAlign: "left", padding: "0.75rem 1rem", color: "var(--muted)", fontWeight: 500, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.06em", whiteSpace: "nowrap" }}>PDF</th>
                  </tr>
                </thead>
                <tbody>
                  {loading ? (
                    <tr>
                      <td colSpan={8} style={{ textAlign: "center", padding: "3rem", color: "var(--muted)" }}>
                        <span className="animate-spin" style={{ display: "inline-block", width: 24, height: 24, border: "3px solid var(--border-hi)", borderTopColor: "var(--accent)", borderRadius: "50%" }} />
                      </td>
                    </tr>
                  ) : filtered.length === 0 ? (
                    <tr>
                      <td colSpan={8} style={{ textAlign: "center", padding: "3rem", color: "var(--muted)", fontSize: "0.875rem" }}>
                        No invoices found
                      </td>
                    </tr>
                  ) : (
                    filtered.map((inv) => {
                      const s = STATUS_STYLE[inv.status] ?? STATUS_STYLE.pending;
                      const isSelected = selectedInvoice?.id === inv.id;
                      return (
                        <tr
                          key={inv.id}
                          onClick={() => setSelectedInvoice(isSelected ? null : inv)}
                          style={{ borderBottom: "1px solid var(--border)", cursor: "pointer", transition: "background 0.1s", background: isSelected ? "rgba(59,130,246,0.07)" : "transparent" }}
                          onMouseOver={(e) => { if (!isSelected) (e.currentTarget as HTMLTableRowElement).style.background = "var(--surface)"; }}
                          onMouseOut={(e) => { if (!isSelected) (e.currentTarget as HTMLTableRowElement).style.background = "transparent"; }}
                        >
                          <td style={{ padding: "0.75rem 1rem", fontFamily: "var(--font-mono)", fontSize: "0.75rem", color: "var(--muted)" }}>{inv.id}</td>
                          <td className="col-date" style={{ padding: "0.75rem 1rem", color: "var(--muted-hi)", whiteSpace: "nowrap" }}>{inv.invoice_date}</td>
                          <td style={{ padding: "0.75rem 1rem", color: "var(--text)", maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{inv.customer_name}</td>
                          <td style={{ padding: "0.75rem 1rem" }}>
                            <span style={{ display: "inline-flex", alignItems: "center", gap: "0.375rem", padding: "0.125rem 0.625rem", borderRadius: 20, fontSize: "0.75rem", fontWeight: 600, background: s.bg, color: s.color }}>
                              <span className={`dot ${s.dot}`} style={{ width: 6, height: 6 }} />
                              {inv.status}
                            </span>
                          </td>
                          <td className="col-zoho-id" style={{ padding: "0.75rem 1rem", fontFamily: "var(--font-mono)", fontSize: "0.75rem", color: "var(--accent-hi)" }}>
                            {inv.zoho_invoice_id ?? <span style={{ color: "var(--muted)" }}>—</span>}
                          </td>
                          <td className="col-processed-at" style={{ padding: "0.75rem 1rem", color: "var(--muted)", whiteSpace: "nowrap", fontSize: "0.8125rem" }}>
                            {inv.processed_at ? new Date(inv.processed_at).toLocaleString() : "—"}
                          </td>
                          <td className="col-error" style={{ padding: "0.75rem 1rem", color: "var(--red)", fontSize: "0.75rem", maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                            {inv.error_message ?? ""}
                          </td>
                          <td style={{ padding: "0.75rem 1rem" }} onClick={(e) => e.stopPropagation()}>
                            {inv.pdf_output_path ? (
                              <button
                                onClick={() => invoicesApi.downloadPdf(inv.id, `${inv.customer_name}_${inv.invoice_date}.pdf`).catch((e) => alert(e.message))}
                                style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem", padding: "0.25rem 0.625rem", borderRadius: 6, background: "rgba(59,130,246,0.1)", border: "1px solid rgba(59,130,246,0.25)", color: "var(--accent-hi)", fontSize: "0.75rem", fontWeight: 600, cursor: "pointer", whiteSpace: "nowrap", minHeight: 44 }}
                              >
                                ↓ PDF
                              </button>
                            ) : (
                              <span style={{ color: "var(--muted)", fontSize: "0.75rem" }}>—</span>
                            )}
                          </td>
                        </tr>
                      );
                    })
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.75rem 1rem", borderTop: "1px solid var(--border)", fontSize: "0.8125rem", color: "var(--muted)" }}>
                <span>{(page - 1) * pageSize + 1}–{Math.min(page * pageSize, total)} of {total}</span>
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <button disabled={page === 1} onClick={() => setPage((p) => p - 1)} style={{ padding: "0.375rem 0.75rem", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 6, color: page === 1 ? "var(--muted)" : "var(--text)", cursor: page === 1 ? "not-allowed" : "pointer", fontSize: "0.8125rem", minHeight: 44 }}>← Prev</button>
                  <button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)} style={{ padding: "0.375rem 0.75rem", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 6, color: page >= totalPages ? "var(--muted)" : "var(--text)", cursor: page >= totalPages ? "not-allowed" : "pointer", fontSize: "0.8125rem", minHeight: 44 }}>Next →</button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Detail panel (right side on tablet+, slide-up sheet on mobile) */}
        {selectedInvoice && (
          <InvoiceDetailPanel
            invoice={selectedInvoice}
            onClose={() => setSelectedInvoice(null)}
          />
        )}
      </div>
    </div>
  );
}
