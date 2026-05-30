import { useEffect, useRef, useState, useCallback } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import Nav from './Nav.jsx'

const CORES_GRAU = (grau) => {
  if (grau >= 80) return '#e76f51'
  if (grau >= 40) return '#f4a261'
  if (grau >= 20) return '#2a9d8f'
  return '#264653'
}

export default function App() {
  const [grafoData, setGrafoData]   = useState({ nodes: [], links: [] })
  const [nodeSelecionado, setNode]  = useState(null)
  const [busca, setBusca]           = useState('')
  const [status, setStatus]         = useState('Carregando dados...')
  const [simulando, setSimulando]   = useState(false)
  const fgRef = useRef()

  // ── Carrega JSON ────────────────────────────────────────────────
  useEffect(() => {
    setStatus('Carregando dados...')
    fetch('/grafo_data.json')
      .then(r => r.json())
      .then(data => {
        setStatus(`Calculando layout — ${data.nodes.length.toLocaleString()} nós, ${data.links.length.toLocaleString()} arestas...`)
        setSimulando(true)
        setGrafoData(data)
      })
  }, [])

  // ── Clique em nó ────────────────────────────────────────────────
  const aoClicarNo = useCallback(node => {
    setNode(node)
    fgRef.current?.centerAt(node.x, node.y, 600)
    fgRef.current?.zoom(6, 600)
  }, [])

  // ── Busca ────────────────────────────────────────────────────────
  const aoFocarBusca = () => {
    const termo = busca.trim().toLowerCase()
    if (!termo) return
    const encontrado = grafoData.nodes.find(n =>
      n.id.toLowerCase().includes(termo)
    )
    if (encontrado) aoClicarNo(encontrado)
    else alert(`"${busca}" não encontrado.`)
  }

  // ── Vizinhos do nó selecionado ───────────────────────────────────
  const vizinhos = nodeSelecionado
    ? grafoData.links
        .filter(l => {
          const s = typeof l.source === 'object' ? l.source.id : l.source
          const t = typeof l.target === 'object' ? l.target.id : l.target
          return s === nodeSelecionado.id || t === nodeSelecionado.id
        })
        .map(l => {
          const s = typeof l.source === 'object' ? l.source.id : l.source
          const t = typeof l.target === 'object' ? l.target.id : l.target
          return s === nodeSelecionado.id ? t : s
        })
    : []

  const largura = window.innerWidth
  const altura  = window.innerHeight

  return (
    <div style={{ position: 'relative', width: largura, height: altura }}>
      <Nav />

      {/* ── Cabeçalho ── */}
      <div style={estilos.cabecalho}>
        <span style={estilos.titulo}>Grafo Wikipedia</span>
        {grafoData.nodes.length > 0 && (
          <span style={estilos.stats}>
            {grafoData.nodes.length.toLocaleString()} vértices
            · {grafoData.links.length.toLocaleString()} arestas
            {simulando && ' · calculando layout...'}
          </span>
        )}
      </div>

      {/* ── Barra de busca ── */}
      <div style={estilos.barraBusca}>
        <input
          style={estilos.input}
          placeholder="Buscar página..."
          value={busca}
          onChange={e => setBusca(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && aoFocarBusca()}
        />
        <button style={estilos.botao} onClick={aoFocarBusca}>Ir</button>
        {nodeSelecionado && (
          <button
            style={{ ...estilos.botao, background: '#555' }}
            onClick={() => {
              setNode(null)
              fgRef.current?.zoom(1, 600)
            }}
          >
            Ver tudo
          </button>
        )}
      </div>

      {/* ── Legenda ── */}
      <div style={estilos.legenda}>
        <p style={{ marginBottom: 6, fontWeight: 600, fontSize: 12 }}>Grau de conexão</p>
        {[
          ['#e76f51', '≥ 80  (hub)'],
          ['#f4a261', '≥ 40'],
          ['#2a9d8f', '≥ 20'],
          ['#264653', '< 20'],
        ].map(([cor, label]) => (
          <div key={cor} style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 3 }}>
            <div style={{ width: 10, height: 10, borderRadius: '50%', background: cor, flexShrink: 0 }} />
            <span style={{ fontSize: 11 }}>{label}</span>
          </div>
        ))}
        <p style={{ marginTop: 8, fontSize: 10, color: '#666' }}>
          Scroll → zoom · arraste → mover<br />
          Clique num nó → detalhes
        </p>
      </div>

      {/* ── Painel do nó selecionado ── */}
      {nodeSelecionado && (
        <div style={estilos.painel}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <strong style={{ fontSize: 13, lineHeight: 1.4, flex: 1, marginRight: 8 }}>
              {nodeSelecionado.id}
            </strong>
            <button
              style={estilos.fechar}
              onClick={() => { setNode(null); fgRef.current?.zoom(1, 600) }}
            >✕</button>
          </div>
          <hr style={{ borderColor: '#333', margin: '8px 0' }} />
          <p style={{ fontSize: 12 }}>Grau: <strong>{nodeSelecionado.grau}</strong></p>
          <p style={{ fontSize: 12, marginTop: 4 }}>
            Vizinhos visíveis: <strong>{vizinhos.length}</strong>
          </p>
          {vizinhos.length > 0 && (
            <div style={{ marginTop: 8, maxHeight: 200, overflowY: 'auto' }}>
              {vizinhos.slice(0, 100).map(v => (
                <div
                  key={v}
                  style={estilos.vizinho}
                  onClick={() => {
                    const no = grafoData.nodes.find(n => n.id === v)
                    if (no) aoClicarNo(no)
                  }}
                >
                  {v}
                </div>
              ))}
              {vizinhos.length > 100 && (
                <p style={{ fontSize: 10, color: '#666', marginTop: 4 }}>
                  + {vizinhos.length - 100} mais...
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── Status / loading ── */}
      {(grafoData.nodes.length === 0) && (
        <div style={estilos.loading}>{status}</div>
      )}

      {/* ── Grafo ── */}
      {grafoData.nodes.length > 0 && (
        <ForceGraph2D
          ref={fgRef}
          graphData={grafoData}
          width={largura}
          height={altura}
          backgroundColor="#0f1117"

          // ── Otimizações de performance para grafos grandes ──
          warmupTicks={60}           // roda 60 ticks de física antes de renderizar
          cooldownTicks={200}        // para a simulação após 200 ticks
          d3AlphaDecay={0.03}        // convergência mais rápida (padrão: 0.0228)
          d3VelocityDecay={0.4}      // amortecimento maior → menos oscilação
          onEngineStop={() => setSimulando(false)}

          // ── Nós ──
          nodeRelSize={2}            // nós menores para caber mais na tela
          nodeVal={n => Math.max(1, n.grau / 15)}
          nodeColor={n => CORES_GRAU(n.grau)}
          nodeLabel={n => `${n.id}  (grau: ${n.grau})`}
          onNodeClick={aoClicarNo}

          // ── Arestas ──
          linkColor={() => 'rgba(42,58,74,0.6)'}
          linkWidth={0.4}
          linkDirectionalArrowLength={2}
          linkDirectionalArrowRelPos={1}

          // ── Labels: só mostra quando der zoom suficiente ──
          nodeCanvasObjectMode={n => n.grau >= 30 ? 'after' : undefined}
          nodeCanvasObject={(node, ctx, globalScale) => {
            if (globalScale < 1.5) return   // não renderiza labels em zoom baixo
            const label    = node.id.length > 25 ? node.id.slice(0, 25) + '…' : node.id
            const fontSize = Math.max(6, 10 / globalScale)
            ctx.font       = `${fontSize}px Segoe UI`
            ctx.fillStyle  = 'rgba(224,224,224,0.9)'
            ctx.textAlign  = 'center'
            ctx.fillText(label, node.x, node.y + Math.max(1, node.grau / 15) + fontSize + 1)
          }}
        />
      )}
    </div>
  )
}

const estilos = {
  cabecalho: {
    position: 'absolute', top: 16, left: '50%', transform: 'translateX(-50%)',
    zIndex: 10, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2,
    pointerEvents: 'none',
  },
  titulo: { fontSize: 18, fontWeight: 700, color: '#e0e0e0' },
  stats:  { fontSize: 12, color: '#888' },
  barraBusca: {
    position: 'absolute', top: 16, right: 16, zIndex: 10,
    display: 'flex', gap: 6,
  },
  input: {
    padding: '6px 10px', borderRadius: 6, border: '1px solid #333',
    background: '#1a1f2e', color: '#e0e0e0', fontSize: 13, width: 200,
    outline: 'none',
  },
  botao: {
    padding: '6px 12px', borderRadius: 6, border: 'none',
    background: '#2a9d8f', color: '#fff', cursor: 'pointer', fontSize: 13,
  },
  legenda: {
    position: 'absolute', bottom: 24, left: 16, zIndex: 10,
    background: 'rgba(15,17,23,0.85)', padding: '10px 14px',
    borderRadius: 8, border: '1px solid #2a3a4a',
  },
  painel: {
    position: 'absolute', top: 60, left: 16, zIndex: 10, width: 240,
    background: 'rgba(15,17,23,0.92)', padding: '12px 14px',
    borderRadius: 8, border: '1px solid #2a3a4a',
  },
  fechar: {
    background: 'none', border: 'none', color: '#888',
    cursor: 'pointer', fontSize: 14, padding: 0,
  },
  vizinho: {
    fontSize: 11, padding: '4px 6px', marginBottom: 2,
    background: '#1a2535', borderRadius: 4, cursor: 'pointer',
    color: '#a0c4d8', overflow: 'hidden', textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  loading: {
    position: 'absolute', top: '50%', left: '50%',
    transform: 'translate(-50%, -50%)',
    color: '#888', fontSize: 16,
  },
}
