import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'

import { PRODUCT_CATEGORIES, PRODUCT_CATEGORY_LABELS } from '@/api/enums'
import { useCreateProduct, useUpdateProduct } from '@/api/products'
import { useRecipes } from '@/api/recipes'
import type { Product, ProductCategory } from '@/api/types'
import { Button } from '@/components/ui/Button'
import { Field, Select, TextInput, Textarea } from '@/components/ui/Field'
import { Modal } from '@/components/ui/Modal'

type Draft = {
  name: string
  description: string
  sale_price: string
  category: ProductCategory
  recipe_id: string
}

const EMPTY_DRAFT: Draft = {
  name: '',
  description: '',
  sale_price: '',
  category: 'Pasteles',
  recipe_id: '',
}

function toDraft(product: Product): Draft {
  return {
    name: product.name,
    description: product.description,
    sale_price: String(product.sale_price),
    category: product.category,
    recipe_id: String(product.recipe_id),
  }
}

export function ProductFormModal({
  open,
  product,
  onClose,
}: {
  open: boolean
  product: Product | null
  onClose: () => void
}) {
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT)
  // Same reasoning as the recipe form: keep inactive recipes selectable so editing
  // a product that points at one does not silently repoint it.
  const recipes = useRecipes(true)
  const createProduct = useCreateProduct()
  const updateProduct = useUpdateProduct()

  const mutation = product ? updateProduct : createProduct

  useEffect(() => {
    if (!open) return
    setDraft(product ? toDraft(product) : EMPTY_DRAFT)
    createProduct.reset()
    updateProduct.reset()
    // eslint-disable-next-line react-hooks/exhaustive-deps -- resetting only when the modal opens
  }, [open, product])

  function handleSubmit(event: FormEvent) {
    event.preventDefault()

    const payload = {
      name: draft.name.trim(),
      description: draft.description.trim(),
      sale_price: Number(draft.sale_price),
      category: draft.category,
      recipe_id: Number(draft.recipe_id),
    }

    if (product) {
      // Sin `is_active`: editar no debe reactivar. Ver IngredientFormModal.
      updateProduct.mutate({ id: product.id, changes: payload }, { onSuccess: onClose })
    } else {
      createProduct.mutate({ ...payload, is_active: true }, { onSuccess: onClose })
    }
  }

  const noRecipes = !recipes.isPending && (recipes.data ?? []).length === 0

  return (
    <Modal
      open={open}
      title={product ? 'Editar producto' : 'Nuevo producto'}
      description="Producto terminado. Su costo se calcula desde la receta asociada."
      onClose={onClose}
      footer={
        <>
          <Button onClick={onClose} disabled={mutation.isPending}>
            Cancelar
          </Button>
          <Button
            variant="primary"
            type="submit"
            form="product-form"
            disabled={mutation.isPending || noRecipes}
          >
            {mutation.isPending ? 'Guardando…' : 'Guardar'}
          </Button>
        </>
      }
    >
      <form id="product-form" onSubmit={handleSubmit} className="space-y-4">
        {noRecipes ? (
          <p className="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">
            Un producto necesita una receta. Crea primero una receta.
          </p>
        ) : null}

        <Field label="Nombre">
          {(controlProps) => (
            <TextInput
              {...controlProps}
              value={draft.name}
              onChange={(event) => setDraft({ ...draft, name: event.target.value })}
              required
              placeholder="Pastel de chocolate"
            />
          )}
        </Field>

        <Field label="Descripción">
          {(controlProps) => (
            <Textarea
              {...controlProps}
              rows={2}
              value={draft.description}
              onChange={(event) => setDraft({ ...draft, description: event.target.value })}
              required
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
                  setDraft({ ...draft, category: event.target.value as ProductCategory })
                }
              >
                {PRODUCT_CATEGORIES.map((category) => (
                  <option key={category} value={category}>
                    {PRODUCT_CATEGORY_LABELS[category]}
                  </option>
                ))}
              </Select>
            )}
          </Field>

          <Field label="Precio de venta">
            {(controlProps) => (
              <TextInput
                {...controlProps}
                type="number"
                min={0}
                step="0.01"
                value={draft.sale_price}
                onChange={(event) => setDraft({ ...draft, sale_price: event.target.value })}
                required
                placeholder="0.00"
              />
            )}
          </Field>
        </div>

        <Field label="Receta" hint="Define el costo del producto a partir de sus ingredientes.">
          {(controlProps) => (
            <Select
              {...controlProps}
              value={draft.recipe_id}
              onChange={(event) => setDraft({ ...draft, recipe_id: event.target.value })}
              required
              disabled={recipes.isPending}
            >
              <option value="">Selecciona una receta…</option>
              {(recipes.data ?? []).map((recipe) => (
                <option key={recipe.id} value={recipe.id}>
                  {recipe.name}
                  {recipe.is_active ? '' : ' (inactiva)'}
                </option>
              ))}
            </Select>
          )}
        </Field>

        {mutation.isError ? (
          <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">
            {mutation.error.message}
          </p>
        ) : null}
      </form>
    </Modal>
  )
}
