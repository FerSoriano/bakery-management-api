import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { api, unwrap } from './client'
import type { Product, ProductCreate, ProductUpdate } from './types'

export const productKeys = {
  all: ['products'] as const,
  list: (includeInactive: boolean) => ['products', 'list', { includeInactive }] as const,
}

export function useProducts(includeInactive = false) {
  return useQuery({
    queryKey: productKeys.list(includeInactive),
    queryFn: () =>
      unwrap(
        api.GET('/api/v1/products/', {
          params: { query: { include_inactive: includeInactive } },
        }),
      ),
  })
}

function useProductInvalidation() {
  const queryClient = useQueryClient()
  return () => {
    void queryClient.invalidateQueries({ queryKey: productKeys.all })
  }
}

export function useCreateProduct() {
  const invalidate = useProductInvalidation()
  return useMutation({
    mutationFn: (product: ProductCreate) => unwrap(api.POST('/api/v1/products/', { body: product })),
    onSuccess: invalidate,
  })
}

export function useUpdateProduct() {
  const invalidate = useProductInvalidation()
  return useMutation({
    mutationFn: ({ id, changes }: { id: Product['id']; changes: ProductUpdate }) =>
      unwrap(
        api.PATCH('/api/v1/products/{product_id}', {
          params: { path: { product_id: id } },
          body: changes,
        }),
      ),
    onSuccess: invalidate,
  })
}

export function useDeactivateProduct() {
  const invalidate = useProductInvalidation()
  return useMutation({
    mutationFn: (id: Product['id']) =>
      unwrap(api.DELETE('/api/v1/products/{product_id}', { params: { path: { product_id: id } } })),
    onSuccess: invalidate,
  })
}

export function useReactivateProduct() {
  const invalidate = useProductInvalidation()
  return useMutation({
    mutationFn: (id: Product['id']) =>
      unwrap(
        api.PATCH('/api/v1/products/{product_id}/reactivate', {
          params: { path: { product_id: id } },
          // Body obligatorio en el contrato pero ignorado en la práctica (exclude_unset).
          body: {},
        }),
      ),
    onSuccess: invalidate,
  })
}
