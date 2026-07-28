import { useState } from 'react'

import { useDeactivateRecipe, useReactivateRecipe, useRecipes } from '@/api/recipes'
import type { Recipe } from '@/api/types'
import { InactiveToggle, PageHeader } from '@/components/PageHeader'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/States'
import { TableShell, Td, Th, Tr } from '@/components/ui/Table'
import { formatQuantity } from '@/lib/format'

import { RecipeFormModal } from './RecipeFormModal'

function IngredientList({ recipe }: { recipe: Recipe }) {
  if (recipe.ingredients.length === 0) {
    return <span className="text-stone-400">Sin ingredientes</span>
  }

  return (
    <ul className="space-y-0.5">
      {recipe.ingredients.map((item) => (
        <li key={item.ingredient_id} className="text-stone-600">
          <span className="tabular-nums">{formatQuantity(item.quantity)}</span>{' '}
          <span className="text-stone-400">{item.ingredient_unit}</span> · {item.ingredient_name}
        </li>
      ))}
    </ul>
  )
}

export function RecipesPage() {
  const [includeInactive, setIncludeInactive] = useState(false)
  const [editing, setEditing] = useState<Recipe | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [pendingDeactivation, setPendingDeactivation] = useState<Recipe | null>(null)
  const [expanded, setExpanded] = useState<number | null>(null)

  const recipes = useRecipes(includeInactive)
  const deactivate = useDeactivateRecipe()
  const reactivate = useReactivateRecipe()

  function openCreate() {
    setEditing(null)
    setFormOpen(true)
  }

  return (
    <>
      <PageHeader
        title="Recetas"
        description="Qué lleva cada preparación y en qué cantidad."
        actions={
          <>
            <InactiveToggle checked={includeInactive} onChange={setIncludeInactive} />
            <Button variant="primary" onClick={openCreate}>
              Nueva receta
            </Button>
          </>
        }
      />

      {recipes.isPending ? (
        <LoadingState />
      ) : recipes.isError ? (
        <ErrorState error={recipes.error} onRetry={() => void recipes.refetch()} />
      ) : recipes.data.length === 0 ? (
        <EmptyState
          title="Todavía no hay recetas"
          description="Una receta agrupa ingredientes y cantidades; es lo que da costo a un producto."
          action={
            <Button variant="primary" onClick={openCreate}>
              Nueva receta
            </Button>
          }
        />
      ) : (
        <TableShell>
          <thead>
            <tr>
              <Th>Nombre</Th>
              <Th className="text-right">Ingredientes</Th>
              <Th>Estado</Th>
              <Th className="text-right">Acciones</Th>
            </tr>
          </thead>
          <tbody>
            {recipes.data.map((recipe) => (
              <Tr key={recipe.id} muted={!recipe.is_active}>
                <Td className="font-medium text-stone-900">
                  <button
                    type="button"
                    onClick={() => setExpanded(expanded === recipe.id ? null : recipe.id)}
                    className="text-left hover:text-amber-800"
                    aria-expanded={expanded === recipe.id}
                  >
                    {recipe.name}
                    <span aria-hidden className="ml-1.5 text-xs text-stone-400">
                      {expanded === recipe.id ? '▾' : '▸'}
                    </span>
                  </button>

                  {expanded === recipe.id ? (
                    <div className="mt-3 space-y-3 border-l-2 border-stone-200 pl-3 text-sm font-normal">
                      <IngredientList recipe={recipe} />
                      <p className="whitespace-pre-line text-stone-500">{recipe.instructions}</p>
                    </div>
                  ) : null}
                </Td>
                <Td className="text-right align-top tabular-nums">{recipe.ingredients.length}</Td>
                <Td className="align-top">
                  {recipe.is_active ? (
                    <Badge tone="success">Activa</Badge>
                  ) : (
                    <Badge tone="neutral">Inactiva</Badge>
                  )}
                </Td>
                <Td className="text-right align-top whitespace-nowrap">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => {
                      setEditing(recipe)
                      setFormOpen(true)
                    }}
                  >
                    Editar
                  </Button>
                  {recipe.is_active ? (
                    <Button
                      size="sm"
                      variant="ghost"
                      className="text-red-700 hover:bg-red-50"
                      onClick={() => setPendingDeactivation(recipe)}
                    >
                      Desactivar
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      variant="ghost"
                      disabled={reactivate.isPending}
                      onClick={() => reactivate.mutate(recipe.id)}
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

      <RecipeFormModal open={formOpen} recipe={editing} onClose={() => setFormOpen(false)} />

      <ConfirmDialog
        open={pendingDeactivation !== null}
        title="Desactivar receta"
        message={`"${pendingDeactivation?.name ?? ''}" dejará de aparecer en los listados. Los productos que la usan seguirán apuntando a ella.`}
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
