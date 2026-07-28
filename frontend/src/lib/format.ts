const currency = new Intl.NumberFormat('es-MX', {
  style: 'currency',
  currency: 'MXN',
})

const quantity = new Intl.NumberFormat('es-MX', {
  maximumFractionDigits: 3,
})

const percent = new Intl.NumberFormat('es-MX', {
  style: 'percent',
  maximumFractionDigits: 1,
})

export function formatCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—'
  return currency.format(value)
}

export function formatQuantity(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—'
  return quantity.format(value)
}

export function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined) return '—'
  return percent.format(value)
}

/**
 * Gross margin over the sale price. Returns null when it cannot be computed —
 * `cost` is optional in the API and a product priced at 0 has no meaningful margin.
 */
export function grossMargin(salePrice: number, cost: number | null | undefined): number | null {
  if (cost === null || cost === undefined || salePrice <= 0) return null
  return (salePrice - cost) / salePrice
}
