import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { api, unwrap } from './client'
import { productKeys } from './products'
import type { Ingredient, IngredientCreate, IngredientUpdate } from './types'

export const ingredientKeys = {
  all: ['ingredients'] as const,
  list: (includeInactive: boolean) => ['ingredients', 'list', { includeInactive }] as const,
}

export function useIngredients(includeInactive = false) {
  return useQuery({
    queryKey: ingredientKeys.list(includeInactive),
    queryFn: () =>
      unwrap(
        api.GET('/api/v1/ingredients/', {
          params: { query: { include_inactive: includeInactive } },
        }),
      ),
  })
}

/**
 * Ingredient prices feed `Product.cost` (computed server-side), so any write here
 * can change what the products screen shows. Invalidate both.
 */
function useIngredientInvalidation() {
  const queryClient = useQueryClient()
  return () => {
    void queryClient.invalidateQueries({ queryKey: ingredientKeys.all })
    void queryClient.invalidateQueries({ queryKey: productKeys.all })
  }
}

export function useCreateIngredient() {
  const invalidate = useIngredientInvalidation()
  return useMutation({
    mutationFn: (ingredient: IngredientCreate) =>
      unwrap(api.POST('/api/v1/ingredients/', { body: ingredient })),
    onSuccess: invalidate,
  })
}

export function useUpdateIngredient() {
  const invalidate = useIngredientInvalidation()
  return useMutation({
    mutationFn: ({ id, changes }: { id: Ingredient['id']; changes: IngredientUpdate }) =>
      unwrap(
        api.PATCH('/api/v1/ingredients/{ingredient_id}', {
          params: { path: { ingredient_id: id } },
          body: changes,
        }),
      ),
    onSuccess: invalidate,
  })
}

/** Soft delete: the row stays, `is_active` flips to false. */
export function useDeactivateIngredient() {
  const invalidate = useIngredientInvalidation()
  return useMutation({
    mutationFn: (id: Ingredient['id']) =>
      unwrap(
        api.DELETE('/api/v1/ingredients/{ingredient_id}', {
          params: { path: { ingredient_id: id } },
        }),
      ),
    onSuccess: invalidate,
  })
}

export function useReactivateIngredient() {
  const invalidate = useIngredientInvalidation()
  return useMutation({
    mutationFn: (id: Ingredient['id']) =>
      unwrap(
        api.PATCH('/api/v1/ingredients/{ingredient_id}/reactivate', {
          params: { path: { ingredient_id: id } },
          // El endpoint declara un IngredientUpdate obligatorio que no necesita.
          // Lo lee con exclude_unset=True, así que `{}` solo reactiva.
          body: {},
        }),
      ),
    onSuccess: invalidate,
  })
}
