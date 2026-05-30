import { useEffect, useState } from 'react'
import Nav from './Nav.jsx'

const COR = { Dijkstra: '#e9c46a', 'Bellman-Ford': '#e76f51' }

export default function Algoritmos() {
  const [index, setIndex]         = useState(null)
  const [aba, setAba]             = useState('Dijkstra')
  const [aberto, setAberto]       = useState(null)   // id do cenário expandido
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

  const lista = index
    ? (aba === 'Dijkstra' ? index.dijkstra : index.bellman_ford)
    : []

  return (
    <>
      <Nav />
      <div style={s.pagina}>

        {/* ── Seletor de algoritmo ── */}
        <div style={s.card}>
          <h2 style={s.h2}>Caminhos Pré-definidos</h2>
          <p style={{ fontSize: 13, color: '#667', marginBottom: 20 }}>
            Selecione o algoritmo e clique em um cenário para ver o caminho completo
            com os pesos de cada aresta.
          </p>
          <div style={{ display: 'flex', gap: 8, marginBottom: 4 }}>
            {['Dijkstra', 'Bellman-Ford'].map(alg => (
              <button
                key={alg}
                onClick={() => { setAba(alg); setAberto(null); setResultado(null) }}
                style={{
                  ...s.btnAlg,
                  background:  aba === alg ? COR[alg] : 'transparent',
                  color:       aba === alg ? '#111'   : '#889',
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
                <span style={{ ...s.badge, background: COR[c.algoritmo] }}>
                  {c.algoritmo}
                </span>
                {c.tipo === 'negativo' && (
                  <span style={s.tagNeg}>pesos negativos</span>
                )}
                {c.tipo === 'ciclo' && (
                  <span style={s.tagCiclo}>ciclo negativo</span>
                )}
                <p style={{ fontSize: 13, color: '#ccc', marginTop: 8 }}>
                  <span style={{ color: '#556' }}>De: </span>
                  <strong>{c.origem}</strong>
                </p>
                <p style={{ fontSize: 13, color: '#ccc', marginTop: 2 }}>
                  <span style={{ color: '#556' }}>Para: </span>
                  <strong>{c.destino}</strong>
                </p>
              </div>
              <span style={{ color: '#445', fontSize: 18 }}>
                {aberto === c.id ? '▲' : '▼'}
              </span>
            </div>

            {/* Conteúdo expandido */}
            {aberto === c.id && (
              <div style={{ marginTop: 20, borderTop: '1px solid #1e2d3d', paddingTop: 20 }}>
                {carregando && <p style={{ color: '#556' }}>Carregando...</p>}

                {resultado && (
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
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </>
  )
}

const s = {
  pagina:     { marginTop: 56, background: '#0a0c12', minHeight: 'calc(100vh - 56px)', padding: '28px 32px', display: 'flex', flexDirection: 'column', gap: 16 },
  card:       { background: '#0f1420', border: '1px solid #1e2d3d', borderRadius: 12, padding: '20px 24px' },
  h2:         { fontSize: 18, fontWeight: 700, color: '#d0e0f0', marginBottom: 8 },
  btnAlg:     { padding: '8px 22px', borderRadius: 8, border: '1px solid', cursor: 'pointer', fontSize: 14, transition: 'all 0.15s' },
  badge:      { display: 'inline-block', fontSize: 11, fontWeight: 700, color: '#111', padding: '3px 10px', borderRadius: 20, marginRight: 8 },
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
}
