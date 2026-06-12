import { useEffect, useState } from "react";
import type { Settings } from "../types";
import { api } from "../api";

export function useSettings(enabled = true) {
  const [settings, setSettings] = useState<Settings | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!enabled) return;
    setLoading(true);
    api.settings
      .get()
      .then(setSettings)
      .finally(() => setLoading(false));
  }, [enabled]);

  useEffect(() => {
    if (settings?.theme) {
      document.documentElement.setAttribute("data-theme", settings.theme);
    }
  }, [settings?.theme]);

  const updateSettings = async (patch: Partial<Settings>) => {
    const updated = await api.settings.update(patch);
    setSettings(updated);
    return updated;
  };

  return { settings, loading, updateSettings, setSettings };
}

export function daysUntilExam(examDate: string | null): number | null {
  if (!examDate) return null;
  const target = new Date(examDate + "T00:00:00");
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  const diff = Math.ceil((target.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  return diff;
}

export function readinessClass(label: string): string {
  if (label.includes("Ready") && !label.includes("Near")) return "ready";
  if (label.includes("Near")) return "near";
  if (label.includes("Building")) return "building";
  return "focus";
}
