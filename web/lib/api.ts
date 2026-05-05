import type { paths } from "@/lib/generated/api-types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
const ALLOW_API_FALLBACK = process.env.NEXT_PUBLIC_ALLOW_API_FALLBACK === "true";

type HttpMethod = "get" | "post";
type OperationFor<
  TPath extends keyof paths,
  TMethod extends HttpMethod,
> = TMethod extends keyof paths[TPath]
  ? NonNullable<paths[TPath][TMethod]> extends never
    ? never
    : NonNullable<paths[TPath][TMethod]>
  : never;

type PathWithMethod<TMethod extends HttpMethod> = {
  [TPath in keyof paths]: OperationFor<TPath, TMethod> extends never
    ? never
    : TPath;
}[keyof paths];

type JsonResponse<
  TPath extends keyof paths,
  TMethod extends HttpMethod,
> = OperationFor<TPath, TMethod> extends {
  responses: {
    200: {
      content: {
        "application/json": infer TResponse;
      };
    };
  };
}
  ? TResponse
  : never;

type ApiData<
  TPath extends keyof paths,
  TMethod extends HttpMethod,
> = JsonResponse<TPath, TMethod> extends { data: infer TData }
  ? TData
  : JsonResponse<TPath, TMethod>;

type QueryFor<TPath extends PathWithMethod<"get">> = OperationFor<
  TPath,
  "get"
> extends {
  parameters: {
    query?: infer TQuery;
  };
}
  ? TQuery
  : never;

type BodyFor<TPath extends PathWithMethod<"post">> = OperationFor<
  TPath,
  "post"
> extends {
  requestBody: {
    content: {
      "application/json": infer TBody;
    };
  };
}
  ? TBody
  : never;

type FetchOptions<TPath extends PathWithMethod<"get">> = {
  query?: QueryFor<TPath>;
  init?: RequestInit;
};

class ApiFetchError extends Error {
  constructor(path: string, error: unknown) {
    const detail = error instanceof Error ? error.message : String(error);
    super(`API request failed for ${path}: ${detail}`);
    this.name = "ApiFetchError";
  }
}

function buildUrl<TPath extends keyof paths>(
  path: TPath,
  query?: Record<string, string | number | boolean | null | undefined>,
) {
  const url = new URL(String(path), API_BASE_URL);
  for (const [key, value] of Object.entries(query ?? {})) {
    if (value !== undefined && value !== null) {
      url.searchParams.set(key, String(value));
    }
  }
  return url.toString();
}

async function requestJson<
  TPath extends keyof paths,
  TMethod extends HttpMethod,
>(
  path: TPath,
  fallback: ApiData<TPath, TMethod>,
  init: RequestInit,
  query?: Record<string, string | number | boolean | null | undefined>,
): Promise<ApiData<TPath, TMethod>> {
  try {
    const response = await fetch(buildUrl(path, query), {
      ...init,
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
        ...(init.headers ?? {}),
      },
    });

    if (!response.ok) {
      throw new Error(`API error ${response.status}`);
    }

    const payload = (await response.json()) as JsonResponse<TPath, TMethod>;
    if (payload && typeof payload === "object" && "data" in payload) {
      return (payload as { data: ApiData<TPath, TMethod> }).data;
    }
    return payload as ApiData<TPath, TMethod>;
  } catch (error) {
    if (
      error instanceof Error &&
      error.message.includes("Dynamic server usage")
    ) {
      throw error;
    }

    if (ALLOW_API_FALLBACK) {
      console.warn(`Using explicit fallback data for ${String(path)}`, error);
      return fallback;
    }

    throw new ApiFetchError(String(path), error);
  }
}

export async function fetchApi<TPath extends PathWithMethod<"get">>(
  path: TPath,
  fallback: ApiData<TPath, "get">,
  options: FetchOptions<TPath> = {},
): Promise<ApiData<TPath, "get">> {
  return requestJson<TPath, "get">(
    path,
    fallback,
    options.init ?? {},
    options.query as Record<string, string | number | boolean | null | undefined>,
  );
}

export async function postApi<TPath extends PathWithMethod<"post">>(
  path: TPath,
  payload: BodyFor<TPath>,
  fallback: ApiData<TPath, "post">,
): Promise<ApiData<TPath, "post">> {
  return requestJson<TPath, "post">(path, fallback, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
