"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { auth as authApi } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const resp = await authApi.login(email, password);
      localStorage.setItem("token", resp.access_token);
      router.push("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

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
      {/* Subtle background glow */}
      <div
        style={{
          position: "fixed",
          top: "20%",
          left: "50%",
          transform: "translateX(-50%)",
          width: 600,
          height: 400,
          background:
            "radial-gradient(ellipse, rgba(59,130,246,0.08) 0%, transparent 70%)",
          pointerEvents: "none",
        }}
      />

      <div className="animate-fade-up" style={{ width: "100%", maxWidth: 420 }}>
        {/* Logo mark */}
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
                width: 36,
                height: 36,
                borderRadius: 10,
                background:
                  "linear-gradient(135deg, var(--accent) 0%, #22d3a5 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "1.1rem",
              }}
            >
              ⚡
            </div>
            <span
              style={{
                fontFamily: "var(--font-syne, Syne, sans-serif)",
                fontWeight: 700,
                fontSize: "1.125rem",
                color: "var(--text)",
                letterSpacing: "-0.02em",
              }}
            >
              ZohoFlow
            </span>
          </div>
          <h1
            style={{
              fontFamily: "var(--font-syne, Syne, sans-serif)",
              fontSize: "1.75rem",
              fontWeight: 800,
              color: "var(--text)",
              letterSpacing: "-0.03em",
            }}
          >
            Welcome back
          </h1>
          <p style={{ color: "var(--muted)", marginTop: "0.25rem", fontSize: "0.9rem" }}>
            Sign in to your automation dashboard
          </p>
        </div>

        {/* Card */}
        <div className="card" style={{ borderColor: "var(--border-hi)" }}>
          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div>
              <label
                htmlFor="email"
                style={{ display: "block", fontSize: "0.8125rem", color: "var(--muted-hi)", marginBottom: "0.375rem", fontWeight: 500 }}
              >
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                required
                autoComplete="email"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                style={{ display: "block", fontSize: "0.8125rem", color: "var(--muted-hi)", marginBottom: "0.375rem", fontWeight: 500 }}
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                autoComplete="current-password"
              />
            </div>

            {error && (
              <div
                style={{
                  background: "rgba(248,113,113,0.1)",
                  border: "1px solid rgba(248,113,113,0.3)",
                  borderRadius: 8,
                  padding: "0.625rem 0.875rem",
                  color: "var(--red)",
                  fontSize: "0.875rem",
                }}
              >
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              style={{
                marginTop: "0.5rem",
                padding: "0.75rem",
                background: loading ? "var(--border-hi)" : "var(--accent)",
                color: "white",
                border: "none",
                borderRadius: 8,
                fontFamily: "var(--font-syne, Syne, sans-serif)",
                fontWeight: 700,
                fontSize: "0.9375rem",
                cursor: loading ? "not-allowed" : "pointer",
                transition: "background 0.15s, transform 0.1s",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "0.5rem",
              }}
            >
              {loading ? (
                <>
                  <span
                    className="animate-spin"
                    style={{
                      width: 16, height: 16,
                      border: "2px solid rgba(255,255,255,0.3)",
                      borderTopColor: "white",
                      borderRadius: "50%",
                      display: "inline-block",
                    }}
                  />
                  Signing in…
                </>
              ) : (
                "Sign in"
              )}
            </button>
          </form>
        </div>

        <p style={{ textAlign: "center", marginTop: "1.25rem", color: "var(--muted)", fontSize: "0.875rem" }}>
          Don&apos;t have an account?{" "}
          <Link
            href="/register"
            style={{ color: "var(--accent-hi)", textDecoration: "none", fontWeight: 500 }}
          >
            Register
          </Link>
        </p>
      </div>
    </div>
  );
}
