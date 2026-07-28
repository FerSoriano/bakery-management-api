import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'

import { INGREDIENT_CATEGORIES, INGREDIENT_CATEGORY_LABELS, MEASUREMENT_UNITS, MEASUREMENT_UNIT_LABELS } from '@/api/enums'
import { useCreateIngredient, useUpdateIngredient } from '@/api/ingredients'
import type { Ingredient, IngredientCategory, MeasurementUnit } from '@/api/types'
import { Button } from '@/components/ui/Button'
import { Field, Select, TextInput } from '@/components/ui/Field'
import { Modal } from '@/components/ui/Modal'

type Draft = {
  name: string
  stock_quantity: string
  unit: MeasurementUnit
  category: IngredientCategory
  current_unit_price: string
}

const EMPTY_DRAFT: Draft = {
  name: '',
  stock_quantity: '0',
  unit: 'kg',
  category: 'secos',
  current_unit_price: '',
}

function toDraft(ingredient: Ingredient): Draft {
  return {
    name: ingredient.name,
    stock_quantity: String(ingredient.stock_quantity),
    unit: ingredient.unit,
    category: ingredient.category,
    current_unit_price: String(ingredient.current_unit_price),
  }
}

export function IngredientFormModal({
  open,
  ingredient,
  onClose,
}: {
  open: boolean
  /** `null` opens the modal in create mode. */
  ingredient: Ingredient | null
  onClose: () => void
}) {
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT)
  const createIngredient = useCreateIngredient()
  const updateIngredient = useUpdateIngredient()

  const mutation = ingredient ? updateIngredient : createIngredient

  // Reset the form every time the modal opens so a previous edit never leaks in.
  useEffect(() => {
    if (!open) return
    setDraft(ingredient ? toDraft(ingredient) : EMPTY_DRAFT)
    createIngredient.reset()
    updateIngredient.reset()
    // eslint-disable-next-line react-hooks/exhaustive-deps -- mutations are stable enough; re-running on them would loop
  }, [open, ingredient])

  function handleSubmit(event: FormEvent) {
    event.preventDefault()

    const payload = {
      name: draft.name.trim(),
      stock_quantity: Number(draft.stock_quantity),
      unit: draft.unit,
      category: draft.category,
      current_unit_price: Number(draft.current_unit_price),
    }

    if (ingredient) {
      // `is_active` queda fuera a propósito: editar un ingrediente inactivo no debe
      // reactivarlo. Para eso está el botón "Reactivar".
      updateIngredient.mutate({ id: ingredient.id, changes: payload }, { onSuccess: onClose })
    } else {
      createIngredient.mutate({ ...payload, is_active: true }, { onSuccess: onClose })
    }
  }

  return (
    <Modal
      open={open}
      title={ingredient ? 'Editar ingrediente' : 'Nuevo ingrediente'}
      description={
        ingredient
          ? 'El precio unitario alimenta el costo de las recetas y productos.'
          : 'La materia prima con la que se costean las recetas.'
      }
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose} disabled={mutation.isPending}>
            Cancelar
          </Button>
          <Button
            variant="primary"
            type="submit"
            form="ingredient-form"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? 'Guardando…' : 'Guardar'}
          </Button>
        </>
      }
    >
      <form id="ingredient-form" onSubmit={handleSubmit} className="space-y-4">
        <Field label="Nombre">
          {(controlProps) => (
            <TextInput
              {...controlProps}
              value={draft.name}
              onChange={(event) => setDraft({ ...draft, name: event.target.value })}
              required
              maxLength={100}
              placeholder="Harina de trigo"
            />
          )}
        </Field>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Categoría">
            {(controlProps) => (
              <Select
                {...controlProps}
                value={draft.category}
                onChange={(event) =>
                  setDraft({ ...draft, category: event.target.value as IngredientCategory })
                }
              >
                {INGREDIENT_CATEGORIES.map((category) => (
                  <option key={category} value={category}>
                    {INGREDIENT_CATEGORY_LABELS[category]}
                  </option>
                ))}
              </Select>
            )}
          </Field>

          <Field label="Unidad de medida">
            {(controlProps) => (
              <Select
                {...controlProps}
                value={draft.unit}
                onChange={(event) =>
                  setDraft({ ...draft, unit: event.target.value as MeasurementUnit })
                }
              >
                {MEASUREMENT_UNITS.map((unit) => (
                  <option key={unit} value={unit}>
                    {MEASUREMENT_UNIT_LABELS[unit]}
                  </option>
                ))}
              </Select>
            )}
          </Field>

          <Field label="Stock actual">
            {(controlProps) => (
              <TextInput
                {...controlProps}
                type="number"
                min={0}
                step="0.001"
                value={draft.stock_quantity}
                onChange={(event) => setDraft({ ...draft, stock_quantity: event.target.value })}
                required
              />
            )}
          </Field>

          <Field label="Precio por unidad" hint="Costo de compra de 1 unidad de medida.">
            {(controlProps) => (
              <TextInput
                {...controlProps}
                type="number"
                min={0}
                step="0.01"
                value={draft.current_unit_price}
                onChange={(event) => setDraft({ ...draft, current_unit_price: event.target.value })}
                required
                placeholder="0.00"
              />
            )}
          </Field>
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
