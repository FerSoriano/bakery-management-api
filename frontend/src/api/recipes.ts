import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { api, unwrap } from './client'
import { productKeys } from './products'
import type { Recipe, RecipeCreate, RecipeUpdate } from './types'

export const recipeKeys = {
  all: ['recipes'] as const,
  list: (includeInactive: boolean) => ['recipes', 'list', { includeInactive }] as const,
}

export function useRecipes(includeInactive = false) {
  return useQuery({
    queryKey: recipeKeys.list(includeInactive),
    queryFn: () =>
      unwrap(
        api.GET('/api/v1/recipes/', {
          params: { query: { include_inactive: includeInactive } },
        }),
      ),
  })
}

/** A recipe's ingredient list drives `Product.cost`, so products go stale too. */
function useRecipeInvalidation() {
  const queryClient = useQueryClient()
  return () => {
    void queryClient.invalidateQueries({ queryKey: recipeKeys.all })
    void queryClient.invalidateQueries({ queryKey: productKeys.all })
  }
}

export function useCreateRecipe() {
  const invalidate = useRecipeInvalidation()
  return useMutation({
    mutationFn: (recipe: RecipeCreate) => unwrap(api.POST('/api/v1/recipes/', { body: recipe })),
    onSuccess: invalidate,
  })
}

export function useUpdateRecipe() {
  const invalidate = useRecipeInvalidation()
  return useMutation({
    mutationFn: ({ id, changes }: { id: Recipe['id']; changes: RecipeUpdate }) =>
      unwrap(
        api.PATCH('/api/v1/recipes/{recipe_id}', {
          params: { path: { recipe_id: id } },
          body: changes,
        }),
      ),
    onSuccess: invalidate,
  })
}

export function useDeactivateRecipe() {
  const invalidate = useRecipeInvalidation()
  return useMutation({
    mutationFn: (id: Recipe['id']) =>
      unwrap(api.DELETE('/api/v1/recipes/{recipe_id}', { params: { path: { recipe_id: id } } })),
    onSuccess: invalidate,
  })
}

export function useReactivateRecipe() {
  const invalidate = useRecipeInvalidation()
  return useMutation({
    mutationFn: (id: Recipe['id']) =>
      unwrap(
        api.PATCH('/api/v1/recipes/{recipe_id}/reactivate', {
          params: { path: { recipe_id: id } },
          // Body obligatorio en el contrato pero ignorado en la práctica (exclude_unset).
          body: {},
        }),
      ),
    onSuccess: invalidate,
  })
}
