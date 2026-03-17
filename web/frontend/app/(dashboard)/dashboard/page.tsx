"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { invoices as invoicesApi, watcher as watcherApi, pipeline as pipelineApi } from "@/lib/api";
import type { InvoiceStats, WatcherStatus, Job } from "@/lib/api";

// ── Payment details ───────────────────────────────────────────────────────────
const GCASH = { name: "Gideon Noel Valera", number: "09625408076" };
const BANK  = { bank: "Wise Pilipinas Inc.", name: "Gideon Noel Valera", account: "2005141027" };

// ── Matcha modal ──────────────────────────────────────────────────────────────
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
      <div style={{ position: "fixed", top: "50%", left: "50%", transform: "translate(-50%,-50%)", zIndex: 100, width: 340, background: "var(--card)", border: "1px solid var(--border)", borderRadius: 16, padding: "1.5rem", boxShadow: "0 24px 64px rgba(0,0,0,0.5)" }}>
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: "1.25rem" }}>
          <div>
            <div style={{ fontFamily: "var(--font-syne, Syne, sans-serif)", fontWeight: 800, fontSize: "1.1rem", color: "var(--green)", letterSpacing: "-0.02em" }}>🍵 Buy me a Matcha</div>
            <div style={{ fontSize: "0.8rem", color: "var(--muted)", marginTop: "0.25rem" }}>If ZohoFlow saved you time, I&apos;d love a matcha!</div>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "var(--muted)", fontSize: "1.125rem", cursor: "pointer", padding: "0 0.25rem", lineHeight: 1 }}>✕</button>
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

// ── Stat card ─────────────────────────────────────────────────────────────────
function StatCard({ label, value, color, sub }: { label: string; value: number | string; color: string; sub?: string }) {
  return (
    <div className="card animate-fade-up" style={{ borderTop: `2px solid ${color}`, width: "calc(25% - 0.75rem)", minWidth: 140, flexShrink: 0 }}>
      <div style={{ fontSize: "0.75rem", color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "0.5rem" }}>
        {label}
      </div>
      <div style={{ fontFamily: "var(--font-syne, Syne, sans-serif)", fontSize: "1.5rem", fontWeight: 700, color, letterSpacing: "-0.02em", lineHeight: 1 }}>
        {value}
      </div>
      {sub && <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "0.375rem" }}>{sub}</div>}
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────
export default function DashboardPage() {
  const [stats, setStats]           = useState<InvoiceStats | null>(null);
  const [watchStatus, setWatchStatus] = useState<WatcherStatus | null>(null);
  const [recentJobs, setRecentJobs] = useState<Job[]>([]);
  const [error, setError]           = useState("");
  const [showMatcha, setShowMatcha] = useState(false);

  useEffect(() => {
    Promise.all([
      invoicesApi.stats().catch(() => null),
      watcherApi.status().catch(() => null),
      pipelineApi.jobs().catch(() => []),
    ]).then(([s, w, j]) => {
      if (s) setStats(s);
      if (w) setWatchStatus(w);
      setRecentJobs((j as Job[]).slice(0, 5));
    }).catch((e) => setError(e.message));
  }, []);

  const statusDot = watchStatus?.enabled
    ? <span className="dot dot-green animate-pulse-dot" />
    : <span className="dot dot-grey" />;

  return (
    <div>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: "2rem" }}>
        <div>
          <h1 style={{ fontFamily: "var(--font-syne, Syne, sans-serif)", fontSize: "1.75rem", fontWeight: 800, color: "var(--text)", letterSpacing: "-0.03em" }}>
            Dashboard
          </h1>
          <p style={{ color: "var(--muted)", marginTop: "0.25rem" }}>
            Overview of your invoice automation pipeline
          </p>
        </div>
        {/* Matcha button */}
        <button
          onClick={() => setShowMatcha(true)}
          style={{
            padding: "0.5rem 1rem",
            background: "rgba(34,211,165,0.07)",
            border: "1px solid rgba(34,211,165,0.2)",
            borderRadius: 8, cursor: "pointer",
            display: "flex", alignItems: "center", gap: "0.5rem",
            color: "var(--green)", fontSize: "0.8125rem", fontWeight: 500,
            transition: "background 0.15s",
            flexShrink: 0,
          }}
        >
          🍵 Buy me a Matcha
        </button>
      </div>

      {showMatcha && <MatchaModal onClose={() => setShowMatcha(false)} />}

      {error && (
        <div style={{ background: "rgba(248,113,113,0.1)", border: "1px solid rgba(248,113,113,0.3)", borderRadius: 8, padding: "0.75rem 1rem", color: "var(--red)", marginBottom: "1.5rem", fontSize: "0.875rem" }}>
          {error}
        </div>
      )}

      {/* Stats row */}
      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
        <StatCard label="Total Invoices" value={stats?.total ?? "—"} color="var(--accent)" />
        <StatCard label="Pushed"         value={stats?.pushed ?? "—"} color="var(--green)" sub="to Zoho Books" />
        <StatCard label="Pending"        value={stats?.pending ?? "—"} color="var(--yellow)" />
        <StatCard label="Errors"         value={stats?.error ?? "—"} color="var(--red)" />
      </div>

      {/* 2-col grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>

        {/* Watcher status — desktop only */}
        <div className="card" style={{ opacity: 0.45, filter: "grayscale(1)", pointerEvents: "none" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.5rem" }}>
            <h2 style={{ fontFamily: "var(--font-syne, Syne, sans-serif)", fontWeight: 700, fontSize: "1rem" }}>Folder Watcher</h2>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.8125rem", color: "var(--muted)" }}>
              {statusDot}
              Inactive
            </div>
          </div>
          <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginBottom: "0.75rem" }}>
            Desktop only — not available in cloud mode
          </div>
          <div style={{ fontSize: "0.8125rem", color: "var(--muted)", lineHeight: 1.8 }}>
            <div>
              <span style={{ color: "var(--muted-hi)" }}>Folder: </span>
              <code style={{ fontFamily: "var(--font-mono)", fontSize: "0.75rem" }}>Not configured</code>
            </div>
            <div>
              <span style={{ color: "var(--muted-hi)" }}>Last event: </span>
              Never
            </div>
          </div>
        </div>

        {/* Quick actions */}
        <div className="card">
          <h2 style={{ fontFamily: "var(--font-syne, Syne, sans-serif)", fontWeight: 700, fontSize: "1rem", marginBottom: "1rem" }}>Quick Actions</h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.625rem" }}>
            <Link href="/pipeline" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.75rem 1rem", background: "rgba(59,130,246,0.1)", border: "1px solid rgba(59,130,246,0.25)", borderRadius: 8, textDecoration: "none", color: "var(--accent-hi)", fontSize: "0.875rem", fontWeight: 500 }}>
              <span>▶ Run Pipeline Now</span>
              <span style={{ opacity: 0.6, fontSize: "0.75rem" }}>manual</span>
            </Link>
            <Link href="/invoices" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.75rem 1rem", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, textDecoration: "none", color: "var(--text)", fontSize: "0.875rem" }}>
              <span>≡ View All Invoices</span>
              <span style={{ opacity: 0.6, fontSize: "0.75rem" }}>{stats?.total ?? 0} records</span>
            </Link>
          </div>
        </div>

        {/* Recent runs */}
        <div className="card" style={{ gridColumn: "1 / -1" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1rem" }}>
            <h2 style={{ fontFamily: "var(--font-syne, Syne, sans-serif)", fontWeight: 700, fontSize: "1rem" }}>Recent Pipeline Runs</h2>
            <Link href="/pipeline" style={{ fontSize: "0.8125rem", color: "var(--accent-hi)", textDecoration: "none" }}>View all →</Link>
          </div>
          {recentJobs.length === 0 ? (
            <div style={{ color: "var(--muted)", fontSize: "0.875rem", padding: "1rem 0" }}>
              No pipeline runs yet.{" "}
              <Link href="/pipeline" style={{ color: "var(--accent-hi)", textDecoration: "none" }}>Run it now →</Link>
            </div>
          ) : (
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.875rem" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--border)" }}>
                  {["ID", "Status", "Triggered by", "Pushed", "Errors", "Started"].map((h) => (
                    <th key={h} style={{ textAlign: "left", padding: "0.375rem 0.75rem", color: "var(--muted)", fontWeight: 500, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.06em" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {recentJobs.map((job) => (
                  <tr key={job.id} style={{ borderBottom: "1px solid var(--border)" }}>
                    <td style={{ padding: "0.625rem 0.75rem", fontFamily: "var(--font-mono)", fontSize: "0.8125rem", color: "var(--muted-hi)" }}>#{job.id}</td>
                    <td style={{ padding: "0.625rem 0.75rem" }}>
                      <span style={{ display: "inline-flex", alignItems: "center", gap: "0.375rem", padding: "0.125rem 0.625rem", borderRadius: 20, fontSize: "0.75rem", fontWeight: 600, background: job.status === "done" ? "rgba(34,211,165,0.12)" : job.status === "error" ? "rgba(248,113,113,0.12)" : "rgba(251,146,60,0.12)", color: job.status === "done" ? "var(--green)" : job.status === "error" ? "var(--red)" : "var(--orange)" }}>
                        <span className={`dot ${job.status === "done" ? "dot-green" : job.status === "error" ? "dot-red" : "dot-orange"}`} />
                        {job.status}
                      </span>
                    </td>
                    <td style={{ padding: "0.625rem 0.75rem", color: "var(--muted-hi)", fontSize: "0.8125rem" }}>{job.triggered_by}</td>
                    <td style={{ padding: "0.625rem 0.75rem", color: "var(--green)", fontFamily: "var(--font-mono)", fontSize: "0.8125rem" }}>{job.invoices_pushed}</td>
                    <td style={{ padding: "0.625rem 0.75rem", color: job.errors > 0 ? "var(--red)" : "var(--muted)", fontFamily: "var(--font-mono)", fontSize: "0.8125rem" }}>{job.errors}</td>
                    <td style={{ padding: "0.625rem 0.75rem", color: "var(--muted)", fontSize: "0.8125rem" }}>{new Date(job.started_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

      </div>

      {/* Branding */}
      <div style={{ textAlign: "center", marginTop: "2.5rem", paddingBottom: "1rem", fontSize: "0.75rem", color: "var(--muted)", letterSpacing: "0.05em" }}>
        created by{" "}
        <span style={{ color: "var(--muted-hi)", fontWeight: 500 }}>leonnel18</span>
      </div>
    </div>
  );
}
