import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import App from './App.jsx'
import Algoritmos from './Algoritmos.jsx'
import Analise from './Analise.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/"           element={<App />} />
        <Route path="/algoritmos" element={<Algoritmos />} />
        <Route path="/analise"    element={<Analise />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)
