import '@testing-library/jest-dom/vitest'

// jsdom doesn't implement ResizeObserver (used by Recharts' ResponsiveContainer).
// Real browsers always have it; this is a test-environment-only polyfill.
if (typeof globalThis.ResizeObserver === 'undefined') {
  globalThis.ResizeObserver = class ResizeObserver {
    observe() {}
    unobserve() {}
    disconnect() {}
  }
}
