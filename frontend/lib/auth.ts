const TOKEN_KEY = "factory_monitor_token";

export function persistToken(token: string) {
  if (typeof window === "undefined") {
    return;
  }
  localStorage.setItem(TOKEN_KEY, token);
  document.cookie = `factory_monitor_token=${token}; path=/; max-age=86400; samesite=lax`;
}

export function getStoredToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem(TOKEN_KEY);
}

export function clearStoredToken() {
  if (typeof window === "undefined") {
    return;
  }
  localStorage.removeItem(TOKEN_KEY);
  document.cookie = "factory_monitor_token=; path=/; max-age=0; samesite=lax";
}
