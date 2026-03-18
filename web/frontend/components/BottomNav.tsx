"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const GCASH = { name: "Gideon Noel Valera", number: "09625408076" };
const BANK  = { bank: "Wise Pilipinas Inc.", name: "Gideon Noel Valera", account: "2005141027" };

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: "▦" },
  { href: "/pipeline",  label: "Pipeline",  icon: "▶" },
  { href: "/invoices",  label: "Invoices",  icon: "≡" },
  { href: "/settings",  label: "Settings",  icon: "⚙" },
];

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
        <div style={{ fontSize: "0.7rem", color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.07em" }}>{label}</div>
        <div style={{ fontFamily: "var(--font-mono)", fontSize: "0.8125rem", color: "var(--text)", marginTop: "0.125rem" }}>{value}</div>
      </div>
      <button onClick={() => copy(value, k)} style={{ padding: "0.25rem 0.625rem", background: copied === k ? "rgba(34,211,165,0.15)" : "var(--surface)", border: "1px solid var(--border)", borderRadius: 6, color: copied === k ? "var(--green)" : "var(--muted)", fontSize: "0.75rem", cursor: "pointer", flexShrink: 0, marginLeft: "0.75rem" }}>
        {copied === k ? "✓ Copied" : "Copy"}
      </button>
    </div>
  );
  return (
    <>
      <div onClick={onClose} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)", zIndex: 99, backdropFilter: "blur(2px)" }} />
      <div style={{ position: "fixed", top: "50%", left: "50%", transform: "translate(-50%,-50%)", zIndex: 100, width: 340, maxWidth: "calc(100vw - 2rem)", background: "var(--card)", border: "1px solid var(--border)", borderRadius: 16, padding: "1.5rem", boxShadow: "0 24px 64px rgba(0,0,0,0.5)" }}>
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

interface Props {
  onLogout: () => void;
}

export default function BottomNav({ onLogout }: Props) {
  const path = usePathname();
  const [showOverflow, setShowOverflow] = useState(false);
  const [showMatcha, setShowMatcha] = useState(false);

  return (
    <>
      <nav className="bottom-nav" aria-label="Mobile navigation">
        {NAV.map((item) => {
          const active = path === item.href || path.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`bottom-nav-tab${active ? " active" : ""}`}
              aria-current={active ? "page" : undefined}
            >
              <span className="bottom-nav-icon">{item.icon}</span>
              <span className="bottom-nav-label">{item.label}</span>
            </Link>
          );
        })}
        <button
          className="bottom-nav-tab"
          onClick={() => setShowOverflow((o) => !o)}
          aria-label="More options"
        >
          <span className="bottom-nav-icon">⋯</span>
          <span className="bottom-nav-label">More</span>
        </button>
      </nav>

      {/* Overflow sheet */}
      {showOverflow && (
        <>
          <div
            onClick={() => setShowOverflow(false)}
            style={{ position: "fixed", inset: 0, zIndex: 55, background: "rgba(0,0,0,0.5)" }}
          />
          <div
            style={{
              position: "fixed",
              bottom: "calc(var(--bottom-nav-h, 56px) + var(--sab, 0px))",
              left: 0, right: 0,
              zIndex: 56,
              background: "var(--surface)",
              borderTop: "1px solid var(--border)",
              borderRadius: "16px 16px 0 0",
              padding: "1rem",
              display: "flex",
              flexDirection: "column",
              gap: "0.625rem",
            }}
          >
            <button
              onClick={() => { setShowOverflow(false); setShowMatcha(true); }}
              style={{
                width: "100%", padding: "0.75rem 1rem",
                background: "rgba(34,211,165,0.07)",
                border: "1px solid rgba(34,211,165,0.2)",
                borderRadius: 8, cursor: "pointer",
                display: "flex", alignItems: "center", gap: "0.625rem",
                color: "var(--green)", fontSize: "0.9rem", fontWeight: 500,
                minHeight: 44,
              }}
            >
              🍵 Buy me a Matcha
            </button>
            <button
              onClick={() => { setShowOverflow(false); onLogout(); }}
              style={{
                width: "100%", padding: "0.75rem 1rem",
                background: "transparent",
                border: "1px solid var(--border)",
                borderRadius: 8, cursor: "pointer",
                color: "var(--muted)", fontSize: "0.9rem",
                minHeight: 44,
              }}
            >
              Sign out
            </button>
          </div>
        </>
      )}

      {showMatcha && <MatchaModal onClose={() => setShowMatcha(false)} />}
    </>
  );
}
