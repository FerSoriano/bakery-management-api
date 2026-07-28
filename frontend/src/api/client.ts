import createClient from 'openapi-fetch'

import type { paths } from './schema'

const baseUrl = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000'

export const api = createClient<paths>({ baseUrl })

/** An error carrying the HTTP status, so callers can branch on 404 / 409 / 422. */
export class ApiError extends Error {
  status: number
  detail: unknown

  constructor(message: string, status: number, detail?: unknown) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

type ValidationDetail = { loc: (string | number)[]; msg: string; type: string }

function isValidationDetail(value: unknown): value is ValidationDetail {
  return typeof value === 'object' && value !== null && 'msg' in value && 'loc' in value
}

/**
 * FastAPI answers with `{"detail": "..."}` for HTTPException and with
 * `{"detail": [{loc, msg, type}, ...]}` for 422s. Flatten both into one string.
 */
function messageFromDetail(error: unknown, status: number): string {
  if (typeof error === 'object' && error !== null && 'detail' in error) {
    const detail = (error as { detail: unknown }).detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      const parts = detail.filter(isValidationDetail).map((item) => {
        // loc looks like ["body", "sale_price"]; the field name is the last entry.
        const field = item.loc.at(-1)
        return field === undefined ? item.msg : `${String(field)}: ${item.msg}`
      })
      if (parts.length > 0) return parts.join(' · ')
    }
  }
  return `Error ${status} al comunicarse con la API`
}

type FetchResult<T> = { data?: T; error?: unknown; response: Response }

/**
 * Turn openapi-fetch's `{ data, error }` result into a value-or-throw, which is
 * what TanStack Query expects.
 */
export async function unwrap<T>(request: Promise<FetchResult<T>>): Promise<T> {
  const { data, error, response } = await request

  if (!response.ok) {
    throw new ApiError(messageFromDetail(error, response.status), response.status, error)
  }

  return data as T
}
