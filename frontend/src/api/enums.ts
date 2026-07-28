import type { IngredientCategory, MeasurementUnit, ProductCategory } from './types'

/**
 * Display labels for the API enums.
 *
 * These are typed as `Record<Enum, string>` on purpose: the generated schema is
 * the source of truth, so if the backend adds, removes or renames a member, the
 * regenerated types break *here* — one file — instead of silently rendering a
 * blank cell somewhere. Never widen these to `Record<string, string>`.
 */
export const MEASUREMENT_UNIT_LABELS: Record<MeasurementUnit, string> = {
  kg: 'kg',
  g: 'g',
  l: 'L',
  ml: 'mL',
  pza: 'pza',
  caja: 'caja',
}

export const INGREDIENT_CATEGORY_LABELS: Record<IngredientCategory, string> = {
  lacteos: 'Lácteos',
  secos: 'Secos',
  liquidos: 'Líquidos',
  frutas_verduras: 'Frutas y verduras',
  especias: 'Especias',
}

export const PRODUCT_CATEGORY_LABELS: Record<ProductCategory, string> = {
  Pasteles: 'Pasteles',
  Rebanadas: 'Rebanadas',
  // TODO(backend): el valor del enum tiene un typo — "Postes" debería ser "Postres"
  // (app/schemas/product.py:6). Al arreglarlo y regenerar, esta clave dará error de tipo.
  'Postes Individuales': 'Postres individuales',
  Bebidas: 'Bebidas',
  Otros: 'Otros',
}

/** Enum members in the order the backend declares them, for <select> options. */
export const MEASUREMENT_UNITS = Object.keys(MEASUREMENT_UNIT_LABELS) as MeasurementUnit[]
export const INGREDIENT_CATEGORIES = Object.keys(INGREDIENT_CATEGORY_LABELS) as IngredientCategory[]
export const PRODUCT_CATEGORIES = Object.keys(PRODUCT_CATEGORY_LABELS) as ProductCategory[]
