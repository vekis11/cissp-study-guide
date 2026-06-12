import { useEffect, useState } from "react";
import { api } from "../api";

interface ServerWakeUpProps {
  onReady: () => void;
}

export function ServerWakeUp({ onReady }: ServerWakeUpProps) {
  const [message, setMessage] = useState("Connecting to study server…");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;

    const wake = async () => {
      for (let i = 0; i < 8; i++) {
        if (cancelled) return;
        setAttempt(i + 1);
        try {
          await api.health();
          if (!cancelled) onReady();
          return;
        } catch {
          setMessage(
            i < 2
              ? "Connecting to study server…"
              : "Server is waking up (Render cold start). This can take up to a minute…",
          );
          await new Promise((r) => setTimeout(r, 2500 + i * 1500));
        }
      }
      if (!cancelled) {
        setMessage("Server is slow to respond. Retrying — check your connection.");
        onReady();
      }
    };

    wake();
    return () => {
      cancelled = true;
    };
  }, [onReady]);

  return (
    <div className="server-wakeup glass-card">
      <div className="loading shimmer" style={{ marginBottom: "1rem" }}>
        Starting CISSP Study Companion
      </div>
      <p>{message}</p>
      <p className="sub">Attempt {attempt} of 8</p>
    </div>
  );
}
