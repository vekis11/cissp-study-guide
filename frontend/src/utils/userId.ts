const STORAGE_KEY = "cissp-study-user-id";

export function getUserId(): string {
  try {
    let id = localStorage.getItem(STORAGE_KEY);
    if (!id) {
      id = crypto.randomUUID().replace(/-/g, "");
      localStorage.setItem(STORAGE_KEY, id);
    }
    return id;
  } catch {
    return "local-fallback-user";
  }
}

export function setUserId(id: string): void {
  const trimmed = id.trim();
  if (trimmed.length >= 8) {
    localStorage.setItem(STORAGE_KEY, trimmed);
  }
}
