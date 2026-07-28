import { useEffect, useRef } from 'react'
import type { ReactNode } from 'react'

import { Button } from './Button'

type ModalProps = {
  open: boolean
  title: string
  description?: string
  onClose: () => void
  children: ReactNode
  footer?: ReactNode
}

/**
 * Built on the native <dialog>: `showModal()` gives Escape-to-close, focus
 * containment and inertness of the rest of the page for free.
 */
export function Modal({ open, title, description, onClose, children, footer }: ModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null)

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return

    if (open && !dialog.open) dialog.showModal()
    if (!open && dialog.open) dialog.close()
  }, [open])

  return (
    <dialog
      ref={dialogRef}
      onClose={onClose}
      className="m-auto w-[min(36rem,calc(100vw-2rem))] rounded-xl bg-white p-0 text-stone-900 shadow-xl backdrop:bg-stone-900/40"
    >
      <div className="flex items-start justify-between gap-4 border-b border-stone-200 px-5 py-4">
        <div>
          <h2 className="text-base font-semibold text-stone-900">{title}</h2>
          {description ? <p className="mt-0.5 text-sm text-stone-500">{description}</p> : null}
        </div>
        <Button variant="ghost" size="sm" onClick={onClose} aria-label="Cerrar">
          ✕
        </Button>
      </div>

      <div className="max-h-[70vh] overflow-y-auto px-5 py-4">{children}</div>

      {footer ? (
        <div className="flex justify-end gap-2 border-t border-stone-200 bg-stone-50 px-5 py-3">
          {footer}
        </div>
      ) : null}
    </dialog>
  )
}
