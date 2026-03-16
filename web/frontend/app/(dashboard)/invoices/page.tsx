"use client";

import { useEffect, useState } from "react";
import { invoices as invoicesApi } from "@/lib/api";
import type { Invoice, InvoiceStats } from "@/lib/api";

const STATUS_STYLE: Record<string, { bg: string; color: string; dot: string }> = {
  pushed:  { bg: "rgba(34,211,165,0.12)",  color: "var(--green)",  dot: "dot-green"  },
  pending: { bg: "rgba(251,191,36,0.12)",  color: "var(--yellow)", dot: "dot-orange" },
  error:   { bg: "rgba(248,113,113,0.12)", color: "var(--red)",    dot: "dot-red"    },
};

export default function InvoicesPage() {
  const [items, setItems] = useState<Invoice[]>([]);
  const [stats, setStats] = useState<InvoiceStats | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "pending" | "pushed" | "error">("all");
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
      {/* Header */}
      <div style={{ marginBottom: "1.5rem" }}>
        <h1 style={{ fontFamily: "var(--font-syne, Syne, sans-serif)", fontSize: "1.75rem", fontWeight: 800, color: "var(--text)", letterSpacing: "-0.03em" }}>
          Invoices
        </h1>
        <p style={{ color: "var(--muted)", marginTop: "0.25rem" }}>
          All invoice records from the pipeline
        </p>
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
                style={{
                  padding: "0.375rem 0.875rem",
                  borderRadius: 20,
                  border: active ? "1px solid var(--accent)" : "1px solid var(--border)",
                  background: active ? "rgba(59,130,246,0.12)" : "var(--card)",
                  color: active ? "var(--accent-hi)" : "var(--muted-hi)",
                  fontSize: "0.8125rem", fontWeight: active ? 600 : 400,
                  cursor: "pointer", transition: "all 0.15s",
                  display: "flex", alignItems: "center", gap: "0.375rem",
                }}
              >
                {st && <span className={`dot ${st.dot}`} style={{ width: 6, height: 6 }} />}
                {s.charAt(0).toUpperCase() + s.slice(1)}
                <span style={{ fontFamily: "var(--font-mono)", fontSize: "0.75rem" }}>
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      )}

      {/* Table */}
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border)", background: "var(--surface)" }}>
                {["#", "Date", "Customer", "Status", "Zoho ID", "Processed At", "Error"].map((h) => (
                  <th
                    key={h}
                    style={{
                      textAlign: "left", padding: "0.75rem 1rem",
                      color: "var(--muted)", fontWeight: 500,
                      fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.06em",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: "center", padding: "3rem", color: "var(--muted)" }}>
                    <span className="animate-spin" style={{ display: "inline-block", width: 24, height: 24, border: "3px solid var(--border-hi)", borderTopColor: "var(--accent)", borderRadius: "50%" }} />
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: "center", padding: "3rem", color: "var(--muted)", fontSize: "0.875rem" }}>
                    No invoices found
                  </td>
                </tr>
              ) : (
                filtered.map((inv) => {
                  const s = STATUS_STYLE[inv.status] ?? STATUS_STYLE.pending;
                  return (
                    <tr
                      key={inv.id}
                      style={{ borderBottom: "1px solid var(--border)", transition: "background 0.1s" }}
                      onMouseOver={(e) => (e.currentTarget.style.background = "var(--surface)")}
                      onMouseOut={(e) => (e.currentTarget.style.background = "transparent")}
                    >
                      <td style={{ padding: "0.75rem 1rem", fontFamily: "var(--font-mono)", fontSize: "0.75rem", color: "var(--muted)" }}>
                        {inv.id}
                      </td>
                      <td style={{ padding: "0.75rem 1rem", color: "var(--muted-hi)", whiteSpace: "nowrap" }}>
                        {inv.invoice_date}
                      </td>
                      <td style={{ padding: "0.75rem 1rem", color: "var(--text)", maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {inv.customer_name}
                      </td>
                      <td style={{ padding: "0.75rem 1rem" }}>
                        <span style={{ display: "inline-flex", alignItems: "center", gap: "0.375rem", padding: "0.125rem 0.625rem", borderRadius: 20, fontSize: "0.75rem", fontWeight: 600, background: s.bg, color: s.color }}>
                          <span className={`dot ${s.dot}`} style={{ width: 6, height: 6 }} />
                          {inv.status}
                        </span>
                      </td>
                      <td style={{ padding: "0.75rem 1rem", fontFamily: "var(--font-mono)", fontSize: "0.75rem", color: "var(--accent-hi)" }}>
                        {inv.zoho_invoice_id ?? <span style={{ color: "var(--muted)" }}>—</span>}
                      </td>
                      <td style={{ padding: "0.75rem 1rem", color: "var(--muted)", whiteSpace: "nowrap", fontSize: "0.8125rem" }}>
                        {inv.processed_at ? new Date(inv.processed_at).toLocaleString() : "—"}
                      </td>
                      <td style={{ padding: "0.75rem 1rem", color: "var(--red)", fontSize: "0.75rem", maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {inv.error_message ?? ""}
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
          <div
            style={{
              display: "flex", alignItems: "center", justifyContent: "space-between",
              padding: "0.75rem 1rem",
              borderTop: "1px solid var(--border)",
              fontSize: "0.8125rem", color: "var(--muted)",
            }}
          >
            <span>
              {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, total)} of {total}
            </span>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <button
                disabled={page === 1}
                onClick={() => setPage((p) => p - 1)}
                style={{ padding: "0.375rem 0.75rem", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 6, color: page === 1 ? "var(--muted)" : "var(--text)", cursor: page === 1 ? "not-allowed" : "pointer", fontSize: "0.8125rem" }}
              >
                ← Prev
              </button>
              <button
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
                style={{ padding: "0.375rem 0.75rem", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 6, color: page >= totalPages ? "var(--muted)" : "var(--text)", cursor: page >= totalPages ? "not-allowed" : "pointer", fontSize: "0.8125rem" }}
              >
                Next →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
