import { NavLink } from 'react-router-dom'

export default function Nav() {
  const base = {
    padding: '8px 20px',
    borderRadius: 6,
    textDecoration: 'none',
    fontSize: 14,
    fontWeight: 500,
    transition: 'background 0.15s',
    color: '#a0b0c0',
  }
  const ativo = { ...base, background: '#1e2d3d', color: '#e0e0e0' }

  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100,
      background: 'rgba(10,12,18,0.95)',
      backdropFilter: 'blur(8px)',
      borderBottom: '1px solid #1e2d3d',
      display: 'flex', alignItems: 'center', gap: 4,
      padding: '10px 20px',
    }}>
      <span style={{ color: '#e0e0e0', fontWeight: 700, marginRight: 16, fontSize: 15 }}>
        Grafo Wikipedia
      </span>
      <NavLink to="/"           style={({ isActive }) => isActive ? ativo : base}>Visualização</NavLink>
      <NavLink to="/algoritmos" style={({ isActive }) => isActive ? ativo : base}>Algoritmos</NavLink>
      <NavLink to="/analise"    style={({ isActive }) => isActive ? ativo : base}>Análises</NavLink>
    </nav>
  )
}
