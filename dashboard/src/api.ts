/**
 * API base URL from env. Empty in dev (Vite proxy handles /api).
 * Set VITE_API_URL in production (e.g. https://snip.mothership-ai.com or Railway URL).
 */
export const apiBase = (import.meta.env.VITE_API_URL as string) || '';

export function apiUrl(path: string): string {
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${apiBase}${p}`;
}
