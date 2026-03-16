"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const MATCHA_GCASH  = { name: "Gideon Noel Valera", number: "09625408076" };
const MATCHA_BANK   = { bank: "Wise Pilipinas Inc.", name: "Gideon Noel Valera", account: "2005141027" };

function MatchaModal({ onClose }: { onClose: () => void }) {
  const [copied, setCopied] = useState<string | null>(null);
  function copy(text: string, key: string) {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(key);
      setTimeout(() => setCopied(null), 2000);
    });
  }
  const Row = ({ label, value, copyKey }: { label: string; value: string; copyKey: string }) => (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0.5rem 0", borderBottom: "1px solid var(--border)" }}>
      <div>
        <div style={{ fontSize: "0.7rem", color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.07em" }}>{label}</div>
        <div style={{ fontFamily: "var(--font-mono)", fontSize: "0.8125rem", color: "var(--text)", marginTop: "0.125rem" }}>{value}</div>
      </div>
      <button
        onClick={() => copy(value, copyKey)}
        style={{ padding: "0.25rem 0.625rem", background: copied === copyKey ? "rgba(34,211,165,0.15)" : "var(--surface)", border: "1px solid var(--border)", borderRadius: 6, color: copied === copyKey ? "var(--green)" : "var(--muted)", fontSize: "0.75rem", cursor: "pointer", transition: "all 0.15s", flexShrink: 0, marginLeft: "0.75rem" }}
      >
        {copied === copyKey ? "✓ Copied" : "Copy"}
      </button>
    </div>
  );
  return (
    <>
      {/* Backdrop */}
      <div onClick={onClose} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)", zIndex: 99, backdropFilter: "blur(2px)" }} />
      {/* Dialog */}
      <div style={{ position: "fixed", top: "50%", left: "50%", transform: "translate(-50%,-50%)", zIndex: 100, width: 340, background: "var(--card)", border: "1px solid var(--border)", borderRadius: 16, padding: "1.5rem", boxShadow: "0 24px 64px rgba(0,0,0,0.5)" }}>
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: "1.25rem" }}>
          <div>
            <div style={{ fontFamily: "var(--font-syne, Syne, sans-serif)", fontWeight: 800, fontSize: "1.1rem", color: "var(--green)", letterSpacing: "-0.02em" }}>
              🍵 Buy me a Matcha
            </div>
            <div style={{ fontSize: "0.8rem", color: "var(--muted)", marginTop: "0.25rem" }}>
              If ZohoFlow saved you time, I'd love a matcha!
            </div>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "var(--muted)", fontSize: "1.125rem", cursor: "pointer", padding: "0 0.25rem", lineHeight: 1 }}>✕</button>
        </div>

        {/* GCash */}
        <div style={{ marginBottom: "1rem" }}>
          <div style={{ fontSize: "0.7rem", color: "var(--green)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "0.5rem" }}>GCash</div>
          <Row label="Account Name" value={MATCHA_GCASH.name} copyKey="gcash-name" />
          <Row label="Number" value={MATCHA_GCASH.number} copyKey="gcash-number" />
        </div>

        {/* Bank */}
        <div>
          <div style={{ fontSize: "0.7rem", color: "var(--accent-hi)", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "0.5rem" }}>Bank Transfer</div>
          <Row label="Bank" value={MATCHA_BANK.bank} copyKey="bank-name" />
          <Row label="Account Name" value={MATCHA_BANK.name} copyKey="bank-acct-name" />
          <Row label="Account Number" value={MATCHA_BANK.account} copyKey="bank-acct-num" />
        </div>
      </div>
    </>
  );
}

interface NavItem {
  href: string;
  label: string;
  icon: string;
}

const NAV: NavItem[] = [
  { href: "/dashboard", label: "Dashboard",  icon: "▦" },
  { href: "/pipeline",  label: "Pipeline",   icon: "▶" },
  { href: "/invoices",  label: "Invoices",   icon: "≡" },
  { href: "/settings",  label: "Settings",   icon: "⚙" },
];

interface Props {
  userEmail?: string;
  displayName?: string;
  onLogout: () => void;
}

export default function Sidebar({ userEmail, displayName, onLogout }: Props) {
  const path = usePathname();
  const [showMatcha, setShowMatcha] = useState(false);

  return (
    <aside
      style={{
        width: 220,
        minHeight: "100vh",
        background: "var(--surface)",
        borderRight: "1px solid var(--border)",
        display: "flex",
        flexDirection: "column",
        padding: "1.25rem 0",
        position: "fixed",
        top: 0,
        left: 0,
        zIndex: 50,
      }}
    >
      {/* Logo */}
      <div
        style={{
          padding: "0 1.25rem",
          marginBottom: "2rem",
          display: "flex",
          alignItems: "center",
          gap: "0.625rem",
        }}
      >
        <div
          style={{
            width: 32, height: 32, borderRadius: 8,
            background: "linear-gradient(135deg, var(--accent) 0%, var(--green) 100%)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: "1rem", flexShrink: 0,
          }}
        >
          ⚡
        </div>
        <span
          style={{
            fontFamily: "var(--font-syne, Syne, sans-serif)",
            fontWeight: 800, fontSize: "1rem",
            color: "var(--text)", letterSpacing: "-0.02em",
          }}
        >
          ZohoFlow
        </span>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: "0 0.75rem" }}>
        {NAV.map((item) => {
          const active = path === item.href || path.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.75rem",
                padding: "0.625rem 0.75rem",
                borderRadius: 8,
                marginBottom: "0.25rem",
                textDecoration: "none",
                fontWeight: active ? 600 : 400,
                fontSize: "0.9rem",
                color: active ? "var(--text)" : "var(--muted-hi)",
                background: active ? "var(--card)" : "transparent",
                transition: "background 0.15s, color 0.15s",
                borderLeft: active
                  ? "2px solid var(--accent)"
                  : "2px solid transparent",
              }}
            >
              <span style={{ fontSize: "0.85rem", opacity: active ? 1 : 0.7, width: 18, textAlign: "center" }}>
                {item.icon}
              </span>
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Matcha button */}
      <div style={{ padding: "0 0.75rem", marginBottom: "0.5rem" }}>
        <button
          onClick={() => setShowMatcha(true)}
          style={{
            width: "100%", padding: "0.5rem 0.75rem",
            background: "rgba(34,211,165,0.07)",
            border: "1px solid rgba(34,211,165,0.2)",
            borderRadius: 8, cursor: "pointer",
            display: "flex", alignItems: "center", gap: "0.5rem",
            color: "var(--green)", fontSize: "0.8125rem", fontWeight: 500,
            transition: "background 0.15s, border-color 0.15s",
          }}
          onMouseOver={(e) => { (e.currentTarget as HTMLButtonElement).style.background = "rgba(34,211,165,0.13)"; (e.currentTarget as HTMLButtonElement).style.borderColor = "rgba(34,211,165,0.4)"; }}
          onMouseOut={(e) => { (e.currentTarget as HTMLButtonElement).style.background = "rgba(34,211,165,0.07)"; (e.currentTarget as HTMLButtonElement).style.borderColor = "rgba(34,211,165,0.2)"; }}
        >
          🍵 Buy me a Matcha
        </button>
      </div>

      {showMatcha && <MatchaModal onClose={() => setShowMatcha(false)} />}

      {/* User footer */}
      <div
        style={{
          padding: "0.75rem",
          borderTop: "1px solid var(--border)",
          margin: "0 0.75rem",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.625rem",
            padding: "0.5rem 0.75rem",
            borderRadius: 8,
            marginBottom: "0.5rem",
          }}
        >
          <div
            style={{
              width: 28, height: 28, borderRadius: "50%",
              background: "linear-gradient(135deg, var(--accent), var(--green))",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "0.75rem", fontWeight: 700, color: "#0c0e16", flexShrink: 0,
            }}
          >
            {(displayName ?? userEmail ?? "?")[0].toUpperCase()}
          </div>
          <div style={{ overflow: "hidden" }}>
            <div
              style={{
                fontSize: "0.8125rem", fontWeight: 600,
                color: "var(--text)", whiteSpace: "nowrap",
                overflow: "hidden", textOverflow: "ellipsis",
              }}
            >
              {displayName ?? "User"}
            </div>
            <div
              style={{
                fontSize: "0.6875rem", color: "var(--muted)",
                whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
              }}
            >
              {userEmail}
            </div>
          </div>
        </div>
        <button
          onClick={onLogout}
          style={{
            width: "100%", padding: "0.5rem",
            background: "transparent",
            border: "1px solid var(--border)",
            borderRadius: 8,
            color: "var(--muted)", fontSize: "0.8125rem",
            cursor: "pointer", transition: "border-color 0.15s, color 0.15s",
          }}
          onMouseOver={(e) => {
            (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--red)";
            (e.currentTarget as HTMLButtonElement).style.color = "var(--red)";
          }}
          onMouseOut={(e) => {
            (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--border)";
            (e.currentTarget as HTMLButtonElement).style.color = "var(--muted)";
          }}
        >
          Sign out
        </button>
      </div>
    </aside>
  );
}
