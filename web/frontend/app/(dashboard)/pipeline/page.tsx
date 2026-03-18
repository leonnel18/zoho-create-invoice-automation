"use client";

import { useEffect, useRef, useState } from "react";
import { pipeline as pipelineApi } from "@/lib/api";
import type { Job } from "@/lib/api";

// ── Payment details ───────────────────────────────────────────────────────────
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
      <div style={{ position: "fixed", top: "50%", left: "50%", transform: "translate(-50%,-50%)", zIndex: 100, width: 380, background: "var(--card)", border: "1px solid var(--border)", borderRadius: 16, padding: "1.5rem", boxShadow: "0 24px 64px rgba(0,0,0,0.5)" }}>
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

function JobBadge({ status }: { status: Job["status"] }) {
  const map = {
    done:    { dot: "dot-green",  bg: "rgba(34,211,165,0.12)",  color: "var(--green)"  },
    error:   { dot: "dot-red",    bg: "rgba(248,113,113,0.12)", color: "var(--red)"    },
    running: { dot: "dot-orange", bg: "rgba(251,146,60,0.12)",  color: "var(--orange)" },
  };
  const s = map[status] ?? map.running;
  return (
    <span
      style={{
        display: "inline-flex", alignItems: "center", gap: "0.375rem",
        padding: "0.125rem 0.625rem", borderRadius: 20, fontSize: "0.75rem", fontWeight: 600,
        background: s.bg, color: s.color,
      }}
    >
      <span className={`dot ${s.dot} ${status === "running" ? "animate-pulse-dot" : ""}`} />
      {status}
    </span>
  );
}

export default function PipelinePage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [activeJob, setActiveJob] = useState<Job | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");
  const [uploadFiles, setUploadFiles] = useState<File[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const [showMatcha, setShowMatcha] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const logRef = useRef<HTMLDivElement>(null);

  function scrollLog() {
    if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight;
  }

  async function loadJobs() {
    try {
      const j = await pipelineApi.jobs();
      setJobs(j);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load jobs");
    }
  }

  useEffect(() => {
    loadJobs();
  }, []);

  function startPolling(jobId: number) {
    pollRef.current = setInterval(async () => {
      try {
        const job = await pipelineApi.status(jobId);
        setActiveJob(job);
        scrollLog();
        if (job.status !== "running") {
          clearInterval(pollRef.current!);
          setRunning(false);
          loadJobs();
        }
      } catch {
        clearInterval(pollRef.current!);
        setRunning(false);
      }
    }, 1500);
  }

  function addFiles(incoming: FileList | null) {
    if (!incoming) return;
    const pdfs = Array.from(incoming).filter((f) => f.name.toLowerCase().endsWith(".pdf"));
    setUploadFiles((prev) => {
      const names = new Set(prev.map((f) => f.name));
      return [...prev, ...pdfs.filter((f) => !names.has(f.name))];
    });
  }

  async function handleUpload() {
    if (!uploadFiles.length) return;
    setError("");
    setRunning(true);
    setActiveJob(null);
    try {
      const { job_id } = await pipelineApi.upload(uploadFiles);
      setUploadFiles([]);
      const job = await pipelineApi.status(job_id);
      setActiveJob(job);
      startPolling(job_id);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Upload failed");
      setRunning(false);
    }
  }

  async function handleRun() {
    setError("");
    setRunning(true);
    setActiveJob(null);
    try {
      const { job_id } = await pipelineApi.run();
      const job = await pipelineApi.status(job_id);
      setActiveJob(job);
      startPolling(job_id);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to start pipeline");
      setRunning(false);
    }
  }

  async function handleStop() {
    if (!activeJob) return;
    try {
      await pipelineApi.stop(activeJob.id);
    } catch {
      // ignore — polling will pick up the final state
    }
  }

  function selectJob(job: Job) {
    setActiveJob(job);
  }

  return (
    <div>
      {showMatcha && <MatchaModal onClose={() => setShowMatcha(false)} />}

      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: "2rem" }}>
        <div>
          <h1 style={{ fontFamily: "var(--font-syne, Syne, sans-serif)", fontSize: "1.75rem", fontWeight: 800, color: "var(--text)", letterSpacing: "-0.03em" }}>
            Pipeline
          </h1>
          <p style={{ color: "var(--muted)", marginTop: "0.25rem" }}>Upload delivery receipt PDFs to create invoices in Zoho Books</p>
        </div>
        <button
          onClick={() => setShowMatcha(true)}
          style={{
            padding: "0.5rem 1rem", background: "rgba(34,211,165,0.07)",
            border: "1px solid rgba(34,211,165,0.2)", borderRadius: 8,
            color: "var(--green)", fontSize: "0.8125rem", fontWeight: 600,
            cursor: "pointer", flexShrink: 0, whiteSpace: "nowrap",
          }}
        >
          🍵 Buy me a Matcha
        </button>
      </div>

      {error && (
        <div style={{ background: "rgba(248,113,113,0.1)", border: "1px solid rgba(248,113,113,0.3)", borderRadius: 8, padding: "0.75rem 1rem", color: "var(--red)", marginBottom: "1.5rem", fontSize: "0.875rem" }}>
          {error}
        </div>
      )}

      {/* PDF Upload dropzone */}
      <div
        className="card"
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); addFiles(e.dataTransfer.files); }}
        style={{
          marginBottom: "1rem",
          border: dragOver ? "1.5px dashed var(--accent)" : "1.5px dashed var(--border-hi)",
          background: dragOver ? "rgba(59,130,246,0.05)" : undefined,
          transition: "border-color 0.15s, background 0.15s",
          cursor: "pointer",
        }}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          multiple
          style={{ display: "none" }}
          onChange={(e) => addFiles(e.target.files)}
        />
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "0.75rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <span style={{ fontSize: "1.5rem", opacity: 0.5 }}>📄</span>
            <div>
              <div style={{ fontWeight: 600, color: "var(--text)", fontSize: "0.9rem" }}>
                {uploadFiles.length ? `${uploadFiles.length} PDF${uploadFiles.length > 1 ? "s" : ""} selected` : "Upload PDFs"}
              </div>
              <div style={{ fontSize: "0.75rem", color: "var(--muted)", marginTop: "0.125rem" }}>
                {uploadFiles.length
                  ? uploadFiles.map((f) => f.name).join(", ")
                  : "Drag & drop or click to browse — cloud mode"}
              </div>
            </div>
          </div>
          <div style={{ display: "flex", gap: "0.5rem" }} onClick={(e) => e.stopPropagation()}>
            {uploadFiles.length > 0 && (
              <button
                onClick={() => setUploadFiles([])}
                style={{
                  padding: "0.5rem 0.875rem", background: "transparent",
                  border: "1px solid var(--border-hi)", borderRadius: 7,
                  color: "var(--muted)", fontSize: "0.8125rem", cursor: "pointer",
                }}
              >
                Clear
              </button>
            )}
            <button
              onClick={handleUpload}
              disabled={running || uploadFiles.length === 0}
              style={{
                padding: "0.5rem 1.25rem",
                background: uploadFiles.length && !running ? "var(--accent)" : "var(--border-hi)",
                color: uploadFiles.length && !running ? "white" : "var(--muted)",
                border: "none", borderRadius: 7,
                fontFamily: "var(--font-syne, Syne, sans-serif)",
                fontWeight: 700, fontSize: "0.875rem",
                cursor: uploadFiles.length && !running ? "pointer" : "not-allowed",
                display: "flex", alignItems: "center", gap: "0.5rem",
              }}
            >
              {running ? (
                <>
                  <span className="animate-spin" style={{ width: 13, height: 13, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "white", borderRadius: "50%", display: "inline-block" }} />
                  Processing…
                </>
              ) : "Process PDFs"}
            </button>
          </div>
        </div>
      </div>

      <div className="pipeline-layout" style={{ display: "grid", gridTemplateColumns: "260px 1fr", gap: "1rem", alignItems: "start" }}>
        {/* Job list */}
        <div className="pipeline-history-panel card" style={{ padding: "0.75rem" }}>
          <div style={{ fontSize: "0.75rem", color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.08em", padding: "0.25rem 0.75rem", marginBottom: "0.5rem" }}>
            Run History
          </div>
          {jobs.length === 0 ? (
            <div style={{ padding: "1rem 0.75rem", color: "var(--muted)", fontSize: "0.875rem" }}>No runs yet</div>
          ) : (
            jobs.map((job) => (
              <button
                key={job.id}
                onClick={() => selectJob(job)}
                style={{
                  display: "block", width: "100%", textAlign: "left",
                  padding: "0.625rem 0.75rem", borderRadius: 6,
                  background: activeJob?.id === job.id ? "var(--surface)" : "transparent",
                  border: "none", cursor: "pointer",
                  color: "var(--text)", fontSize: "0.8125rem",
                  marginBottom: "0.125rem", transition: "background 0.1s",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontFamily: "var(--font-mono)", color: "var(--muted-hi)", fontSize: "0.75rem" }}>#{job.id}</span>
                  <JobBadge status={job.status} />
                </div>
                <div style={{ color: "var(--muted)", fontSize: "0.75rem", marginTop: "0.25rem" }}>
                  {new Date(job.started_at).toLocaleString()}
                </div>
                <div style={{ color: "var(--muted-hi)", fontSize: "0.75rem" }}>
                  via {job.triggered_by}
                </div>
              </button>
            ))
          )}
        </div>

        {/* Log viewer */}
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          {activeJob ? (
            <>
              {/* Job header */}
              <div
                style={{
                  padding: "1rem 1.25rem",
                  borderBottom: "1px solid var(--border)",
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  <span style={{ fontFamily: "var(--font-mono)", color: "var(--muted)", fontSize: "0.8125rem" }}>
                    Job #{activeJob.id}
                  </span>
                  <JobBadge status={activeJob.status} />
                </div>
                <div style={{ display: "flex", gap: "1.5rem", fontSize: "0.8125rem" }}>
                  <span style={{ color: "var(--muted)" }}>
                    Pushed: <span style={{ color: "var(--green)", fontWeight: 600 }}>{activeJob.invoices_pushed}</span>
                  </span>
                  <span style={{ color: "var(--muted)" }}>
                    Errors: <span style={{ color: activeJob.errors > 0 ? "var(--red)" : "var(--muted)", fontWeight: 600 }}>{activeJob.errors}</span>
                  </span>
                  {activeJob.finished_at && (
                    <span style={{ color: "var(--muted)" }}>
                      {((new Date(activeJob.finished_at).getTime() - new Date(activeJob.started_at).getTime()) / 1000).toFixed(1)}s
                    </span>
                  )}
                </div>
              </div>

              {/* Log output */}
              <div
                ref={logRef}
                style={{
                  padding: "1rem 1.25rem",
                  fontFamily: "var(--font-mono)",
                  fontSize: "0.75rem",
                  lineHeight: 1.7,
                  color: "var(--muted-hi)",
                  background: "#0a0c14",
                  minHeight: 320,
                  maxHeight: 480,
                  overflowY: "auto",
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-word",
                }}
              >
                {activeJob.log_output
                  ? activeJob.log_output.split("\n").map((line, i) => {
                      const isError = /error|failed|exception/i.test(line);
                      const isSuccess = /pushed|success|done/i.test(line);
                      return (
                        <div
                          key={i}
                          style={{
                            color: isError
                              ? "var(--red)"
                              : isSuccess
                              ? "var(--green)"
                              : "var(--muted-hi)",
                          }}
                        >
                          {line}
                        </div>
                      );
                    })
                  : (
                    <span style={{ color: "var(--muted)" }}>
                      {activeJob.status === "running" ? "Pipeline running…" : "No output captured"}
                    </span>
                  )
                }
                {activeJob.status === "running" && (
                  <div style={{ display: "flex", gap: "0.375rem", marginTop: "0.5rem" }}>
                    {[0, 1, 2].map((i) => (
                      <span
                        key={i}
                        className="animate-pulse-dot"
                        style={{
                          display: "inline-block", width: 6, height: 6,
                          borderRadius: "50%", background: "var(--accent)",
                          animationDelay: `${i * 0.2}s`,
                        }}
                      />
                    ))}
                  </div>
                )}
              </div>
            </>
          ) : (
            <div
              style={{
                minHeight: 400, display: "flex", alignItems: "center", justifyContent: "center",
                flexDirection: "column", gap: "0.75rem", padding: "2rem",
              }}
            >
              <div style={{ fontSize: "2rem", opacity: 0.2 }}>▶</div>
              <div style={{ color: "var(--muted)", fontSize: "0.875rem" }}>
                Run the pipeline or select a past job to view logs
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
