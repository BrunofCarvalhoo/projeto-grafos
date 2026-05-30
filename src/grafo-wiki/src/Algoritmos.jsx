import { useEffect, useState } from 'react'
import Nav from './Nav.jsx'

const COR = {
  BFS: '#2a9d8f',
  DFS: '#264653',
  Dijkstra: '#e9c46a',
  'Bellman-Ford': '#e76f51',
}

export default function Algoritmos() {
  const [index, setIndex]         = useState(null)
  const [aba, setAba]             = useState('BFS')
  const [aberto, setAberto]       = useState(null)
  const [resultado, setResultado] = useState(null)
  const [carregando, setCarregando] = useState(false)

  useEffect(() => {
    fetch('/cenarios_index.json').then(r => r.json()).then(setIndex)
  }, [])

  const abrirCenario = (c) => {
    if (aberto === c.id) { setAberto(null); setResultado(null); return }
    setAberto(c.id)
    setResultado(null)
    setCarregando(true)
    fetch(`/${c.id}.json`)
      .then(r => r.json())
      .then(d => { setResultado(d); setCarregando(false) })
  }

  const abaKey = { BFS: 'bfs', DFS: 'dfs', Dijkstra: 'dijkstra', 'Bellman-Ford': 'bellman_ford' }
  const lista = index ? (index[abaKey[aba]] || []) : []
  const isBusca = aba === 'BFS' || aba === 'DFS'

  return (
    <>
      <Nav />
      <div style={s.pagina}>

        {/* ── Seletor de algoritmo ── */}
        <div style={s.card}>
          <h2 style={s.h2}>Algoritmos do Grafo</h2>
          <p style={{ fontSize: 13, color: '#667', marginBottom: 20 }}>
            Selecione o algoritmo e clique em um cenário para visualizar o resultado.
          </p>

          {/* Grupo: Busca */}
          <p style={s.groupLabel}>Travessia</p>
          <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
            {['BFS', 'DFS'].map(alg => (
              <button
                key={alg}
                onClick={() => { setAba(alg); setAberto(null); setResultado(null) }}
                style={{
                  ...s.btnAlg,
                  background:  aba === alg ? COR[alg] : 'transparent',
                  color:       aba === alg ? '#fff'   : '#889',
                  borderColor: aba === alg ? COR[alg] : '#2a3a4a',
                  fontWeight:  aba === alg ? 700 : 400,
                }}
              >
                {alg}
              </button>
            ))}
          </div>

          {/* Grupo: Caminho mínimo */}
          <p style={s.groupLabel}>Caminho mínimo</p>
          <div style={{ display: 'flex', gap: 8, marginBottom: 4 }}>
            {['Dijkstra', 'Bellman-Ford'].map(alg => (
              <button
                key={alg}
                onClick={() => { setAba(alg); setAberto(null); setResultado(null) }}
                style={{
                  ...s.btnAlg,
                  background:  aba === alg ? COR[alg] : 'transparent',
                  color:       aba === alg ? (alg === 'Dijkstra' ? '#111' : '#fff') : '#889',
                  borderColor: aba === alg ? COR[alg] : '#2a3a4a',
                  fontWeight:  aba === alg ? 700 : 400,
                }}
              >
                {alg}
              </button>
            ))}
          </div>
        </div>

        {/* ── Cenários ── */}
        {lista.map(c => (
          <div key={c.id} style={s.card}>
            {/* Cabeçalho clicável */}
            <div
              onClick={() => abrirCenario(c)}
              style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}
            >
              <div>
                <span style={{ ...s.badge, background: COR[c.algoritmo] || '#556',
                  color: c.algoritmo === 'Dijkstra' ? '#111' : '#fff' }}>
                  {c.algoritmo}
                </span>
                {c.tipo === 'negativo' && (
                  <span style={s.tagNeg}>pesos negativos</span>
                )}
                {c.tipo === 'ciclo' && (
                  <span style={s.tagCiclo}>ciclo negativo</span>
                )}
                <p style={{ fontSize: 13, color: '#ccc', marginTop: 8 }}>
                  <span style={{ color: '#556' }}>{isBusca ? 'Origem: ' : 'De: '}</span>
                  <strong>{c.origem}</strong>
                </p>
                {!isBusca && c.destino && (
                  <p style={{ fontSize: 13, color: '#ccc', marginTop: 2 }}>
                    <span style={{ color: '#556' }}>Para: </span>
                    <strong>{c.destino}</strong>
                  </p>
                )}
              </div>
              <span style={{ color: '#445', fontSize: 18 }}>
                {aberto === c.id ? '▲' : '▼'}
              </span>
            </div>

            {/* Conteúdo expandido */}
            {aberto === c.id && (
              <div style={{ marginTop: 20, borderTop: '1px solid #1e2d3d', paddingTop: 20 }}>
                {carregando && <p style={{ color: '#556' }}>Carregando...</p>}

                {resultado && isBusca && <ResultadoBusca resultado={resultado} cor={COR[aba]} />}
                {resultado && !isBusca && <ResultadoCaminho resultado={resultado} />}
              </div>
            )}
          </div>
        ))}
      </div>
    </>
  )
}


/* ═══════════════════════════════════════════════════
   Componente: Resultado de BFS / DFS
   ═══════════════════════════════════════════════════ */
function ResultadoBusca({ resultado, cor }) {
  const [mostrarTodos, setMostrarTodos] = useState(false)
  const ordemExibida = mostrarTodos
    ? resultado.ordem_visita
    : resultado.ordem_visita.slice(0, 20)

  return (
    <>
      {/* Stats */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 20 }}>
        <div style={s.statBox}>
          <p style={s.statLabel}>Nós visitados</p>
          <p style={{ ...s.statVal, fontSize: 28, color: cor }}>{resultado.total_visitados}</p>
        </div>
        {resultado.profundidade_maxima !== undefined && (
          <div style={s.statBox}>
            <p style={s.statLabel}>Profundidade máx.</p>
            <p style={{ ...s.statVal, fontSize: 28 }}>{resultado.profundidade_maxima}</p>
          </div>
        )}
        <div style={s.statBox}>
          <p style={s.statLabel}>Arestas na árvore</p>
          <p style={{ ...s.statVal, fontSize: 28 }}>{resultado.total_arestas_arvore}</p>
        </div>
        <div style={s.statBox}>
          <p style={s.statLabel}>Tempo</p>
          <p style={{ ...s.statVal, fontSize: 18 }}>{resultado.tempo_ms} ms</p>
        </div>
      </div>

      {/* Ordem de visitação */}
      <div style={s.boxCaminho}>
        <p style={{ fontSize: 11, color: '#445', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 14 }}>
          Ordem de visitação {resultado.total_visitados > resultado.ordem_visita.length
            ? `(primeiros ${resultado.ordem_visita.length} de ${resultado.total_visitados})`
            : ''}
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, alignItems: 'center' }}>
          {ordemExibida.map((no, i) => (
            <span key={i} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <span style={{
                ...s.noTag,
                ...(i === 0 ? { background: '#0d2a1a', color: '#4ae080', fontWeight: 600 } : {}),
                fontSize: 11,
              }}>
                <span style={{ color: '#556', fontSize: 10, marginRight: 4 }}>{i + 1}.</span>
                {no}
              </span>
              {i < ordemExibida.length - 1 && (
                <span style={{ color: '#334', fontSize: 12 }}>→</span>
              )}
            </span>
          ))}
        </div>
        {resultado.ordem_visita.length > 20 && (
          <button
            onClick={() => setMostrarTodos(!mostrarTodos)}
            style={s.btnMais}
          >
            {mostrarTodos
              ? 'Mostrar menos'
              : `Mostrar todos (${resultado.ordem_visita.length})`}
          </button>
        )}
      </div>

      {/* Árvore de busca */}
      <div style={{ ...s.boxCaminho, marginTop: 12 }}>
        <p style={{ fontSize: 11, color: '#445', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 14 }}>
          Árvore de {resultado.algoritmo === 'BFS' ? 'largura' : 'profundidade'}
          {resultado.total_arestas_arvore > resultado.arvore.length
            ? ` (primeiras ${resultado.arvore.length} de ${resultado.total_arestas_arvore} arestas)`
            : ''}
        </p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {resultado.arvore.slice(0, 20).map((aresta, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12 }}>
              <span style={{ ...s.noTag, fontSize: 11, background: '#1a2a1a', color: '#7dcea0' }}>{aresta.de}</span>
              <span style={{ color: cor, fontFamily: 'monospace' }}>──▶</span>
              <span style={{ ...s.noTag, fontSize: 11 }}>{aresta.para}</span>
            </div>
          ))}
          {resultado.arvore.length > 20 && (
            <p style={{ fontSize: 11, color: '#445', marginTop: 6 }}>
              ... e mais {resultado.total_arestas_arvore - 20} arestas
            </p>
          )}
        </div>
      </div>
    </>
  )
}


/* ═══════════════════════════════════════════════════
   Componente: Resultado de Dijkstra / Bellman-Ford
   ═══════════════════════════════════════════════════ */
function ResultadoCaminho({ resultado }) {
  return (
    <>
      {/* Ciclo negativo */}
      {resultado.ciclo_negativo && (
        <div style={s.boxCiclo}>
          <p style={{ fontWeight: 700, color: '#e76f51', marginBottom: 8 }}>
            Ciclo negativo — caminho impossível de calcular
          </p>
          <p style={{ fontSize: 13, color: '#bbb', lineHeight: 1.6, marginBottom: 12 }}>
            {resultado.nota}
          </p>
          <div style={{ background: '#100a0a', borderRadius: 8, padding: '12px 16px' }}>
            <p style={{ fontSize: 12, color: '#778', marginBottom: 8 }}>Ciclo detectado:</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, alignItems: 'center' }}>
              {resultado.ciclo_nos.map((no, i) => (
                <span key={i} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <span style={{ ...s.noTag, color: '#f4a261', background: '#1a1005' }}>{no}</span>
                  {i < resultado.ciclo_pesos.length && (
                    <span style={s.arrowNeg}>
                      ──[{resultado.ciclo_pesos[i]}]──▶
                    </span>
                  )}
                </span>
              ))}
            </div>
            <p style={{ fontSize: 13, color: '#e76f51', marginTop: 10, fontWeight: 600 }}>
              Soma do ciclo: {resultado.ciclo_pesos.join(' + ')} = {resultado.ciclo_soma}
            </p>
          </div>
        </div>
      )}

      {/* Caminho válido */}
      {!resultado.ciclo_negativo && resultado.passos && (
        <>
          {/* Nota (BF negativo) */}
          {resultado.nota && (
            <p style={{ fontSize: 13, color: '#f4a261', background: 'rgba(244,162,97,0.08)', padding: '8px 12px', borderRadius: 6, marginBottom: 16, lineHeight: 1.6 }}>
              {resultado.nota}
            </p>
          )}

          {/* Visualização do caminho com pesos */}
          <div style={s.boxCaminho}>
            <p style={{ fontSize: 11, color: '#445', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 14 }}>
              Caminho
            </p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, alignItems: 'center' }}>
              {/* Nó de origem */}
              <span style={{ ...s.noTag, ...s.noOrigem }}>
                {resultado.origem}
              </span>
              {resultado.passos.map((p, i) => (
                <span key={i} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <span style={{
                    ...s.arrowLabel,
                    color: p.peso < 0 ? '#e76f51' : '#556',
                  }}>
                    ──[{p.peso}]──▶
                  </span>
                  <span style={{
                    ...s.noTag,
                    ...(i === resultado.passos.length - 1 ? s.noDestino : {}),
                  }}>
                    {i === resultado.passos.length - 1 && ''}{p.para}
                  </span>
                </span>
              ))}
            </div>
          </div>

          {/* Custo total */}
          <div style={{ marginTop: 16, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <div style={s.statBox}>
              <p style={s.statLabel}>Custo total</p>
              <p style={{
                ...s.statVal,
                color: resultado.custo_total < 0 ? '#e76f51' : '#2a9d8f',
                fontSize: 28,
              }}>
                {resultado.custo_total}
              </p>
            </div>
            <div style={s.statBox}>
              <p style={s.statLabel}>Nós no caminho</p>
              <p style={{ ...s.statVal, fontSize: 28 }}>
                {resultado.passos.length + 1}
              </p>
            </div>
            <div style={s.statBox}>
              <p style={s.statLabel}>Tempo</p>
              <p style={{ ...s.statVal, fontSize: 18 }}>
                {resultado.tempo_ms} ms
              </p>
            </div>
          </div>
        </>
      )}
    </>
  )
}


const s = {
  pagina:     { marginTop: 56, background: '#0a0c12', height: 'calc(100vh - 56px)', overflowY: 'auto', padding: '28px 32px', display: 'flex', flexDirection: 'column', gap: 16 },
  card:       { background: '#0f1420', border: '1px solid #1e2d3d', borderRadius: 12, padding: '20px 24px' },
  h2:         { fontSize: 18, fontWeight: 700, color: '#d0e0f0', marginBottom: 8 },
  groupLabel: { fontSize: 11, color: '#556', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 6 },
  btnAlg:     { padding: '8px 22px', borderRadius: 8, border: '1px solid', cursor: 'pointer', fontSize: 14, transition: 'all 0.15s' },
  badge:      { display: 'inline-block', fontSize: 11, fontWeight: 700, padding: '3px 10px', borderRadius: 20, marginRight: 8 },
  tagNeg:     { display: 'inline-block', fontSize: 11, background: 'rgba(244,162,97,0.15)', color: '#f4a261', padding: '2px 8px', borderRadius: 4 },
  tagCiclo:   { display: 'inline-block', fontSize: 11, background: 'rgba(231,111,81,0.15)', color: '#e76f51', padding: '2px 8px', borderRadius: 4 },
  boxCiclo:   { background: 'rgba(231,111,81,0.07)', border: '1px solid rgba(231,111,81,0.25)', borderRadius: 10, padding: '16px 18px' },
  boxCaminho: { background: '#0a0c12', border: '1px solid #1a2d3d', borderRadius: 10, padding: '16px 18px' },
  noTag:      { background: '#1a2230', color: '#b0c8e0', padding: '5px 12px', borderRadius: 6, fontSize: 12, whiteSpace: 'nowrap' },
  noOrigem:   { background: '#0d2a1a', color: '#4ae080', fontWeight: 600 },
  noDestino:  { background: '#1a0d0d', color: '#f08080', fontWeight: 600 },
  arrowLabel: { fontSize: 12, whiteSpace: 'nowrap', fontFamily: 'monospace' },
  arrowNeg:   { fontSize: 12, color: '#e76f51', whiteSpace: 'nowrap', fontFamily: 'monospace' },
  statBox:    { background: '#0a0c12', border: '1px solid #1e2d3d', borderRadius: 8, padding: '10px 18px', minWidth: 100 },
  statLabel:  { fontSize: 11, color: '#445', marginBottom: 4 },
  statVal:    { fontWeight: 700, color: '#d0e0f0' },
  btnMais:    { marginTop: 10, background: 'transparent', border: '1px solid #2a3a4a', color: '#889', borderRadius: 6, padding: '6px 14px', cursor: 'pointer', fontSize: 12 },
}
