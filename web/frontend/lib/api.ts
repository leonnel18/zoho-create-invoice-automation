/**
 * Typed API client — wraps fetch with auth headers + base URL.
 */

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers ?? {}),
    },
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Request failed");
  }

  return res.json() as Promise<T>;
}

// ── Auth ─────────────────────────────────────────────────────────
export interface TokenResponse {
  access_token: string;
  token_type: string;
}
export interface UserRead {
  id: number;
  email: string;
  display_name: string | null;
  created_at: string;
}

export const auth = {
  login: (email: string, password: string) =>
    request<TokenResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  register: (email: string, password: string, display_name?: string) =>
    request<UserRead>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, display_name }),
    }),
  me: () => request<UserRead>("/api/auth/me"),
};

// ── Settings ─────────────────────────────────────────────────────
export interface Settings {
  zoho_client_id: string;
  zoho_client_secret: string;   // masked
  zoho_refresh_token: string;   // masked
  zoho_org_id: string;
  zoho_region: string;
  input_folder: string;
  output_folder: string;
  db_path: string;
  default_item_rate: number;
  default_customer: string;
  watch_enabled: boolean;
}

export const settings = {
  get: () => request<Settings>("/api/settings"),
  update: (data: Partial<Settings>) =>
    request<Settings>("/api/settings", {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  verify: () =>
    request<{ ok: boolean; message: string }>("/api/settings/verify", {
      method: "POST",
    }),
};

// ── Pipeline ─────────────────────────────────────────────────────
export interface Job {
  id: number;
  status: "running" | "done" | "error";
  triggered_by: string;
  log_output: string | null;
  invoices_pushed: number;
  errors: number;
  started_at: string;
  finished_at: string | null;
}

export const pipeline = {
  run: () =>
    request<{ job_id: number; message: string }>("/api/pipeline/run", {
      method: "POST",
    }),
  upload: (files: File[]): Promise<{ job_id: number }> => {
    const token = getToken();
    const form = new FormData();
    files.forEach((f) => form.append("files", f));
    return fetch(`${BASE}/api/pipeline/upload`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: form,
    }).then(async (res) => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error((err as { detail?: string }).detail ?? "Upload failed");
      }
      return res.json() as Promise<{ job_id: number }>;
    });
  },
  status: (jobId: number) => request<Job>(`/api/pipeline/status/${jobId}`),
  stop:   (jobId: number) => request<{ ok: boolean; killed: boolean }>(`/api/pipeline/stop/${jobId}`, { method: "POST" }),
  jobs: () => request<Job[]>("/api/pipeline/jobs"),
};

// ── Invoices ─────────────────────────────────────────────────────
export interface Invoice {
  id: number;
  source_file: string;
  invoice_date: string;
  customer_name: string;
  zoho_invoice_id: string | null;
  pdf_output_path: string | null;
  status: "pending" | "pushed" | "error";
  error_message: string | null;
  processed_at: string | null;
}
export interface InvoiceStats {
  pending: number;
  pushed: number;
  error: number;
  total: number;
}

export const invoices = {
  list: (page = 1, pageSize = 20) =>
    request<{ items: Invoice[]; total: number; page: number }>(
      `/api/invoices?page=${page}&page_size=${pageSize}`
    ),
  stats: () => request<InvoiceStats>("/api/invoices/stats"),
};

// ── Watcher ──────────────────────────────────────────────────────
export interface WatcherStatus {
  enabled: boolean;
  folder: string | null;
  last_event: string | null;
}

export const watcher = {
  status: () => request<WatcherStatus>("/api/watcher/status"),
  enable: () =>
    request<WatcherStatus>("/api/watcher/enable", { method: "POST" }),
  disable: () =>
    request<WatcherStatus>("/api/watcher/disable", { method: "POST" }),
};
