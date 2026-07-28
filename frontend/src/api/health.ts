import { useQuery } from '@tanstack/react-query'

import { api } from './client'

/**
 * `GET /health` answers 200 when the database responds and 503 when it does not.
 * A 503 is a meaningful answer here, not a failure, so this does not use
 * `unwrap` — it reads the status code directly and never throws.
 */
export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      try {
        const { response } = await api.GET('/health')
        return response.ok ? 'ok' : 'degraded'
      } catch {
        return 'unreachable'
      }
    },
    refetchInterval: 30_000,
    retry: false,
  })
}
