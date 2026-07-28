import { useId } from 'react'
import type {
  InputHTMLAttributes,
  ReactNode,
  SelectHTMLAttributes,
  TextareaHTMLAttributes,
} from 'react'

import { cn } from '@/lib/cn'

const CONTROL_CLASSES = cn(
  'block w-full rounded-lg border-0 bg-white px-3 py-2 text-sm text-stone-900',
  'ring-1 ring-inset ring-stone-300 placeholder:text-stone-400',
  'focus:ring-2 focus:ring-inset focus:ring-amber-700 focus:outline-none',
  'disabled:cursor-not-allowed disabled:bg-stone-50 disabled:text-stone-500',
)

type FieldProps = {
  label: string
  hint?: string
  children: (controlProps: { id: string; 'aria-describedby'?: string }) => ReactNode
}

/**
 * Wires a label to its control with a generated id, so every control in the app
 * is reachable by its label without hand-managed ids.
 */
export function Field({ label, hint, children }: FieldProps) {
  const id = useId()
  const hintId = hint ? `${id}-hint` : undefined

  return (
    <div className="space-y-1.5">
      <label htmlFor={id} className="block text-sm font-medium text-stone-700">
        {label}
      </label>
      {children({ id, 'aria-describedby': hintId })}
      {hint ? (
        <p id={hintId} className="text-xs text-stone-500">
          {hint}
        </p>
      ) : null}
    </div>
  )
}

export function TextInput({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={cn(CONTROL_CLASSES, className)} {...props} />
}

export function Select({ className, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={cn(CONTROL_CLASSES, 'pr-8', className)} {...props} />
}

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={cn(CONTROL_CLASSES, 'resize-y', className)} {...props} />
}
