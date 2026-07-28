import type { ReactNode, ThHTMLAttributes } from 'react'

import { cn } from '@/lib/cn'

export function TableShell({ children }: { children: ReactNode }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-stone-200 bg-white">
      <table className="w-full border-collapse text-sm">{children}</table>
    </div>
  )
}

export function Th({ className, ...props }: ThHTMLAttributes<HTMLTableCellElement>) {
  return (
    <th
      scope="col"
      className={cn(
        'border-b border-stone-200 bg-stone-50 px-4 py-2.5 text-left text-xs font-semibold tracking-wide text-stone-500 uppercase',
        className,
      )}
      {...props}
    />
  )
}

export function Td({
  className,
  children,
}: {
  className?: string
  children?: ReactNode
}) {
  return <td className={cn('border-b border-stone-100 px-4 py-3 text-stone-700', className)}>{children}</td>
}

export function Tr({
  children,
  muted = false,
}: {
  children: ReactNode
  /** Soft-deleted rows are dimmed rather than hidden, so the state stays legible. */
  muted?: boolean
}) {
  return <tr className={cn('hover:bg-stone-50/70', muted && 'opacity-55')}>{children}</tr>
}
