import { useEffect, useState, useMemo } from 'react'
import Nav from './Nav.jsx'

const API = 'http://localhost:5000'

const ALGORITMOS = [
  { id: 'BFS',          cor: '#2a9d8f', precisaDestino: false, descricao: 'Busca em Largura — visita por níveis a partir da origem.' },
  { id: 'DFS',          cor: '#264653', precisaDestino: false, descricao: 'Busca em Profundidade — explora cada ramo até o fim antes de voltar.' },
  { id: 'Dijkstra',     cor: '#e9c46a', precisaDestino: true,  descricao: 'Menor caminho com pesos positivos — origem até destino.' },
  { id: 'Bellman-Ford', cor: '#e76f51', precisaDestino: true,  descricao: 'Menor caminho com pesos quaisquer — detecta ciclos negativos.' },
]

export default function Algoritmos() {
  const [nos, setNos]               = useState([])
  const [info, setInfo]             = useState(null)
  const [apiOff, setApiOff]         = useState(false)

  const [algSel, setAlgSel]         = useState('BFS')
  const [origem, setOrigem]         = useState('')
  const [destino, setDestino]       = useState('')
  const [sugO, setSugO]             = useState([])
  const [sugD, setSugD]             = useState([])

  const [rodando, setRodando]       = useState(false)
  const [resultado, setResultado]   = useState(null)
  const [erro, setErro]             = useState('')

  const algoritmoMeta = useMemo(
    () => ALGORITMOS.find(a => a.id === algSel),
    [algSel]
  )

  useEffect(() => {
    Promise.all([
      fetch(`${API}/nos`).then(r => r.json()),
      fetch(`${API}/info`).then(r => r.json()),
    ])
      .then(([listaNos, infoData]) => {
        setNos(listaNos)
        setInfo(infoData)
      })
      .catch(() => setApiOff(true))
  }, [])

  const filtrar = (texto, setSug) => {
    if (texto.length < 2) { setSug([]); return }
    const t = texto.toLowerCase()
    setSug(nos.filter(n => n.toLowerCase().includes(t)).slice(0, 8))
  }

  const executar = async () => {
    setErro('')
    setResultado(null)
    setRodando(true)

    try {
      const body = {
        algoritmo: algSel,
        origem,
        destino: algoritmoMeta.precisaDestino ? destino : null,
      }
      const res = await fetch(`${API}/algoritmo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      const data = await res.json()
      if (!res.ok) {
        setErro(data.detail || data.erro || 'Erro desconhecido.')
      } else {
        setResultado(data)
      }
    } catch {
      setErro('Não foi possível conectar à API. Confirme que ela está rodando.')
      setApiOff(true)
    } finally {
      setRodando(false)
    }
  }

  return (
    <>
      <Nav />
      <div style={s.pagina}>

        {/* Aviso de API offline */}
        {apiOff && (
          <div style={s.banner}>
            ⚠ API offline. Em outro terminal, execute:{' '}
            <code style={s.code}>python src/api.py</code>
          </div>
        )}

        {/* ── Painel de controle ── */}
        <div style={s.card}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16, gap: 12, flexWrap: 'wrap' }}>
            <div>
              <h2 style={s.h2}>Executar Algoritmo</h2>
              <p style={{ fontSize: 13, color: '#778' }}>
                Os algoritmos rodam em Python via API local, sobre o grafo Wikipedia.
              </p>
            </div>
            {info && (
              <span style={s.badge}>
                {info.vertices.toLocaleString()} vértices · {info.arestas.toLocaleString()} arestas
              </span>
            )}
          </div>

          {/* Seletor de algoritmo */}
          <div style={s.grupo}>
            <label style={s.label}>Algoritmo</label>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {ALGORITMOS.map(a => (
                <button
                  key={a.id}
                  onClick={() => {
                    setAlgSel(a.id)
                    setResultado(null)
                    setErro('')
                    if (!a.precisaDestino) setDestino('')
                  }}
                  style={{
                    ...s.btnAlg,
                    background:  algSel === a.id ? a.cor : 'transparent',
                    color:       algSel === a.id ? (a.id === 'Dijkstra' ? '#111' : '#fff') : '#889',
                    borderColor: algSel === a.id ? a.cor : '#2a3a4a',
                    fontWeight:  algSel === a.id ? 700 : 400,
                  }}
                >
                  {a.id}
                </button>
              ))}
            </div>
            <p style={{ fontSize: 12, color: '#667', marginTop: 8, lineHeight: 1.5 }}>
              {algoritmoMeta.descricao}
            </p>
          </div>

          {/* Origem */}
          <div style={s.grupo}>
            <label style={s.label}>Nó de origem</label>
            <Autocomplete
              value={origem}
              onChange={v => { setOrigem(v); filtrar(v, setSugO) }}
              sugestoes={sugO}
              onSelect={v => { setOrigem(v); setSugO([]) }}
              placeholder="Comece a digitar o nome da página..."
              disabled={apiOff}
            />
          </div>

          {/* Destino — só se precisa */}
          {algoritmoMeta.precisaDestino && (
            <div style={s.grupo}>
              <label style={s.label}>Nó de destino</label>
              <Autocomplete
                value={destino}
                onChange={v => { setDestino(v); filtrar(v, setSugD) }}
                sugestoes={sugD}
                onSelect={v => { setDestino(v); setSugD([]) }}
                placeholder="Comece a digitar o nome da página..."
                disabled={apiOff}
              />
            </div>
          )}

          {erro && <p style={s.erro}>{erro}</p>}

          <button
            style={{ ...s.btnExecutar, opacity: (rodando || apiOff) ? 0.5 : 1 }}
            onClick={executar}
            disabled={
              rodando || apiOff || !origem ||
              (algoritmoMeta.precisaDestino && !destino)
            }
          >
            {rodando ? 'Executando...' : `Executar ${algSel}`}
          </button>
        </div>

        {/* ── Resultado ── */}
        {resultado && (
          <div style={s.card}>
            {(resultado.algoritmo === 'BFS' || resultado.algoritmo === 'DFS') &&
              <ResultadoTravessia r={resultado} cor={algoritmoMeta.cor} />
            }
            {(resultado.algoritmo === 'Dijkstra' || resultado.algoritmo === 'Bellman-Ford') &&
              <ResultadoCaminho r={resultado} cor={algoritmoMeta.cor} />
            }
          </div>
        )}
      </div>
    </>
  )
}

function ResultadoTravessia({ r, cor }) {
  const [mostrarTudo, setMostrarTudo] = useState(false)
  const LIMITE = 30
  const ordem  = mostrarTudo ? r.ordem_visita : r.ordem_visita.slice(0, LIMITE)

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 8, marginBottom: 18 }}>
        <h2 style={s.h2}>{r.algoritmo} — Resultado</h2>
        <p style={{ fontSize: 12, color: '#667' }}>
          Origem: <strong style={{ color: '#ccc' }}>{r.origem}</strong>
        </p>
      </div>

      {/* Stats */}
      <div style={s.statsGrid}>
        <Metrica label="Visitados" valor={r.total_visitados.toLocaleString()} cor={cor} grande />
        <Metrica label="De um total de" valor={r.total_vertices.toLocaleString()} />
        <Metrica label="Arestas da árvore" valor={r.arestas_arvore.length.toLocaleString()} />
        <Metrica label="Tempo (Python)" valor={`${r.tempo_ms} ms`} small />
      </div>

      {/* Ordem de visita */}
      <div style={s.boxCaminho}>
        <p style={s.tituloBox}>
          Ordem de visitação
          {!mostrarTudo && r.total_visitados > LIMITE && ` (primeiros ${LIMITE} de ${r.total_visitados.toLocaleString()})`}
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, alignItems: 'center' }}>
          {ordem.map((no, i) => (
            <span key={i} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <span style={{
                ...s.noTag, fontSize: 11,
                ...(i === 0 ? { background: '#0d2a1a', color: '#4ae080', fontWeight: 600 } : {}),
              }}>
                <span style={{ color: '#556', fontSize: 10, marginRight: 4 }}>{i + 1}.</span>
                {no}
              </span>
              {i < ordem.length - 1 && <span style={{ color: '#334' }}>→</span>}
            </span>
          ))}
        </div>
        {r.total_visitados > LIMITE && (
          <button
            style={s.btnMostrarTudo}
            onClick={() => setMostrarTudo(v => !v)}
          >
            {mostrarTudo ? 'mostrar menos' : `mostrar todos (${r.total_visitados.toLocaleString()})`}
          </button>
        )}
      </div>

      {/* Árvore — apenas amostra */}
      {r.arestas_arvore.length > 0 && (
        <div style={{ ...s.boxCaminho, marginTop: 14 }}>
          <p style={s.tituloBox}>
            Árvore de busca (amostra de {Math.min(20, r.arestas_arvore.length)} arestas)
          </p>
          <div style={{ display: 'grid', gap: 4 }}>
            {r.arestas_arvore.slice(0, 20).map((a, i) => (
              <div key={i} style={{ fontSize: 12, color: '#aab' }}>
                <span style={{ color: '#667' }}>{a.pai}</span>
                <span style={{ color: '#445', margin: '0 6px' }}>→</span>
                <span>{a.filho}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  )
}

function ResultadoCaminho({ r, cor }) {

  if (r.ciclo_negativo) {
    return (
      <>
        <h2 style={s.h2}>{r.algoritmo} — Ciclo negativo</h2>
        <div style={s.boxCiclo}>
          <p style={{ fontWeight: 700, color: '#e76f51', marginBottom: 8 }}>
            ⚠ Ciclo negativo detectado no grafo
          </p>
          <p style={{ fontSize: 13, color: '#ccc', lineHeight: 1.6 }}>
            O Bellman-Ford encontrou um ciclo cuja soma de pesos é negativa.
            Isso impede o cálculo de menor caminho — você poderia percorrer
            o ciclo infinitas vezes para diminuir o custo. As arestas que
            formam o ciclo estão listadas abaixo.
          </p>
        </div>
        <BoxCiclos ciclos={r.ciclos_no_grafo} />
      </>
    )
  }

  if (!r.alcancavel) {
    return (
      <div style={s.boxCiclo}>
        <p style={{ fontWeight: 700, color: '#e76f51', marginBottom: 8 }}>
          Destino inacessível
        </p>
        <p style={{ fontSize: 13, color: '#ccc' }}>
          Não existe caminho de <strong>{r.origem}</strong> até <strong>{r.destino}</strong> no grafo.
        </p>
      </div>
    )
  }

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 8, marginBottom: 18 }}>
        <h2 style={s.h2}>{r.algoritmo} — Caminho encontrado</h2>
        <p style={{ fontSize: 12, color: '#667' }}>{r.tempo_ms} ms</p>
      </div>

      {/* Stats */}
      <div style={s.statsGrid}>
        <Metrica
          label="Custo total"
          valor={r.custo_total}
          cor={r.custo_total < 0 ? '#e76f51' : cor}
          grande
        />
        <Metrica label="Nós no caminho" valor={r.passos.length + 1} />
        <Metrica label="Saltos" valor={r.passos.length} />
      </div>

      {/* Visualização do caminho */}
      <div style={s.boxCaminho}>
        <p style={s.tituloBox}>Caminho percorrido</p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, alignItems: 'center' }}>
          <span style={{ ...s.noTag, ...s.noOrigem }}>🟢 {r.origem}</span>
          {r.passos.map((p, i) => (
            <span key={i} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <span style={{
                ...s.arrowLabel,
                color: p.peso < 0 ? '#e76f51' : '#556',
              }}>
                ──[{p.peso}]──▶
              </span>
              <span style={{
                ...s.noTag,
                ...(i === r.passos.length - 1 ? s.noDestino : {}),
              }}>
                {i === r.passos.length - 1 && '🔴 '}{p.para}
              </span>
            </span>
          ))}
        </div>
      </div>

    </>
  )
}

function BoxCiclos({ ciclos }) {
  if (!ciclos || ciclos.length === 0) return null
  return (
    <div style={{ ...s.boxCaminho, marginTop: 14, borderColor: 'rgba(231,111,81,0.3)' }}>
      <p style={s.tituloBox}>
        Arestas que formam ciclo negativo no grafo ({ciclos.length})
      </p>
      <div style={{ display: 'grid', gap: 8 }}>
        {ciclos.map((c, i) => (
          <div key={i} style={s.boxCicloItem}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 4, flexWrap: 'wrap' }}>
              <span style={{ ...s.noTag, background: '#1a1005', color: '#f4a261' }}>{c.a}</span>
              <span style={{ ...s.arrowLabel, color: '#e76f51' }}>──[{c.peso_ab}]──▶</span>
              <span style={{ ...s.noTag, background: '#1a1005', color: '#f4a261' }}>{c.b}</span>
              <span style={{ ...s.arrowLabel, color: '#e76f51' }}>──[{c.peso_ba}]──▶</span>
              <span style={{ ...s.noTag, background: '#1a1005', color: '#f4a261' }}>{c.a}</span>
            </div>
            <p style={{ fontSize: 11, color: '#e76f51', marginTop: 6, fontWeight: 600 }}>
              Soma do ciclo: {c.peso_ab} + {c.peso_ba} = {c.soma}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

function Autocomplete({ value, onChange, sugestoes, onSelect, placeholder, disabled }) {
  return (
    <div style={{ position: 'relative', maxWidth: 540 }}>
      <input
        style={{ ...s.input, opacity: disabled ? 0.5 : 1 }}
        placeholder={placeholder}
        value={value}
        onChange={e => onChange(e.target.value)}
        disabled={disabled}
      />
      {sugestoes.length > 0 && (
        <div style={s.dropdown}>
          {sugestoes.map(n => (
            <div key={n} style={s.sugestao} onClick={() => onSelect(n)}>{n}</div>
          ))}
        </div>
      )}
    </div>
  )
}

function Metrica({ label, valor, cor, grande, small }) {
  return (
    <div style={s.statBox}>
      <p style={s.statLabel}>{label}</p>
      <p style={{
        ...s.statVal,
        color: cor ?? '#d0e0f0',
        fontSize: grande ? 30 : small ? 16 : 22,
      }}>{valor}</p>
    </div>
  )
}

const s = {
  pagina:     { marginTop: 56, background: '#0a0c12', minHeight: 'calc(100vh - 56px)', padding: '28px 32px', display: 'flex', flexDirection: 'column', gap: 16 },
  card:       { background: '#0f1420', border: '1px solid #1e2d3d', borderRadius: 12, padding: '24px 28px' },
  h2:         { fontSize: 18, fontWeight: 700, color: '#d0e0f0', marginBottom: 6 },
  banner:     { background: 'rgba(231,111,81,0.12)', border: '1px solid #e76f51', borderRadius: 8, padding: '12px 16px', fontSize: 13, color: '#f4a261' },
  code:       { background: '#1a2535', padding: '2px 8px', borderRadius: 4, fontFamily: 'monospace', marginLeft: 6 },
  badge:      { fontSize: 12, color: '#667', background: '#0a0c12', border: '1px solid #1e2d3d', borderRadius: 20, padding: '5px 12px', whiteSpace: 'nowrap' },

  grupo:      { marginBottom: 18 },
  label:      { display: 'block', fontSize: 13, color: '#a0b0c0', marginBottom: 6, fontWeight: 500 },
  input:      { width: '100%', padding: '9px 13px', background: '#0a0c12', border: '1px solid #2a3a4a', borderRadius: 7, color: '#e0e0e0', fontSize: 13, outline: 'none', boxSizing: 'border-box' },
  dropdown:   { position: 'absolute', top: '100%', left: 0, right: 0, background: '#111823', border: '1px solid #2a3a4a', borderRadius: 7, zIndex: 50, boxShadow: '0 8px 24px rgba(0,0,0,0.5)', marginTop: 2 },
  sugestao:   { padding: '9px 13px', fontSize: 13, cursor: 'pointer', color: '#c0d0e0', borderBottom: '1px solid #1a2535' },

  btnAlg:     { padding: '8px 18px', borderRadius: 6, border: '1px solid', cursor: 'pointer', fontSize: 13, transition: 'all 0.15s' },
  btnExecutar:{ padding: '10px 28px', borderRadius: 7, border: 'none', background: '#2a9d8f', color: '#fff', cursor: 'pointer', fontSize: 14, fontWeight: 700, marginTop: 6 },
  btnMostrarTudo: { background: 'none', border: 'none', color: '#2a9d8f', cursor: 'pointer', fontSize: 11, padding: 0, marginTop: 10, textDecoration: 'underline' },

  erro:       { color: '#e76f51', fontSize: 13, marginBottom: 10 },

  statsGrid:  { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))', gap: 12, marginBottom: 20 },
  statBox:    { background: '#0a0c12', border: '1px solid #1e2d3d', borderRadius: 8, padding: '12px 18px' },
  statLabel:  { fontSize: 11, color: '#445', marginBottom: 4, textTransform: 'uppercase', letterSpacing: 0.5 },
  statVal:    { fontWeight: 700 },

  boxCaminho:    { background: '#0a0c12', border: '1px solid #1a2d3d', borderRadius: 10, padding: '16px 18px' },
  boxCiclo:      { background: 'rgba(231,111,81,0.07)', border: '1px solid rgba(231,111,81,0.3)', borderRadius: 10, padding: '20px 24px' },
  boxCicloItem:  { background: '#100a0a', border: '1px solid #2a1a1a', borderRadius: 8, padding: '10px 14px' },
  avisoCiclo:    { background: 'rgba(231,111,81,0.07)', border: '1px solid rgba(231,111,81,0.3)', borderRadius: 8, padding: '12px 16px', marginBottom: 16 },
  tituloBox:  { fontSize: 11, color: '#445', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 1, marginBottom: 12 },

  noTag:      { background: '#1a2230', color: '#b0c8e0', padding: '5px 12px', borderRadius: 6, fontSize: 12, whiteSpace: 'nowrap' },
  noOrigem:   { background: '#0d2a1a', color: '#4ae080', fontWeight: 600 },
  noDestino:  { background: '#1a0d0d', color: '#f08080', fontWeight: 600 },
  arrowLabel: { fontSize: 12, whiteSpace: 'nowrap', fontFamily: 'monospace' },
}
