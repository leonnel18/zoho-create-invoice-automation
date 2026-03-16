"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { auth as authApi } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", password: "", name: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  function set(field: string) {
    return (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await authApi.register(form.email, form.password, form.name || undefined);
      // Auto-login after register
      const resp = await authApi.login(form.email, form.password);
      localStorage.setItem("token", resp.access_token);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  const inputStyle: React.CSSProperties = {
    background: "var(--surface)",
    border: "1px solid var(--border)",
    borderRadius: 8,
    color: "var(--text)",
    padding: "0.625rem 0.875rem",
    width: "100%",
    fontSize: "0.9375rem",
    transition: "border-color 0.15s",
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "var(--bg)",
        padding: "1rem",
      }}
    >
      <div
        style={{
          position: "fixed",
          top: "20%",
          left: "50%",
          transform: "translateX(-50%)",
          width: 600,
          height: 400,
          background: "radial-gradient(ellipse, rgba(34,211,165,0.07) 0%, transparent 70%)",
          pointerEvents: "none",
        }}
      />

      <div className="animate-fade-up" style={{ width: "100%", maxWidth: 420 }}>
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <div
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: "0.5rem",
              marginBottom: "0.75rem",
            }}
          >
            <div
              style={{
                width: 36, height: 36, borderRadius: 10,
                background: "linear-gradient(135deg, var(--accent) 0%, #22d3a5 100%)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "1.1rem",
              }}
            >
              ⚡
            </div>
            <span
              style={{
                fontFamily: "var(--font-syne, Syne, sans-serif)",
                fontWeight: 700, fontSize: "1.125rem",
                color: "var(--text)", letterSpacing: "-0.02em",
              }}
            >
              ZohoFlow
            </span>
          </div>
          <h1
            style={{
              fontFamily: "var(--font-syne, Syne, sans-serif)",
              fontSize: "1.75rem", fontWeight: 800,
              color: "var(--text)", letterSpacing: "-0.03em",
            }}
          >
            Create account
          </h1>
          <p style={{ color: "var(--muted)", marginTop: "0.25rem", fontSize: "0.9rem" }}>
            Set up your invoice automation workspace
          </p>
        </div>

        <div className="card" style={{ borderColor: "var(--border-hi)" }}>
          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div>
              <label style={{ display: "block", fontSize: "0.8125rem", color: "var(--muted-hi)", marginBottom: "0.375rem", fontWeight: 500 }}>
                Display name <span style={{ color: "var(--muted)" }}>(optional)</span>
              </label>
              <input style={inputStyle} type="text" value={form.name} onChange={set("name")} placeholder="Your name" />
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.8125rem", color: "var(--muted-hi)", marginBottom: "0.375rem", fontWeight: 500 }}>
                Email
              </label>
              <input style={inputStyle} type="email" value={form.email} onChange={set("email")} placeholder="you@company.com" required />
            </div>
            <div>
              <label style={{ display: "block", fontSize: "0.8125rem", color: "var(--muted-hi)", marginBottom: "0.375rem", fontWeight: 500 }}>
                Password
              </label>
              <input style={inputStyle} type="password" value={form.password} onChange={set("password")} placeholder="Min 8 characters" required minLength={8} />
            </div>

            {error && (
              <div style={{ background: "rgba(248,113,113,0.1)", border: "1px solid rgba(248,113,113,0.3)", borderRadius: 8, padding: "0.625rem 0.875rem", color: "var(--red)", fontSize: "0.875rem" }}>
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              style={{
                marginTop: "0.5rem",
                padding: "0.75rem",
                background: loading ? "var(--border-hi)" : "var(--green)",
                color: loading ? "var(--muted)" : "#0c0e16",
                border: "none", borderRadius: 8,
                fontFamily: "var(--font-syne, Syne, sans-serif)",
                fontWeight: 700, fontSize: "0.9375rem",
                cursor: loading ? "not-allowed" : "pointer",
                transition: "background 0.15s",
                display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem",
              }}
            >
              {loading ? (
                <>
                  <span className="animate-spin" style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "white", borderRadius: "50%", display: "inline-block" }} />
                  Creating…
                </>
              ) : "Create account"}
            </button>
          </form>
        </div>

        <p style={{ textAlign: "center", marginTop: "1.25rem", color: "var(--muted)", fontSize: "0.875rem" }}>
          Already have an account?{" "}
          <Link href="/login" style={{ color: "var(--accent-hi)", textDecoration: "none", fontWeight: 500 }}>
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
