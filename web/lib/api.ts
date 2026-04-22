import { ApiEnvelope } from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function fetchApi<T>(
  path: string,
  fallback: T,
  init?: RequestInit,
): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
    });

    if (!response.ok) {
      throw new Error(`API error ${response.status}`);
    }

    const payload = (await response.json()) as ApiEnvelope<T>;
    return payload.data;
  } catch {
    return fallback;
  }
}

export async function postApi<TPayload, TResponse>(
  path: string,
  payload: TPayload,
  fallback: TResponse,
): Promise<TResponse> {
  return fetchApi<TResponse>(path, fallback, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

