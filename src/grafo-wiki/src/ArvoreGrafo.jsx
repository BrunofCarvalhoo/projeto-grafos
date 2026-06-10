import { useMemo, useRef, useState, useEffect } from 'react'
import ForceGraph2D from 'react-force-graph-2d'

export default function ArvoreGrafo({ origem, arestasArvore, profundidadeMax, corAlgoritmo }) {
  const [profLimite, setProfLimite] = useState(
    Math.min(2, profundidadeMax || 2)
  )
  const fgRef = useRef()

  const grafoTree = useMemo(() => {
    const arestasFiltradas = arestasArvore.filter(a => a.nivel <= profLimite)
    const idsUsados = new Set([origem])
    for (const a of arestasFiltradas) {
      idsUsados.add(a.pai)
      idsUsados.add(a.filho)
    }

    const nivelPorNo = { [origem]: 0 }
    for (const a of arestasFiltradas) {
      nivelPorNo[a.filho] = a.nivel
    }

    const nodes = [...idsUsados].map(id => ({
      id,
      nivel: nivelPorNo[id] ?? 0,
      ehOrigem: id === origem,
    }))

    const links = arestasFiltradas.map(a => ({
      source: a.pai,
      target: a.filho,
      peso:   a.peso,
    }))

    return { nodes, links }
  }, [arestasArvore, profLimite, origem])

  // ── Espaça os nós: aumenta repulsão e distância das arestas ──
  useEffect(() => {
    if (!fgRef.current) return
    const fg = fgRef.current
    fg.d3Force('charge')?.strength(-180)
    fg.d3Force('link')?.distance(60)
    fg.d3ReheatSimulation()
  }, [grafoTree])

  const corPorNivel = (nivel, ehOrigem) => {
    if (ehOrigem) return '#4ae080'
    const cores = ['#c9a227', '#f4a261', '#e76f51', '#a05a3d', '#5a3a2a']
    return cores[Math.min(nivel - 1, cores.length - 1)]
  }

  const muitosNos = grafoTree.nodes.length > 1500

  return (
    <div>
      {/* Controles */}
      <div style={s.controles}>
        <div>
          <p style={s.label}>
            Profundidade máxima exibida
            <span style={s.contador}>{profLimite} / {profundidadeMax}</span>
          </p>
          <input
            type="range"
            min={1}
            max={profundidadeMax || 1}
            value={profLimite}
            onChange={e => setProfLimite(Number(e.target.value))}
            style={s.slider}
          />
        </div>
        <div style={s.stats}>
          <span>
            <strong style={{ color: corAlgoritmo }}>{grafoTree.nodes.length.toLocaleString()}</strong> nós
          </span>
          <span>
            <strong style={{ color: corAlgoritmo }}>{grafoTree.links.length.toLocaleString()}</strong> arestas
          </span>
          {muitosNos && (
            <span style={{ color: '#f4a261', fontSize: 11 }}>
              árvore grande, pode demorar
            </span>
          )}
        </div>
      </div>

      {/* Grafo */}
      <div style={s.canvas}>
        <ForceGraph2D
          ref={fgRef}
          graphData={grafoTree}
          width={800}
          height={500}
          backgroundColor="#0a0c12"

          warmupTicks={50}
          cooldownTicks={120}
          d3AlphaDecay={0.04}
          d3VelocityDecay={0.5}

          nodeRelSize={4}
          nodeColor={n => corPorNivel(n.nivel, n.ehOrigem)}
          nodeVal={n => n.ehOrigem ? 8 : 3}
          nodeLabel={n => `${n.id}  (nível ${n.nivel})`}

          linkColor={l => l.peso < 0 ? 'rgba(231,111,81,0.7)' : 'rgba(160,180,200,0.4)'}
          linkWidth={l => l.peso < 0 ? 1.5 : 0.8}
          linkDirectionalArrowLength={4}
          linkDirectionalArrowRelPos={1}

          linkCanvasObjectMode={() => 'after'}
          linkCanvasObject={(link, ctx, globalScale) => {
            if (globalScale < 1.2) return  
            if (typeof link.source !== 'object' || typeof link.target !== 'object') return

            const x = (link.source.x + link.target.x) / 2
            const y = (link.source.y + link.target.y) / 2
            const fontSize = Math.max(7, 9 / globalScale)
            const txt = String(link.peso)

            ctx.font = `${fontSize}px Segoe UI`
            const w = ctx.measureText(txt).width + 4
            ctx.fillStyle = '#0a0c12'
            ctx.fillRect(x - w/2, y - fontSize/2 - 1, w, fontSize + 2)
            ctx.fillStyle = link.peso < 0 ? '#e76f51' : '#aab'
            ctx.textAlign = 'center'
            ctx.textBaseline = 'middle'
            ctx.fillText(txt, x, y)
          }}

          nodeCanvasObjectMode={() => 'after'}
          nodeCanvasObject={(node, ctx, globalScale) => {
            if (globalScale < 1.4 && !node.ehOrigem) return
            const label = node.id.length > 22 ? node.id.slice(0, 22) + '…' : node.id
            const fontSize = node.ehOrigem
              ? Math.max(9, 13 / globalScale)
              : Math.max(7, 10 / globalScale)
            ctx.font = `${node.ehOrigem ? '600 ' : ''}${fontSize}px Segoe UI`
            ctx.fillStyle = node.ehOrigem ? '#4ae080' : 'rgba(224,224,224,0.85)'
            ctx.textAlign = 'center'
            ctx.fillText(label, node.x, node.y + (node.ehOrigem ? 12 : 8) + fontSize)
          }}
        />
      </div>

      {/* Legenda de cores por nível */}
      <div style={s.legenda}>
        <span style={{ ...s.tag, background: '#0d2a1a', color: '#4ae080' }}>nível 0 (origem)</span>
        {[1, 2, 3, 4, 5].slice(0, profLimite).map(n => (
          <span
            key={n}
            style={{
              ...s.tag,
              background: 'transparent',
              border: '1px solid',
              borderColor: corPorNivel(n, false),
              color: corPorNivel(n, false),
            }}
          >
            nível {n}
          </span>
        ))}
        <span style={{ ...s.tag, background: 'rgba(231,111,81,0.15)', color: '#e76f51', marginLeft: 'auto' }}>
          aresta com peso negativo
        </span>
      </div>
    </div>
  )
}

const s = {
  controles: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', gap: 24, marginBottom: 14, flexWrap: 'wrap' },
  label:     { fontSize: 12, color: '#aab', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 10 },
  contador:  { color: '#2a9d8f', fontWeight: 700, fontFamily: 'monospace' },
  slider:    { width: 240, accentColor: '#2a9d8f', cursor: 'pointer' },
  stats:     { display: 'flex', gap: 16, fontSize: 13, color: '#aab', alignItems: 'center', flexWrap: 'wrap' },
  canvas:    { background: '#0a0c12', border: '1px solid #1a2d3d', borderRadius: 8, overflow: 'hidden', height: 500 },
  legenda:   { display: 'flex', gap: 6, marginTop: 10, flexWrap: 'wrap', alignItems: 'center' },
  tag:       { fontSize: 10, padding: '3px 8px', borderRadius: 4, fontWeight: 600 },
}
