import { useState } from 'react'

import { INGREDIENT_CATEGORY_LABELS, MEASUREMENT_UNIT_LABELS } from '@/api/enums'
import {
  useDeactivateIngredient,
  useIngredients,
  useReactivateIngredient,
} from '@/api/ingredients'
import type { Ingredient } from '@/api/types'
import { InactiveToggle, PageHeader } from '@/components/PageHeader'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/States'
import { TableShell, Td, Th, Tr } from '@/components/ui/Table'
import { formatCurrency, formatQuantity } from '@/lib/format'

import { IngredientFormModal } from './IngredientFormModal'

export function IngredientsPage() {
  const [includeInactive, setIncludeInactive] = useState(false)
  const [editing, setEditing] = useState<Ingredient | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [pendingDeactivation, setPendingDeactivation] = useState<Ingredient | null>(null)

  const ingredients = useIngredients(includeInactive)
  const deactivate = useDeactivateIngredient()
  const reactivate = useReactivateIngredient()

  function openCreate() {
    setEditing(null)
    setFormOpen(true)
  }

  function openEdit(ingredient: Ingredient) {
    setEditing(ingredient)
    setFormOpen(true)
  }

  return (
    <>
      <PageHeader
        title="Ingredientes"
        description="Materia prima e inventario. El precio unitario es la base del costeo."
        actions={
          <>
            <InactiveToggle checked={includeInactive} onChange={setIncludeInactive} />
            <Button variant="primary" onClick={openCreate}>
              Nuevo ingrediente
            </Button>
          </>
        }
      />

      {ingredients.isPending ? (
        <LoadingState />
      ) : ingredients.isError ? (
        <ErrorState error={ingredients.error} onRetry={() => void ingredients.refetch()} />
      ) : ingredients.data.length === 0 ? (
        <EmptyState
          title="Todavía no hay ingredientes"
          description="Registra la materia prima para poder costear recetas."
          action={
            <Button variant="primary" onClick={openCreate}>
              Nuevo ingrediente
            </Button>
          }
        />
      ) : (
        <TableShell>
          <thead>
            <tr>
              <Th>Nombre</Th>
              <Th>Categoría</Th>
              <Th className="text-right">Stock</Th>
              <Th className="text-right">Precio unitario</Th>
              <Th>Estado</Th>
              <Th className="text-right">Acciones</Th>
            </tr>
          </thead>
          <tbody>
            {ingredients.data.map((ingredient) => (
              <Tr key={ingredient.id} muted={!ingredient.is_active}>
                <Td className="font-medium text-stone-900">{ingredient.name}</Td>
                <Td>{INGREDIENT_CATEGORY_LABELS[ingredient.category]}</Td>
                <Td className="text-right tabular-nums">
                  {formatQuantity(ingredient.stock_quantity)}{' '}
                  <span className="text-stone-400">{MEASUREMENT_UNIT_LABELS[ingredient.unit]}</span>
                </Td>
                <Td className="text-right tabular-nums">
                  {formatCurrency(ingredient.current_unit_price)}
                  <span className="text-stone-400">
                    {' / '}
                    {MEASUREMENT_UNIT_LABELS[ingredient.unit]}
                  </span>
                </Td>
                <Td>
                  {ingredient.is_active ? (
                    <Badge tone="success">Activo</Badge>
                  ) : (
                    <Badge tone="neutral">Inactivo</Badge>
                  )}
                </Td>
                <Td className="text-right whitespace-nowrap">
                  <Button size="sm" variant="ghost" onClick={() => openEdit(ingredient)}>
                    Editar
                  </Button>
                  {ingredient.is_active ? (
                    <Button
                      size="sm"
                      variant="ghost"
                      className="text-red-700 hover:bg-red-50"
                      onClick={() => setPendingDeactivation(ingredient)}
                    >
                      Desactivar
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      variant="ghost"
                      disabled={reactivate.isPending}
                      onClick={() => reactivate.mutate(ingredient.id)}
                    >
                      Reactivar
                    </Button>
                  )}
                </Td>
              </Tr>
            ))}
          </tbody>
        </TableShell>
      )}

      <IngredientFormModal
        open={formOpen}
        ingredient={editing}
        onClose={() => setFormOpen(false)}
      />

      <ConfirmDialog
        open={pendingDeactivation !== null}
        title="Desactivar ingrediente"
        message={`"${pendingDeactivation?.name ?? ''}" dejará de aparecer en los listados, pero las recetas que lo usan conservan la referencia. Puedes reactivarlo después.`}
        confirmLabel="Desactivar"
        pending={deactivate.isPending}
        onCancel={() => setPendingDeactivation(null)}
        onConfirm={() => {
          if (!pendingDeactivation) return
          deactivate.mutate(pendingDeactivation.id, {
            onSettled: () => setPendingDeactivation(null),
          })
        }}
      />
    </>
  )
}
