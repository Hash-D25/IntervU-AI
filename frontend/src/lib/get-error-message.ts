import { ApiError } from "@/lib/api-client";
import { getApiConnectionErrorMessage } from "@/lib/api-connection-error";

export function getErrorMessage(err: unknown, fallback: string): string {
  if (err instanceof ApiError) {
    return err.message;
  }
  if (err instanceof TypeError) {
    return getApiConnectionErrorMessage();
  }
  if (err instanceof Error) {
    return err.message;
  }
  return fallback;
}
