import { Link, Outlet } from '@tanstack/react-router'

import { useHealth } from '@/api/health'
import { cn } from '@/lib/cn'

const NAV = [
  { to: '/ingredients', label: 'Ingredientes', icon: '🌾' },
  { to: '/recipes', label: 'Recetas', icon: '📋' },
  { to: '/products', label: 'Productos', icon: '🧁' },
] as const

function HealthDot() {
  const { data: status, isPending } = useHealth()

  const tone = isPending
    ? { color: 'bg-stone-300', label: 'Comprobando API…' }
    : status === 'ok'
      ? { color: 'bg-emerald-500', label: 'API y base de datos OK' }
      : status === 'degraded'
        ? { color: 'bg-amber-500', label: 'API arriba, base de datos no disponible' }
        : { color: 'bg-red-500', label: 'API no alcanzable' }

  return (
    <div className="flex items-center gap-2 text-xs text-stone-500">
      <span className={cn('size-2 rounded-full', tone.color)} aria-hidden />
      {tone.label}
    </div>
  )
}

export function AppLayout() {
  return (
    <div className="flex min-h-screen bg-stone-50 text-stone-900">
      <aside className="hidden w-60 shrink-0 flex-col justify-between border-r border-stone-200 bg-white px-4 py-6 sm:flex">
        <div>
          <div className="px-2">
            <p className="text-sm font-semibold tracking-tight text-stone-900">Panadería</p>
            <p className="text-xs text-stone-500">Gestión de inventario</p>
          </div>

          <nav className="mt-8 space-y-1">
            {NAV.map((item) => (
              <Link
                key={item.to}
                to={item.to}
                className="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm font-medium text-stone-600 transition-colors hover:bg-stone-100 hover:text-stone-900"
                activeProps={{ className: 'bg-amber-50 text-amber-900 hover:bg-amber-50' }}
              >
                <span aria-hidden>{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        <HealthDot />
      </aside>

      {/* Narrow screens get the same nav as a horizontal bar. */}
      <div className="flex min-w-0 flex-1 flex-col">
        <nav className="flex gap-1 border-b border-stone-200 bg-white px-4 py-2 sm:hidden">
          {NAV.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className="rounded-lg px-3 py-1.5 text-sm font-medium text-stone-600"
              activeProps={{ className: 'bg-amber-50 text-amber-900' }}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <main className="mx-auto w-full max-w-6xl flex-1 space-y-6 px-4 py-8 sm:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
