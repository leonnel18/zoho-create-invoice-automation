"use client";

import { useEffect, useState } from "react";
import { settings as settingsApi, watcher as watcherApi } from "@/lib/api";
import type { Settings, WatcherStatus } from "@/lib/api";

function Field({
  label,
  value,
  onChange,
  type = "text",
  placeholder,
  hint,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  placeholder?: string;
  hint?: string;
}) {
  return (
    <div>
      <label
        style={{
          display: "block", fontSize: "0.8125rem",
          color: "var(--muted-hi)", marginBottom: "0.375rem", fontWeight: 500,
        }}
      >
        {label}
      </label>
      <input type={type} value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder} />
      {hint && <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "0.25rem" }}>{hint}</div>}
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="card" style={{ marginBottom: "1rem" }}>
      <h2
        style={{
          fontFamily: "var(--font-syne, Syne, sans-serif)", fontWeight: 700,
          fontSize: "1rem", color: "var(--text)", marginBottom: "1.25rem",
          paddingBottom: "0.75rem", borderBottom: "1px solid var(--border)",
        }}
      >
        {title}
      </h2>
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {children}
      </div>
    </div>
  );
}

export default function SettingsPage() {
  const [form, setForm] = useState<Partial<Settings>>({});
  const [watchStatus, setWatchStatus] = useState<WatcherStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [saved, setSaved] = useState(false);
  const [verifyResult, setVerifyResult] = useState<{ ok: boolean; message: string } | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([settingsApi.get(), watcherApi.status()])
      .then(([s, w]) => {
        setForm(s);
        setWatchStatus(w);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  function set(field: keyof Settings) {
    return (value: string | boolean) =>
      setForm((f) => ({ ...f, [field]: value }));
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError("");
    setSaved(false);
    try {
      await settingsApi.update(form);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function handleVerify() {
    setVerifying(true);
    setVerifyResult(null);
    try {
      const result = await settingsApi.verify();
      setVerifyResult(result);
    } catch (e: unknown) {
      setVerifyResult({ ok: false, message: e instanceof Error ? e.message : "Verification failed" });
    } finally {
      setVerifying(false);
    }
  }

  async function toggleWatcher() {
    try {
      const result = watchStatus?.enabled
        ? await watcherApi.disable()
        : await watcherApi.enable();
      setWatchStatus(result);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Toggle failed");
    }
  }

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: 300 }}>
        <span className="animate-spin" style={{ width: 28, height: 28, border: "3px solid var(--border-hi)", borderTopColor: "var(--accent)", borderRadius: "50%", display: "inline-block" }} />
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 680 }}>
      <div style={{ marginBottom: "2rem" }}>
        <h1 style={{ fontFamily: "var(--font-syne, Syne, sans-serif)", fontSize: "1.75rem", fontWeight: 800, color: "var(--text)", letterSpacing: "-0.03em" }}>
          Settings
        </h1>
        <p style={{ color: "var(--muted)", marginTop: "0.25rem" }}>Configure your Zoho credentials and pipeline paths</p>
      </div>

      {error && (
        <div style={{ background: "rgba(248,113,113,0.1)", border: "1px solid rgba(248,113,113,0.3)", borderRadius: 8, padding: "0.75rem 1rem", color: "var(--red)", marginBottom: "1.5rem", fontSize: "0.875rem" }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSave}>
        <Section title="Zoho Credentials">
          <Field
            label="Client ID"
            value={form.zoho_client_id ?? ""}
            onChange={set("zoho_client_id")}
            placeholder="1000.XXXXXXXXXXXXXXXX"
          />
          <Field
            label="Client Secret"
            value={form.zoho_client_secret ?? ""}
            onChange={set("zoho_client_secret")}
            type="password"
            placeholder="Encrypted on save"
            hint="Leave blank to keep existing value"
          />
          <Field
            label="Refresh Token"
            value={form.zoho_refresh_token ?? ""}
            onChange={set("zoho_refresh_token")}
            type="password"
            placeholder="Encrypted on save"
            hint="Leave blank to keep existing value"
          />
          <div className="settings-inner-grid" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            <Field
              label="Organization ID"
              value={form.zoho_org_id ?? ""}
              onChange={set("zoho_org_id")}
              placeholder="123456789"
            />
            <div>
              <label style={{ display: "block", fontSize: "0.8125rem", color: "var(--muted-hi)", marginBottom: "0.375rem", fontWeight: 500 }}>
                Region
              </label>
              <select
                value={form.zoho_region ?? "com"}
                onChange={(e) => set("zoho_region")(e.target.value)}
              >
                <option value="com">com (US)</option>
                <option value="eu">eu (Europe)</option>
                <option value="in">in (India)</option>
                <option value="com.au">com.au (Australia)</option>
                <option value="jp">jp (Japan)</option>
              </select>
            </div>
          </div>

          {/* Verify button */}
          <div>
            <button
              type="button"
              onClick={handleVerify}
              disabled={verifying}
              style={{
                padding: "0.5rem 1.25rem",
                background: "transparent",
                border: "1px solid var(--border-hi)",
                borderRadius: 8,
                color: "var(--muted-hi)", fontSize: "0.875rem",
                cursor: verifying ? "not-allowed" : "pointer",
                display: "flex", alignItems: "center", gap: "0.5rem",
                transition: "border-color 0.15s, color 0.15s",
              }}
            >
              {verifying ? (
                <>
                  <span className="animate-spin" style={{ width: 14, height: 14, border: "2px solid rgba(255,255,255,0.2)", borderTopColor: "var(--accent)", borderRadius: "50%", display: "inline-block" }} />
                  Verifying…
                </>
              ) : "✓ Test credentials"}
            </button>
            {verifyResult && (
              <div
                style={{
                  marginTop: "0.5rem",
                  padding: "0.5rem 0.875rem",
                  borderRadius: 8, fontSize: "0.8125rem",
                  background: verifyResult.ok ? "rgba(34,211,165,0.1)" : "rgba(248,113,113,0.1)",
                  border: `1px solid ${verifyResult.ok ? "rgba(34,211,165,0.3)" : "rgba(248,113,113,0.3)"}`,
                  color: verifyResult.ok ? "var(--green)" : "var(--red)",
                }}
              >
                {verifyResult.ok ? "✓ " : "✗ "}{verifyResult.message}
              </div>
            )}
          </div>
        </Section>

        <Section title="Folder Paths (Desktop only)">
          <div style={{ padding: "0.5rem 0.75rem", borderRadius: 8, background: "rgba(59,130,246,0.08)", border: "1px solid rgba(59,130,246,0.2)", fontSize: "0.8125rem", color: "var(--accent)", marginBottom: "0.25rem" }}>
            These paths apply when running the backend locally. In cloud mode, upload PDFs directly on the Pipeline page.
          </div>
          <Field
            label="Input Folder (PDF watch folder)"
            value={form.input_folder ?? ""}
            onChange={set("input_folder")}
            placeholder="C:/path/to/delivery-receipts/"
          />
          <Field
            label="Output Folder (generated invoices)"
            value={form.output_folder ?? ""}
            onChange={set("output_folder")}
            placeholder="C:/path/to/generated-invoices/"
          />
          <Field
            label="Database Path"
            value={form.db_path ?? ""}
            onChange={set("db_path")}
            placeholder="C:/path/to/invoices.db"
          />
        </Section>

        <Section title="Pipeline Defaults">
          <div className="settings-inner-grid" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            <Field
              label="Default Item Rate"
              value={String(form.default_item_rate ?? 1.0)}
              onChange={set("default_item_rate")}
              type="number"
              placeholder="1.00"
            />
            <Field
              label="Default Customer Name"
              value={form.default_customer ?? ""}
              onChange={set("default_customer")}
              placeholder="Generic"
            />
          </div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <div style={{ fontWeight: 500, color: "var(--text)", fontSize: "0.9rem" }}>
                Deduplication
              </div>
              <div style={{ fontSize: "0.8125rem", color: "var(--muted)", marginTop: "0.25rem" }}>
                Skip invoices already pushed for the same PDF + customer + date
              </div>
            </div>
            <button
              type="button"
              onClick={() => set("dedup_enabled")(!form.dedup_enabled)}
              style={{
                width: 48, height: 26, borderRadius: 13,
                background: form.dedup_enabled !== false ? "var(--green)" : "var(--border-hi)",
                border: "none", cursor: "pointer",
                position: "relative", transition: "background 0.2s", flexShrink: 0,
              }}
            >
              <span
                style={{
                  position: "absolute", top: 3,
                  left: form.dedup_enabled !== false ? 25 : 3,
                  width: 20, height: 20, borderRadius: "50%",
                  background: "white", transition: "left 0.2s",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.3)",
                }}
              />
            </button>
          </div>
        </Section>

        <Section title="Folder Watcher (Desktop only)">
          <div style={{ padding: "0.5rem 0.75rem", borderRadius: 8, background: "rgba(59,130,246,0.08)", border: "1px solid rgba(59,130,246,0.2)", fontSize: "0.8125rem", color: "var(--accent)" }}>
            Auto-watching requires the desktop app running locally. Not available in cloud mode.
          </div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <div style={{ fontWeight: 500, color: "var(--text)", fontSize: "0.9rem" }}>
                Auto-watch input folder
              </div>
              <div style={{ fontSize: "0.8125rem", color: "var(--muted)", marginTop: "0.25rem" }}>
                Triggers pipeline automatically when a new PDF lands
              </div>
            </div>
            <button
              type="button"
              onClick={toggleWatcher}
              style={{
                width: 48, height: 26, borderRadius: 13,
                background: watchStatus?.enabled ? "var(--green)" : "var(--border-hi)",
                border: "none", cursor: "pointer",
                position: "relative", transition: "background 0.2s", flexShrink: 0,
              }}
            >
              <span
                style={{
                  position: "absolute", top: 3,
                  left: watchStatus?.enabled ? 25 : 3,
                  width: 20, height: 20, borderRadius: "50%",
                  background: "white", transition: "left 0.2s",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.3)",
                }}
              />
            </button>
          </div>
          {watchStatus?.last_event && (
            <div style={{ fontSize: "0.8125rem", color: "var(--muted)" }}>
              Last trigger: {new Date(watchStatus.last_event).toLocaleString()}
            </div>
          )}
        </Section>

        {/* Save bar */}
        <div
          style={{
            display: "flex", alignItems: "center", justifyContent: "space-between",
            padding: "1rem 1.5rem",
            background: "var(--card)", border: "1px solid var(--border)",
            borderRadius: 12, marginTop: "0.5rem",
          }}
        >
          <span style={{ fontSize: "0.875rem", color: saved ? "var(--green)" : "var(--muted)" }}>
            {saved ? "✓ Settings saved" : "Unsaved changes"}
          </span>
          <button
            type="submit"
            disabled={saving}
            style={{
              padding: "0.625rem 1.5rem",
              background: saving ? "var(--border-hi)" : "var(--accent)",
              color: "white", border: "none", borderRadius: 8,
              fontFamily: "var(--font-syne, Syne, sans-serif)",
              fontWeight: 700, fontSize: "0.9rem",
              cursor: saving ? "not-allowed" : "pointer",
              display: "flex", alignItems: "center", gap: "0.5rem",
              transition: "background 0.15s",
            }}
          >
            {saving ? (
              <>
                <span className="animate-spin" style={{ width: 14, height: 14, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "white", borderRadius: "50%", display: "inline-block" }} />
                Saving…
              </>
            ) : "Save Settings"}
          </button>
        </div>
      </form>
    </div>
  );
}
