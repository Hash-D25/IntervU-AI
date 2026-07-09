import { env } from "@/env";

/** User-facing hint when fetch fails before a response (network / mixed content / wrong API URL). */
export function getApiConnectionErrorMessage(): string {
  if (typeof window === "undefined") {
    return "Cannot reach the API. Check that the backend is running and CORS is configured.";
  }

  const onLocalhost =
    window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";
  const apiPointsToLocalhost =
    env.apiBaseUrl.includes("localhost") || env.apiBaseUrl.includes("127.0.0.1");

  if (!onLocalhost && apiPointsToLocalhost) {
    return "This site is deployed but still points to a local API. Set NEXT_PUBLIC_API_BASE_URL in Vercel to your public backend URL (https://…) and redeploy.";
  }

  if (!onLocalhost && env.apiBaseUrl.startsWith("http://")) {
    return "The API URL must use https in production. Update NEXT_PUBLIC_API_BASE_URL on Vercel.";
  }

  if (onLocalhost) {
    return "Cannot reach the API. Start the backend (uvicorn) on port 8000 and check CORS_ORIGINS.";
  }

  return "Cannot reach the API. Confirm the backend is running, publicly reachable, and allows this origin in CORS_ORIGINS.";
}
