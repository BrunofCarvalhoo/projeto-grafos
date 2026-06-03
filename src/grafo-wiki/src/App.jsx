import { useEffect, useRef, useState, useCallback, useMemo } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import Nav from './Nav.jsx'

const CORES_GRAU = (grau) => {
  if (grau >= 80) return '#e76f51'
  if (grau >= 40) return '#f4a261'
  if (grau >= 20) return '#2a9d8f'
  return '#264653'
}

const MIN_ARESTAS = 200

export default function App() {
  const [dadosCompletos, setDadosCompletos] = useState({ nodes: [], links: [] })
  const [limiteArestas, setLimiteArestas]   = useState(MIN_ARESTAS)
  const [nodeSelecionado, setNode]          = useState(null)
  const [busca, setBusca]                   = useState('')
  const [status, setStatus]                 = useState('Carregando dados...')
  const [simulando, setSimulando]           = useState(false)
  const fgRef = useRef()

  // ── Carrega JSON e ordena arestas pelos endpoints mais conectados ─
  useEffect(() => {
    setStatus('Carregando dados...')
    fetch('/grafo_data.json')
      .then(r => r.json())
      .then(data => {
        // Mapa id → grau para ordenar arestas
        const grauPorId = Object.fromEntries(data.nodes.map(n => [n.id, n.grau]))
        const nodesPorId = Object.fromEntries(data.nodes.map(n => [n.id, n]))

        // Ordena arestas pela "importância" = soma do grau dos dois lados.
        // Assim, as primeiras N arestas conectam os hubs mais relevantes.
        const linksOrdenados = [...data.links].sort((a, b) => {
          const sa = typeof a.source === 'object' ? a.source.id : a.source
          const ta = typeof a.target === 'object' ? a.target.id : a.target
          const sb = typeof b.source === 'object' ? b.source.id : b.source
          const tb = typeof b.target === 'object' ? b.target.id : b.target
          const pesoB = (grauPorId[sb] || 0) + (grauPorId[tb] || 0)
          const pesoA = (grauPorId[sa] || 0) + (grauPorId[ta] || 0)
          return pesoB - pesoA
        })

        setDadosCompletos({ nodes: data.nodes, links: linksOrdenados, nodesPorId })
        setStatus('')
      })
  }, [])

  // ── Filtra grafo segundo o limite de arestas escolhido ─────────
  const grafoData = useMemo(() => {
    if (dadosCompletos.links.length === 0) return { nodes: [], links: [] }

    const linksVisiveis = dadosCompletos.links.slice(0, limiteArestas)

    // Coleta apenas os nós que participam dessas arestas
    const idsUsados = new Set()
    for (const l of linksVisiveis) {
      const s = typeof l.source === 'object' ? l.source.id : l.source
      const t = typeof l.target === 'object' ? l.target.id : l.target
      idsUsados.add(s)
      idsUsados.add(t)
    }
    const nodesVisiveis = dadosCompletos.nodes.filter(n => idsUsados.has(n.id))

    return { nodes: nodesVisiveis, links: linksVisiveis }
  }, [dadosCompletos, limiteArestas])

  // Reinicia simulação quando o limite muda
  useEffect(() => {
    if (grafoData.nodes.length > 0) setSimulando(true)
  }, [limiteArestas])

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
    else alert(`"${busca}" não encontrado (talvez esteja fora do filtro atual).`)
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

  const largura     = window.innerWidth
  const altura      = window.innerHeight
  const totalNos    = dadosCompletos.nodes.length
  const totalLinks  = dadosCompletos.links.length

  return (
    <div style={{ position: 'relative', width: largura, height: altura }}>
      <Nav />

      {/* ── Cabeçalho ── */}
      <div style={estilos.cabecalho}>
        <span style={estilos.titulo}>Grafo Wikipedia</span>
        {grafoData.links.length > 0 && (
          <span style={estilos.stats}>
            {grafoData.links.length.toLocaleString()} de {totalLinks.toLocaleString()} arestas
            · {grafoData.nodes.length.toLocaleString()} vértices
            {simulando && ' · calculando layout...'}
          </span>
        )}
      </div>

      {/* ── Filtro de quantidade de arestas ── */}
      {totalLinks > 0 && (
        <div style={estilos.filtro}>
          <p style={{ fontSize: 11, color: '#aaa', marginBottom: 6, fontWeight: 600 }}>
            Arestas exibidas (mais relevantes primeiro)
          </p>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <input
              type="range"
              min={MIN_ARESTAS}
              max={totalLinks}
              step={100}
              value={limiteArestas}
              onChange={e => setLimiteArestas(Number(e.target.value))}
              style={estilos.slider}
            />
            <span style={estilos.contador}>
              {limiteArestas.toLocaleString()}
            </span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4 }}>
            <span style={{ fontSize: 10, color: '#555' }}>{MIN_ARESTAS}</span>
            <button
              style={estilos.botaoTudo}
              onClick={() => setLimiteArestas(totalLinks)}
            >
              ver tudo ({totalLinks.toLocaleString()})
            </button>
          </div>
        </div>
      )}

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

          warmupTicks={60}
          cooldownTicks={200}
          d3AlphaDecay={0.03}
          d3VelocityDecay={0.4}
          onEngineStop={() => setSimulando(false)}

          nodeRelSize={2}
          nodeVal={n => Math.max(1, n.grau / 15)}
          nodeColor={n => CORES_GRAU(n.grau)}
          nodeLabel={n => `${n.id}  (grau: ${n.grau})`}
          onNodeClick={aoClicarNo}

          linkColor={() => 'rgba(42,58,74,0.6)'}
          linkWidth={0.4}
          linkDirectionalArrowLength={2}
          linkDirectionalArrowRelPos={1}

          nodeCanvasObjectMode={n => n.grau >= 30 ? 'after' : undefined}
          nodeCanvasObject={(node, ctx, globalScale) => {
            if (globalScale < 1.5) return
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
    position: 'absolute', top: 64, left: '50%', transform: 'translateX(-50%)',
    zIndex: 10, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2,
    pointerEvents: 'none',
  },
  titulo: { fontSize: 18, fontWeight: 700, color: '#e0e0e0' },
  stats:  { fontSize: 12, color: '#888' },

  filtro: {
    position: 'absolute', top: 64, left: 16, zIndex: 10, width: 260,
    background: 'rgba(15,17,23,0.92)', padding: '12px 14px',
    borderRadius: 8, border: '1px solid #2a3a4a',
  },
  slider: {
    flex: 1, accentColor: '#2a9d8f', cursor: 'pointer',
  },
  contador: {
    minWidth: 48, textAlign: 'right',
    fontSize: 13, fontWeight: 700, color: '#2a9d8f',
  },
  botaoTudo: {
    background: 'none', border: 'none', color: '#2a9d8f',
    cursor: 'pointer', fontSize: 10, padding: 0,
    textDecoration: 'underline',
  },

  barraBusca: {
    position: 'absolute', top: 64, right: 16, zIndex: 10,
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
    position: 'absolute', top: 170, left: 16, zIndex: 10, width: 260,
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
