import { createRootRoute, createRoute, createRouter, redirect } from '@tanstack/react-router'

import { AppLayout } from '@/components/AppLayout'
import { IngredientsPage } from '@/features/ingredients/IngredientsPage'
import { ProductsPage } from '@/features/products/ProductsPage'
import { RecipesPage } from '@/features/recipes/RecipesPage'

const rootRoute = createRootRoute({ component: AppLayout })

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  beforeLoad: () => {
    throw redirect({ to: '/ingredients' })
  },
})

const ingredientsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/ingredients',
  component: IngredientsPage,
})

const recipesRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/recipes',
  component: RecipesPage,
})

const productsRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/products',
  component: ProductsPage,
})

const routeTree = rootRoute.addChildren([
  indexRoute,
  ingredientsRoute,
  recipesRoute,
  productsRoute,
])

export const router = createRouter({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
