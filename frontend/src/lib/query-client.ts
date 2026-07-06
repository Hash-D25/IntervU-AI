import { QueryClient } from "@tanstack/react-query";

// Factory (not a singleton) so each browser session / test gets a fresh cache.
export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60_000,
        retry: 1,
        refetchOnWindowFocus: false,
      },
    },
  });
}
