"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import BottomNav from "@/components/BottomNav";
import { auth as authApi, type UserRead } from "@/lib/api";

const COLLAPSED_KEY = "sidebar_collapsed";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<UserRead | null>(null);
  const [checking, setChecking] = useState(true);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    // Init collapse state from localStorage on mount
    setCollapsed(localStorage.getItem(COLLAPSED_KEY) === "true");

    const token = localStorage.getItem("token");
    if (!token) {
      router.replace("/login");
      return;
    }
    authApi
      .me()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("token");
        router.replace("/login");
      })
      .finally(() => setChecking(false));
  }, [router]);

  function logout() {
    localStorage.removeItem("token");
    router.push("/login");
  }

  function toggleCollapse() {
    setCollapsed((c) => {
      const next = !c;
      localStorage.setItem(COLLAPSED_KEY, String(next));
      return next;
    });
  }

  if (checking) {
    return (
      <div
        style={{
          minHeight: "100vh",
          background: "var(--bg)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <div
          className="animate-spin"
          style={{
            width: 28, height: 28,
            border: "3px solid var(--border-hi)",
            borderTopColor: "var(--accent)",
            borderRadius: "50%",
          }}
        />
      </div>
    );
  }

  const sidebarW = collapsed ? "64px" : "220px";

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg)" }}>
      <Sidebar
        userEmail={user?.email}
        displayName={user?.display_name ?? undefined}
        onLogout={logout}
        collapsed={collapsed}
        onToggleCollapse={toggleCollapse}
      />
      <main
        className={`main-content${collapsed ? " sidebar-rail" : ""}`}
        style={{
          flex: 1,
          marginLeft: sidebarW,
          padding: "2rem 2.5rem",
          maxWidth: `calc(100vw - ${sidebarW})`,
          overflowX: "hidden",
        }}
      >
        {children}
      </main>

      {/* Rendered in DOM always; CSS makes it visible only on mobile */}
      <BottomNav onLogout={logout} />
    </div>
  );
}
