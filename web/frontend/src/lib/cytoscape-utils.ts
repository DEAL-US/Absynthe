import type { Stylesheet } from 'cytoscape'

export const LAYOUTS = {
  grid: { name: 'grid', fit: true, padding: 24, animate: false },
  circle: { name: 'circle', fit: true, padding: 24, animate: false },
  concentric: { name: 'concentric', fit: true, padding: 24, animate: false },
  breadthfirst: { name: 'breadthfirst', fit: true, directed: false, padding: 24, animate: false },
  cose: { name: 'cose', fit: true, padding: 24, animate: false },
  'cose-bilkent': { name: 'cose-bilkent', fit: true, padding: 24, animate: false },
} as const

export type LayoutName = keyof typeof LAYOUTS

export const BASE_STYLESHEET: Stylesheet[] = [
  {
    selector: 'node',
    style: {
      label: 'data(id)',
      color: '#d1d5db',
      'font-size': 10,
      'text-valign': 'center',
      'text-halign': 'center',
      'background-color': '#334155',
      'border-color': '#475569',
      'border-width': 2,
      width: 24,
      height: 24,
      'overlay-opacity': 0,
    },
  },
  {
    selector: 'edge',
    style: {
      width: 2,
      'line-color': '#475569',
      'curve-style': 'bezier',
      'target-arrow-shape': 'none',
      opacity: 0.9,
      'overlay-opacity': 0,
    },
  },
  {
    selector: 'node.removed',
    style: {
      'background-color': '#ef4444',
      'border-color': '#fca5a5',
      opacity: 0.35,
    },
  },
  {
    selector: 'node.changed',
    style: {
      'background-color': '#f59e0b',
      'border-color': '#fcd34d',
      'border-width': 3,
    },
  },
  {
    selector: 'edge.removed',
    style: {
      'line-color': '#ef4444',
      'line-style': 'dashed',
      opacity: 0.75,
    },
  },
  {
    selector: 'edge.added',
    style: {
      'line-color': '#22c55e',
      'line-style': 'dashed',
      opacity: 0.9,
    },
  },
]
