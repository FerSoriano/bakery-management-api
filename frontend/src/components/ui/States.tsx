import type { ReactNode } from 'react'

import { ApiError } from '@/api/client'

import { Button } from './Button'

export function LoadingState({ label = 'Cargando…' }: { label?: string }) {
  return (
    <div className="flex items-center justify-center gap-3 rounded-xl border border-stone-200 bg-white py-16 text-sm text-stone-500">
      <span
        aria-hidden
        className="size-4 animate-spin rounded-full border-2 border-stone-300 border-t-amber-700"
      />
      {label}
    </div>
  )
}

export function ErrorState({ error, onRetry }: { error: unknown; onRetry?: () => void }) {
  const message =
    error instanceof ApiError
      ? error.message
      : error instanceof Error
        ? // A TypeError from fetch means the request never reached the API.
          'No se pudo conectar con la API. ¿Está corriendo en http://127.0.0.1:8000?'
        : 'Ocurrió un error inesperado.'

  return (
    <div className="rounded-xl border border-red-200 bg-red-50 px-5 py-8 text-center">
      <p className="text-sm font-medium text-red-800">{message}</p>
      {onRetry ? (
        <Button variant="secondary" size="sm" className="mt-4" onClick={onRetry}>
          Reintentar
        </Button>
      ) : null}
    </div>
  )
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string
  description?: string
  action?: ReactNode
}) {
  return (
    <div className="rounded-xl border border-dashed border-stone-300 bg-white px-5 py-16 text-center">
      <p className="text-sm font-medium text-stone-700">{title}</p>
      {description ? <p className="mt-1 text-sm text-stone-500">{description}</p> : null}
      {action ? <div className="mt-4 flex justify-center">{action}</div> : null}
    </div>
  )
}
