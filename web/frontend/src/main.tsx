import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './styles/globals.css'

// Register Cytoscape layout plugins
import cytoscape from 'cytoscape'
// @ts-expect-error — no type declarations
import coseBilkent from 'cytoscape-cose-bilkent'
cytoscape.use(coseBilkent)

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
