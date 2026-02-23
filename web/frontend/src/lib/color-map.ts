const PALETTE = [
  { bg: '#4f46e5', border: '#6366f1', text: '#c7d2fe' },
  { bg: '#0f766e', border: '#14b8a6', text: '#99f6e4' },
  { bg: '#0369a1', border: '#0ea5e9', text: '#bae6fd' },
  { bg: '#166534', border: '#22c55e', text: '#bbf7d0' },
  { bg: '#b45309', border: '#f59e0b', text: '#fde68a' },
  { bg: '#be123c', border: '#f43f5e', text: '#fecdd3' },
  { bg: '#7c3aed', border: '#a78bfa', text: '#ddd6fe' },
  { bg: '#475569', border: '#94a3b8', text: '#e2e8f0' },
]

const SPECIAL: Record<string, { bg: string; border: string; text: string }> = {
  unknown: { bg: '#334155', border: '#64748b', text: '#cbd5e1' },
}

function hashString(value: string): number {
  let hash = 0
  for (let i = 0; i < value.length; i += 1) {
    hash = (hash * 31 + value.charCodeAt(i)) >>> 0
  }
  return hash
}

export function getLabelColor(label: string): { bg: string; border: string; text: string } {
  if (!label) return SPECIAL.unknown
  const normalized = label.trim().toLowerCase()
  if (SPECIAL[normalized]) return SPECIAL[normalized]
  return PALETTE[hashString(normalized) % PALETTE.length]
}
