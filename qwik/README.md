# Qwik Template

A minimal [Qwik](https://qwik.dev) project template for building modern web applications.

## Purpose

This template serves as a starting point for Qwik projects. It includes a preconfigured setup with:
- **Qwik** — resumable framework for instant-loading web apps
- **Vite** — fast build tool and dev server
- **Tailwind CSS v4** — utility-first styling
- **TypeScript** — type-safe development

## Project Structure

```
qwik/
└── apps/
    └── web/
        ├── src/
        │   ├── component/      # Reusable UI components
        │   │   ├── header.tsx
        │   │   ├── footer.tsx
        │   │   └── menu.tsx
        │   ├── route/          # Page routes
        │   │   ├── index.tsx   # Home page
        │   │   └── layout.tsx  # Root layout
        │   ├── style/          # Global styles
        │   ├── entry.csr.tsx   # Client entry
        │   ├── entry.ssr.tsx   # SSR entry
        │   └── root.tsx        # App root
        ├── package.json
        ├── vite.config.ts
        └── tailwind.config.ts
```

## Setup

```bash
cd apps/web
bun install
```

## Development

Start the dev server with SSR:

```bash
bun run dev
```

## Build

Build for production:

```bash
bun run build
```

## Type Check

Run TypeScript type checking:

```bash
bun run chk
```
