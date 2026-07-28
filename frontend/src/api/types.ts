import type { components } from './schema'

type Schemas = components['schemas']

export type Ingredient = Schemas['IngredientResponse']
export type IngredientCreate = Schemas['IngredientCreate']
export type IngredientUpdate = Schemas['IngredientUpdate']

export type Recipe = Schemas['RecipeResponse']
export type RecipeCreate = Schemas['RecipeCreate']
export type RecipeUpdate = Schemas['RecipeUpdate']
export type RecipeIngredient = Schemas['RecipeIngredientResponse']

export type Product = Schemas['ProductResponse']
export type ProductCreate = Schemas['ProductCreate']
export type ProductUpdate = Schemas['ProductUpdate']

export type MeasurementUnit = Schemas['MeasurementUnit']
export type IngredientCategory = Schemas['IngredientCategory']
export type ProductCategory = Schemas['ProductCategory']
