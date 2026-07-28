import { useMemo, useState } from 'react'

import { PRODUCT_CATEGORY_LABELS } from '@/api/enums'
import { useDeactivateProduct, useProducts, useReactivateProduct } from '@/api/products'
import { useRecipes } from '@/api/recipes'
import type { Product } from '@/api/types'
import { InactiveToggle, PageHeader } from '@/components/PageHeader'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { EmptyState, ErrorState, LoadingState } from '@/components/ui/States'
import { TableShell, Td, Th, Tr } from '@/components/ui/Table'
import { formatCurrency, formatPercent, grossMargin } from '@/lib/format'

import { ProductFormModal } from './ProductFormModal'

function MarginBadge({ product }: { product: Product }) {
  const margin = grossMargin(product.sale_price, product.cost)

  if (margin === null) return <span className="text-stone-400">—</span>

  // A negative margin means the product is sold below what it costs to make.
  const tone = margin < 0 ? 'danger' : margin < 0.3 ? 'warning' : 'success'

  return <Badge tone={tone}>{formatPercent(margin)}</Badge>
}

export function ProductsPage() {
  const [includeInactive, setIncludeInactive] = useState(false)
  const [editing, setEditing] = useState<Product | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [pendingDeactivation, setPendingDeactivation] = useState<Product | null>(null)

  const products = useProducts(includeInactive)
  const recipes = useRecipes(true)
  const deactivate = useDeactivateProduct()
  const reactivate = useReactivateProduct()

  const recipeNameById = useMemo(() => {
    const map = new Map<number, string>()
    for (const recipe of recipes.data ?? []) map.set(recipe.id, recipe.name)
    return map
  }, [recipes.data])

  function openCreate() {
    setEditing(null)
    setFormOpen(true)
  }

  return (
    <>
      <PageHeader
        title="Productos"
        description="Catálogo de venta. El costo viene de la receta; el margen se calcula sobre el precio."
        actions={
          <>
            <InactiveToggle checked={includeInactive} onChange={setIncludeInactive} />
            <Button variant="primary" onClick={openCreate}>
              Nuevo producto
            </Button>
          </>
        }
      />

      {products.isPending ? (
        <LoadingState />
      ) : products.isError ? (
        <ErrorState error={products.error} onRetry={() => void products.refetch()} />
      ) : products.data.length === 0 ? (
        <EmptyState
          title="Todavía no hay productos"
          description="Un producto es una receta con precio de venta y categoría."
          action={
            <Button variant="primary" onClick={openCreate}>
              Nuevo producto
            </Button>
          }
        />
      ) : (
        <TableShell>
          <thead>
            <tr>
              <Th>Producto</Th>
              <Th>Categoría</Th>
              <Th>Receta</Th>
              <Th className="text-right">Costo</Th>
              <Th className="text-right">Precio</Th>
              <Th className="text-right">Margen</Th>
              <Th>Estado</Th>
              <Th className="text-right">Acciones</Th>
            </tr>
          </thead>
          <tbody>
            {products.data.map((product) => (
              <Tr key={product.id} muted={!product.is_active}>
                <Td className="font-medium text-stone-900">
                  {product.name}
                  <p className="text-xs font-normal text-stone-500">{product.description}</p>
                </Td>
                <Td>{PRODUCT_CATEGORY_LABELS[product.category]}</Td>
                <Td className="text-stone-500">
                  {recipeNameById.get(product.recipe_id) ?? `#${product.recipe_id}`}
                </Td>
                <Td className="text-right tabular-nums">{formatCurrency(product.cost)}</Td>
                <Td className="text-right tabular-nums">{formatCurrency(product.sale_price)}</Td>
                <Td className="text-right">
                  <MarginBadge product={product} />
                </Td>
                <Td>
                  {product.is_active ? (
                    <Badge tone="success">Activo</Badge>
                  ) : (
                    <Badge tone="neutral">Inactivo</Badge>
                  )}
                </Td>
                <Td className="text-right whitespace-nowrap">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => {
                      setEditing(product)
                      setFormOpen(true)
                    }}
                  >
                    Editar
                  </Button>
                  {product.is_active ? (
                    <Button
                      size="sm"
                      variant="ghost"
                      className="text-red-700 hover:bg-red-50"
                      onClick={() => setPendingDeactivation(product)}
                    >
                      Desactivar
                    </Button>
                  ) : (
                    <Button
                      size="sm"
                      variant="ghost"
                      disabled={reactivate.isPending}
                      onClick={() => reactivate.mutate(product.id)}
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

      <ProductFormModal open={formOpen} product={editing} onClose={() => setFormOpen(false)} />

      <ConfirmDialog
        open={pendingDeactivation !== null}
        title="Desactivar producto"
        message={`"${pendingDeactivation?.name ?? ''}" dejará de aparecer en el catálogo. Puedes reactivarlo después.`}
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
