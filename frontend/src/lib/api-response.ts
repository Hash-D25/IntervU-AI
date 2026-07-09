import { ApiError, parseApiErrorResponse } from "@/lib/api-client";

export async function throwIfNotOk(response: Response, fallback: string): Promise<void> {
  if (!response.ok) {
    throw new ApiError(response.status, await parseApiErrorResponse(response, fallback));
  }
}

export async function authGetNullable<T>(response: Response, fallback: string): Promise<T | null> {
  if (response.status === 404) {
    return null;
  }
  await throwIfNotOk(response, fallback);
  return (await response.json()) as T;
}
