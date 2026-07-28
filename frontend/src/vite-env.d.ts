/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Base URL of the FastAPI backend. Must be listed in the API's CORS_ORIGINS. */
  readonly VITE_API_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
