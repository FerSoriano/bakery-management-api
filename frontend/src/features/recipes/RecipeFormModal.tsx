import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'

import { MEASUREMENT_UNIT_LABELS } from '@/api/enums'
import { useIngredients } from '@/api/ingredients'
import { useCreateRecipe, useUpdateRecipe } from '@/api/recipes'
import type { Recipe } from '@/api/types'
import { Button } from '@/components/ui/Button'
import { Field, Select, TextInput, Textarea } from '@/components/ui/Field'
import { Modal } from '@/components/ui/Modal'
import { formatCurrency } from '@/lib/format'

type IngredientRow = { ingredient_id: string; quantity: string }

type Draft = {
  name: string
  instructions: string
  ingredients: IngredientRow[]
}

const EMPTY_ROW: IngredientRow = { ingredient_id: '', quantity: '' }
const EMPTY_DRAFT: Draft = { name: '', instructions: '', ingredients: [EMPTY_ROW] }

function toDraft(recipe: Recipe): Draft {
  return {
    name: recipe.name,
    instructions: recipe.instructions,
    ingredients: recipe.ingredients.map((item) => ({
      ingredient_id: String(item.ingredient_id),
      quantity: String(item.quantity),
    })),
  }
}

export function RecipeFormModal({
  open,
  recipe,
  onClose,
}: {
  open: boolean
  recipe: Recipe | null
  onClose: () => void
}) {
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT)
  // Inactive ingredients are included: an existing recipe may still reference one,
  // and dropping it from the <select> would silently rewrite the recipe on save.
  const ingredients = useIngredients(true)
  const createRecipe = useCreateRecipe()
  const updateRecipe = useUpdateRecipe()

  const mutation = recipe ? updateRecipe : createRecipe

  useEffect(() => {
    if (!open) return
    setDraft(recipe ? toDraft(recipe) : EMPTY_DRAFT)
    createRecipe.reset()
    updateRecipe.reset()
    // eslint-disable-next-line react-hooks/exhaustive-deps -- resetting only when the modal opens
  }, [open, recipe])

  const priceById = useMemo(() => {
    const map = new Map<number, { price: number; unit: string }>()
    for (const ingredient of ingredients.data ?? []) {
      map.set(ingredient.id, {
        price: ingredient.current_unit_price,
        unit: MEASUREMENT_UNIT_LABELS[ingredient.unit],
      })
    }
    return map
  }, [ingredients.data])

  /**
   * Mirrors what the backend computes server-side (SUM(quantity * unit_price)),
   * so the cost is visible while editing instead of only after saving.
   */
  const estimatedCost = draft.ingredients.reduce((total, row) => {
    const price = priceById.get(Number(row.ingredient_id))?.price
    const quantity = Number(row.quantity)
    if (price === undefined || !Number.isFinite(quantity)) return total
    return total + price * quantity
  }, 0)

  function updateRow(index: number, changes: Partial<IngredientRow>) {
    setDraft((current) => ({
      ...current,
      ingredients: current.ingredients.map((row, i) => (i === index ? { ...row, ...changes } : row)),
    }))
  }

  function addRow() {
    setDraft((current) => ({ ...current, ingredients: [...current.ingredients, EMPTY_ROW] }))
  }

  function removeRow(index: number) {
    setDraft((current) => ({
      ...current,
      ingredients: current.ingredients.filter((_, i) => i !== index),
    }))
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()

    const payload = {
      name: draft.name.trim(),
      instructions: draft.instructions.trim(),
      ingredients: draft.ingredients
        .filter((row) => row.ingredient_id !== '' && row.quantity !== '')
        .map((row) => ({
          ingredient_id: Number(row.ingredient_id),
          quantity: Number(row.quantity),
        })),
    }

    if (recipe) {
      // Sin `is_active`: editar no debe reactivar. Ver IngredientFormModal.
      updateRecipe.mutate({ id: recipe.id, changes: payload }, { onSuccess: onClose })
    } else {
      createRecipe.mutate({ ...payload, is_active: true }, { onSuccess: onClose })
    }
  }

  // The backend has no UNIQUE(recipe_id, ingredient_id) yet, so a duplicate would
  // be accepted and double-count in the cost. Catch it here.
  const chosenIds = draft.ingredients.map((row) => row.ingredient_id).filter(Boolean)
  const hasDuplicates = new Set(chosenIds).size !== chosenIds.length

  return (
    <Modal
      open={open}
      title={recipe ? 'Editar receta' : 'Nueva receta'}
      description="Los ingredientes y sus cantidades determinan el costo del producto."
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose} disabled={mutation.isPending}>
            Cancelar
          </Button>
          <Button
            variant="primary"
            type="submit"
            form="recipe-form"
            disabled={mutation.isPending || hasDuplicates}
          >
            {mutation.isPending ? 'Guardando…' : 'Guardar'}
          </Button>
        </>
      }
    >
      <form id="recipe-form" onSubmit={handleSubmit} className="space-y-4">
        <Field label="Nombre">
          {(controlProps) => (
            <TextInput
              {...controlProps}
              value={draft.name}
              onChange={(event) => setDraft({ ...draft, name: event.target.value })}
              required
              placeholder="Masa de hojaldre"
            />
          )}
        </Field>

        <Field label="Instrucciones">
          {(controlProps) => (
            <Textarea
              {...controlProps}
              rows={3}
              value={draft.instructions}
              onChange={(event) => setDraft({ ...draft, instructions: event.target.value })}
              required
              placeholder="Mezclar en seco, incorporar mantequilla fría…"
            />
          )}
        </Field>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-stone-700">Ingredientes</p>
            <Button size="sm" onClick={addRow}>
              Agregar
            </Button>
          </div>

          {draft.ingredients.length === 0 ? (
            <p className="rounded-lg border border-dashed border-stone-300 px-3 py-4 text-center text-sm text-stone-500">
              Agrega al menos un ingrediente.
            </p>
          ) : (
            <ul className="space-y-2">
              {draft.ingredients.map((row, index) => {
                const selected = priceById.get(Number(row.ingredient_id))
                return (
                  // The index is the identity here: rows are positional and have no id.
                  // eslint-disable-next-line react-x/no-array-index-key
                  <li key={index} className="flex items-start gap-2">
                    <Select
                      aria-label={`Ingrediente ${index + 1}`}
                      value={row.ingredient_id}
                      onChange={(event) => updateRow(index, { ingredient_id: event.target.value })}
                      required
                      className="flex-1"
                    >
                      <option value="">Selecciona un ingrediente…</option>
                      {(ingredients.data ?? []).map((ingredient) => (
                        <option key={ingredient.id} value={ingredient.id}>
                          {ingredient.name}
                          {ingredient.is_active ? '' : ' (inactivo)'}
                        </option>
                      ))}
                    </Select>

                    <div className="w-32 shrink-0">
                      <TextInput
                        aria-label={`Cantidad ${index + 1}`}
                        type="number"
                        min={0}
                        step="0.001"
                        value={row.quantity}
                        onChange={(event) => updateRow(index, { quantity: event.target.value })}
                        required
                        placeholder="0"
                      />
                      {selected ? (
                        <p className="mt-1 text-center text-xs text-stone-500">{selected.unit}</p>
                      ) : null}
                    </div>

                    <Button
                      size="sm"
                      variant="ghost"
                      className="mt-1 text-red-700 hover:bg-red-50"
                      onClick={() => removeRow(index)}
                      aria-label={`Quitar ingrediente ${index + 1}`}
                    >
                      ✕
                    </Button>
                  </li>
                )
              })}
            </ul>
          )}

          {hasDuplicates ? (
            <p className="text-sm text-red-700">
              Hay ingredientes repetidos. Únelos en una sola línea sumando la cantidad.
            </p>
          ) : null}
        </div>

        <div className="flex items-center justify-between rounded-lg bg-stone-50 px-3 py-2.5">
          <span className="text-sm text-stone-600">Costo estimado de la receta</span>
          <span className="text-sm font-semibold tabular-nums text-stone-900">
            {formatCurrency(estimatedCost)}
          </span>
        </div>

        {mutation.isError ? (
          <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {mutation.error.message}
          </p>
        ) : null}
      </form>
    </Modal>
  )
}
