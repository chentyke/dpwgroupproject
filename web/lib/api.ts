import { ApiEnvelope } from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
const ALLOW_API_FALLBACK = process.env.NEXT_PUBLIC_ALLOW_API_FALLBACK === "true";

class ApiFetchError extends Error {
  constructor(path: string, error: unknown) {
    const detail = error instanceof Error ? error.message : String(error);
    super(`API request failed for ${path}: ${detail}`);
    this.name = "ApiFetchError";
  }
}

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
  } catch (error) {
    if (
      error instanceof Error &&
      error.message.includes("Dynamic server usage")
    ) {
      throw error;
    }

    if (ALLOW_API_FALLBACK) {
      console.warn(`Using explicit fallback data for ${path}`, error);
      return fallback;
    }

    throw new ApiFetchError(path, error);
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
