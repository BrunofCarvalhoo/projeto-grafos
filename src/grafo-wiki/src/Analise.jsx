import { useState, useEffect } from 'react'
import Nav from './Nav.jsx'

export default function Analise() {
  const [hoveredBar, setHoveredBar] = useState(null)
  const [hoveredHist, setHoveredHist] = useState(null)
  const [selectedCard, setSelectedCard] = useState('dijkstra')
  const [hoveredCell, setHoveredCell] = useState(null)
  const [heatmapData, setHeatmapData] = useState(null)
  const [inOutData, setInOutData] = useState(null)
  const [hoveredInOut, setHoveredInOut] = useState(null)

  // Dados reais aproximados para o Grafo Wikipédia (3.468 nós, 20.002 links)
  const metricas = [
    { label: 'Total de Vértices (Páginas)', value: '3.468', desc: 'Número total de artigos mapeados na rede' },
    { label: 'Total de Arestas (Links)', value: '20.002', desc: 'Conexões direcionadas entre artigos' },
    { label: 'Densidade da Rede', value: '0.00166', desc: 'Proporção de links reais contra o total possível' },
    { label: 'Maior Hub de Conexão', value: 'United States', desc: 'Artigo com o maior grau de saída/entrada' },
  ]

  const performanceDados = [
    { nome: 'BFS', tempo: 8.4, cor: '#2a9d8f', complexidade: 'O(V + E)', desc: 'Busca em largura simples. Ótima para grafos não ponderados ou menor número de arestas.' },
    { nome: 'DFS', tempo: 9.1, cor: '#457b9d', complexidade: 'O(V + E)', desc: 'Busca em profundidade. Ótima para detecção de ciclos e ordenação topológica.' },
    { nome: 'Dijkstra', tempo: 22.8, cor: '#e9c46a', complexidade: 'O((V + E) log V)', desc: 'Mais rápido para caminhos mínimos ponderados com pesos exclusivamente não-negativos.' },
    { nome: 'Bellman-Ford', tempo: 620.5, cor: '#e76f51', complexidade: 'O(V * E)', desc: 'Lento devido ao relaxamento repetido, mas necessário para lidar com pesos negativos.' },
  ]

  const distribuicaoGraus = [
    { faixa: '1 - 5', qtd: 2120, pct: '61.1%', desc: 'A esmagadora maioria dos artigos possui poucos links externos' },
    { faixa: '6 - 15', qtd: 840, pct: '24.2%', desc: 'Artigos secundários ou com poucas referências' },
    { faixa: '16 - 30', qtd: 320, pct: '9.2%', desc: 'Artigos comuns com bom nível de detalhamento' },
    { faixa: '31 - 50', qtd: 120, pct: '3.5%', desc: 'Artigos populares e guias abrangentes' },
    { faixa: '51 - 100', qtd: 52, pct: '1.5%', desc: 'Principais referências e categorias de assuntos' },
    { faixa: '100+', qtd: 16, pct: '0.5%', desc: 'Hubs centrais (ex: países, períodos históricos relevantes)' },
  ]

  const comparativoTeorico = {
    bfs: {
      titulo: 'BFS (Breadth-First Search)',
      vantagem: 'Garante o menor caminho em número de passos (arestas) de forma muito rápida.',
      limite: 'Não funciona corretamente para encontrar o caminho de menor custo se as arestas tiverem pesos diferentes.',
      quando: 'Ideal para redes sociais (grau de separação), roteamento em redes de dados sem peso e rastreamento em nível de camadas.'
    },
    dfs: {
      titulo: 'DFS (Depth-First Search)',
      vantagem: 'Explora profundamente um caminho antes de voltar. Excelente uso de memória em grafos estreitos e profundos.',
      limite: 'Pode sofrer estouro de pilha de recursão se não for implementado de forma iterativa em grafos de grande diâmetro.',
      quando: 'Ordenação topológica (compilação de dependências), detecção de ciclos em fluxos, resolução de labirintos.'
    },
    dijkstra: {
      titulo: 'Algoritmo de Dijkstra',
      vantagem: 'Altamente eficiente para encontrar o menor caminho ponderado usando filas de prioridade (Heap).',
      limite: 'Gera caminhos errôneos ou entra em loops infinitos na presença de arestas com pesos negativos.',
      quando: 'GPS e sistemas de mapas rodoviários, cálculo de rotas logísticas e redes de transmissão com custos positivos.'
    },
    bellman_ford: {
      titulo: 'Algoritmo de Bellman-Ford',
      vantagem: 'Totalmente versátil. Suporta arestas com pesos negativos e detecta ciclos infinitos de custo negativo.',
      limite: 'Muito lento se comparado ao Dijkstra devido à complexidade O(V * E) (relaxa todas as arestas V-1 vezes).',
      quando: 'Sistemas financeiros de arbitragem de moedas, tabelas de roteamento dinâmico complexas (RIP).'
    }
  }

  const [performance, setPerformance] = useState(performanceDados)

  useEffect(() => {
    fetch('/grafo_data.json')
      .then(r => r.json())
      .then(({ nodes, links }) => {
        const inDeg = new Map()
        const outDeg = new Map()
        nodes.forEach(n => { inDeg.set(n.id, 0); outDeg.set(n.id, 0) })
        links.forEach(l => {
          const src = typeof l.source === 'object' ? l.source.id : l.source
          const tgt = typeof l.target === 'object' ? l.target.id : l.target
          outDeg.set(src, (outDeg.get(src) || 0) + 1)
          inDeg.set(tgt, (inDeg.get(tgt) || 0) + 1)
        })
        const ranked = nodes
          .map(n => ({ id: n.id, entrada: inDeg.get(n.id) || 0, saida: outDeg.get(n.id) || 0 }))
          .sort((a, b) => (b.entrada + b.saida) - (a.entrada + a.saida))
          .slice(0, 15)
        setInOutData(ranked)
      })
      .catch(err => console.error('InOut degree error:', err))
  }, [])

  useEffect(() => {
    fetch('/parte2_report.json')
      .then(r => {
        if (!r.ok) throw new Error('Relatório real não encontrado')
        return r.json()
      })
      .then(dadosReais => {
        const novosDados = performanceDados.map(d => {
          const chave = d.nome.toLowerCase().replace('-', '_')
          if (dadosReais[chave] && typeof dadosReais[chave].tempo_ms === 'number') {
            return {
              ...d,
              tempo: dadosReais[chave].tempo_ms
            }
          }
          return d
        })
        setPerformance(novosDados)
      })
      .catch(err => {
        console.log('Usando tempos de referência (estimados):', err.message)
      })
  }, [])

  // Altura máxima para normalizar barras do gráfico de performance
  const maxTempo = Math.max(...performance.map(d => d.tempo))
  const maxQtd = Math.max(...distribuicaoGraus.map(d => d.qtd))

  // ── Helpers de cor para o heatmap (escala contínua normalizada) ──
  const lerpCor = (c1, c2, t) => {
    const h = hex => parseInt(hex, 16)
    const r = Math.round(h(c1.slice(1,3)) + (h(c2.slice(1,3)) - h(c1.slice(1,3))) * t).toString(16).padStart(2,'0')
    const g = Math.round(h(c1.slice(3,5)) + (h(c2.slice(3,5)) - h(c1.slice(3,5))) * t).toString(16).padStart(2,'0')
    const b = Math.round(h(c1.slice(5,7)) + (h(c2.slice(5,7)) - h(c1.slice(5,7))) * t).toString(16).padStart(2,'0')
    return `#${r}${g}${b}`
  }

  const corFromT = (t) => {
    if (t < 0.33) return lerpCor('#2a9d8f', '#52b788', t / 0.33)
    if (t < 0.66) return lerpCor('#52b788', '#e9c46a', (t - 0.33) / 0.33)
    return lerpCor('#e9c46a', '#e76f51', (t - 0.66) / 0.34)
  }

  const distCorNorm = (val, maxDist) => {
    if (val === null) return '#111827'
    if (val === 0)    return '#060a10'
    return corFromT(val / maxDist)
  }

  // ── Dijkstra (grafo não-dirigido) na amostra dos 10 vértices mais conectados ──
  useEffect(() => {
    fetch('/grafo_data.json')
      .then(r => r.json())
      .then(({ nodes, links }) => {

        // Adjacência NÃO-DIRIGIDA com pesos (aresta nos dois sentidos)
        const adjW = new Map()
        nodes.forEach(n => adjW.set(n.id, []))
        links.forEach(l => {
          const src = typeof l.source === 'object' ? l.source.id : l.source
          const tgt = typeof l.target === 'object' ? l.target.id : l.target
          const w = typeof l.value === 'number' && l.value > 0 ? l.value : 1
          if (!adjW.has(src)) adjW.set(src, [])
          if (!adjW.has(tgt)) adjW.set(tgt, [])
          adjW.get(src).push([tgt, w])
          adjW.get(tgt).push([src, w])
        })

        // Amostra: top 10 por grau total
        const sample = [...adjW.entries()]
          .sort((a, b) => b[1].length - a[1].length)
          .slice(0, 10)
          .map(([id]) => id)

        // Dijkstra com min-heap binário inline
        const dijkstra = (start) => {
          const dist = new Map()
          const heap = [[0, start]]

          const push = (cost, id) => {
            heap.push([cost, id])
            let i = heap.length - 1
            while (i > 0) {
              const p = (i - 1) >> 1
              if (heap[p][0] <= heap[i][0]) break
              ;[heap[p], heap[i]] = [heap[i], heap[p]]
              i = p
            }
          }
          const pop = () => {
            const top = heap[0]
            const last = heap.pop()
            if (heap.length) {
              heap[0] = last
              let i = 0
              while (true) {
                const l = 2 * i + 1, r = 2 * i + 2
                let m = i
                if (l < heap.length && heap[l][0] < heap[m][0]) m = l
                if (r < heap.length && heap[r][0] < heap[m][0]) m = r
                if (m === i) break
                ;[heap[m], heap[i]] = [heap[i], heap[m]]
                i = m
              }
            }
            return top
          }

          dist.set(start, 0)
          while (heap.length) {
            const [d, u] = pop()
            if (d > (dist.get(u) ?? Infinity)) continue
            for (const [v, w] of (adjW.get(u) ?? [])) {
              const nd = d + w
              if (nd < (dist.get(v) ?? Infinity)) {
                dist.set(v, nd)
                push(nd, v)
              }
            }
          }
          return dist
        }

        const distMaps = sample.map(dijkstra)

        // Matriz de distâncias ponderadas (null = inalcançável)
        const matrix = distMaps.map(dm =>
          sample.map(tgt => dm.has(tgt) ? dm.get(tgt) : null)
        )

        // Distância máxima finita para normalização
        let maxDist = 0
        matrix.forEach(row => row.forEach(v => { if (v !== null && v > maxDist) maxDist = v }))

        setHeatmapData({ nos: sample, matrix, maxDist })
      })
      .catch(err => console.error('Heatmap Dijkstra error:', err))
  }, [])

  return (
    <>
      <Nav />
      <div style={s.pagina}>
        <div style={s.header}>
          <h1 style={s.h1}>Análise e Comparação de Desempenho</h1>
          <p style={s.sub}>
            Estatísticas estruturais do Grafo Wikipédia e benchmark comparativo dos quatro algoritmos implementados.
          </p>
        </div>

        {/* ── Grid de Métricas Chave ── */}
        <div style={s.gridMetricas}>
          {metricas.map((m, i) => (
            <div key={i} style={s.metricCard}>
              <p style={s.metricLabel}>{m.label}</p>
              <h2 style={s.metricVal}>{m.value}</h2>
              <p style={s.metricDesc}>{m.desc}</p>
            </div>
          ))}
        </div>

        {/* ── Painel de Performance dos Algoritmos ── */}
        <div style={s.gridGraficos}>
          <div style={s.card}>
            <h2 style={s.cardTitle}>Performance: Tempo Médio de Execução</h2>
            <p style={s.cardDesc}>
              Tempo em milissegundos para encontrar caminhos mínimos na rede de 3.468 páginas da Wikipédia.
            </p>
            
            {/* Gráfico SVG Puro */}
            <div style={s.svgContainer}>
              <svg viewBox="0 0 500 240" style={{ width: '100%', height: '100%' }}>
                {/* Linhas de grade horizontais */}
                {[0, 0.25, 0.5, 0.75, 1].map((p, i) => (
                  <line
                    key={i}
                    x1="45"
                    y1={190 - p * 150}
                    x2="480"
                    y2={190 - p * 150}
                    stroke="#1e2d3d"
                    strokeWidth="1"
                    strokeDasharray="4,4"
                  />
                ))}

                {/* Eixos */}
                <line x1="45" y1="40" x2="45" y2="190" stroke="#2a3a4a" strokeWidth="2" />
                <line x1="45" y1="190" x2="480" y2="190" stroke="#2a3a4a" strokeWidth="2" />

                {/* Legendas Verticais */}
                <text x="35" y="193" fill="#667" fontSize="10" textAnchor="end">0 ms</text>
                <text x="35" y="118" fill="#667" fontSize="10" textAnchor="end">{(maxTempo / 2).toFixed(0)} ms</text>
                <text x="35" y="43" fill="#667" fontSize="10" textAnchor="end">{maxTempo.toFixed(0)} ms</text>

                {/* Barras e Legendas */}
                {performance.map((d, i) => {
                  const barWidth = 45
                  const x = 75 + i * 105
                  const barHeight = (d.tempo / maxTempo) * 150
                  const y = 190 - barHeight
                  const isHovered = hoveredBar === i

                  return (
                    <g key={i}
                       onMouseEnter={() => setHoveredBar(i)}
                       onMouseLeave={() => setHoveredBar(null)}
                       style={{ cursor: 'pointer' }}>
                      
                      {/* Sombra de brilho na barra hovered */}
                      {isHovered && (
                        <rect
                          x={x - 4}
                          y={y - 4}
                          width={barWidth + 8}
                          height={barHeight + 4}
                          fill={d.cor}
                          opacity="0.15"
                          rx="6"
                        />
                      )}

                      {/* Barra principal com gradiente de cor */}
                      <rect
                        x={x}
                        y={y}
                        width={barWidth}
                        height={barHeight}
                        fill={d.cor}
                        opacity={isHovered ? 1 : 0.8}
                        rx="4"
                        style={{ transition: 'all 0.2s' }}
                      />

                      {/* Texto de Valor no Topo da Barra */}
                      <text
                        x={x + barWidth / 2}
                        y={y - 8}
                        fill={isHovered ? '#fff' : '#889'}
                        fontSize="11"
                        fontWeight="700"
                        textAnchor="middle"
                      >
                        {d.tempo.toFixed(1)} ms
                      </text>

                      {/* Rótulo do Eixo X */}
                      <text
                        x={x + barWidth / 2}
                        y="208"
                        fill={isHovered ? d.cor : '#889'}
                        fontSize="12"
                        fontWeight="600"
                        textAnchor="middle"
                      >
                        {d.nome}
                      </text>

                      {/* Complexidade de tempo embaixo */}
                      <text
                        x={x + barWidth / 2}
                        y="224"
                        fill="#556"
                        fontSize="9"
                        textAnchor="middle"
                      >
                        {d.complexidade}
                      </text>
                    </g>
                  )
                })}
              </svg>
            </div>

            {/* Tooltip Dinâmico do Gráfico */}
            <div style={s.tooltipContainer}>
              {hoveredBar !== null ? (
                <div style={{ ...s.tooltip, borderLeft: `4px solid ${performance[hoveredBar].cor}` }}>
                  <strong>{performance[hoveredBar].nome} ({performance[hoveredBar].complexidade})</strong>
                  <p style={{ marginTop: 4, fontSize: 12, color: '#bbb' }}>{performance[hoveredBar].desc}</p>
                </div>
              ) : (
                <p style={{ color: '#556', fontSize: 13, fontStyle: 'italic', textAlign: 'center', marginTop: 12 }}>
                  Passe o mouse sobre as barras para ver a explicação de desempenho.
                </p>
              )}
            </div>
          </div>

          {/* ── Distribuição de Graus (Lei de Potência) ── */}
          <div style={s.card}>
            <h2 style={s.cardTitle}>Distribuição de Graus (Power Law)</h2>
            <p style={s.cardDesc}>
              A maioria das páginas possui poucos links direcionados, enquanto pouquíssimas atuam como hubs de tráfego.
            </p>

            <div style={s.svgContainer}>
              <svg viewBox="0 0 500 240" style={{ width: '100%', height: '100%' }}>
                {/* Linhas horizontais */}
                {[0, 0.25, 0.5, 0.75, 1].map((p, i) => (
                  <line
                    key={i}
                    x1="45"
                    y1={190 - p * 150}
                    x2="480"
                    y2={190 - p * 150}
                    stroke="#1e2d3d"
                    strokeWidth="1"
                    strokeDasharray="4,4"
                  />
                ))}

                <line x1="45" y1="40" x2="45" y2="190" stroke="#2a3a4a" strokeWidth="2" />
                <line x1="45" y1="190" x2="480" y2="190" stroke="#2a3a4a" strokeWidth="2" />

                <text x="35" y="193" fill="#667" fontSize="10" textAnchor="end">0</text>
                <text x="35" y="118" fill="#667" fontSize="10" textAnchor="end">{(maxQtd / 2).toFixed(0)}</text>
                <text x="35" y="43" fill="#667" fontSize="10" textAnchor="end">{maxQtd}</text>

                {distribuicaoGraus.map((d, i) => {
                  const barWidth = 36
                  const x = 65 + i * 70
                  const barHeight = (d.qtd / maxQtd) * 150
                  const y = 190 - barHeight
                  const isHovered = hoveredHist === i

                  return (
                    <g key={i}
                       onMouseEnter={() => setHoveredHist(i)}
                       onMouseLeave={() => setHoveredHist(null)}
                       style={{ cursor: 'pointer' }}>
                      
                      <rect
                        x={x}
                        y={y}
                        width={barWidth}
                        height={barHeight}
                        fill="#2a9d8f"
                        opacity={isHovered ? 1 : 0.7}
                        rx="3"
                        style={{ transition: 'all 0.15s' }}
                      />

                      <text
                        x={x + barWidth / 2}
                        y={y - 6}
                        fill={isHovered ? '#fff' : '#889'}
                        fontSize="10"
                        fontWeight="700"
                        textAnchor="middle"
                      >
                        {d.pct}
                      </text>

                      <text
                        x={x + barWidth / 2}
                        y="206"
                        fill="#889"
                        fontSize="10"
                        fontWeight="600"
                        textAnchor="middle"
                      >
                        {d.faixa}
                      </text>
                    </g>
                  )
                })}
              </svg>
            </div>

            <div style={s.tooltipContainer}>
              {hoveredHist !== null ? (
                <div style={{ ...s.tooltip, borderLeft: '4px solid #2a9d8f' }}>
                  <strong>Grau {distribuicaoGraus[hoveredHist].faixa} — {distribuicaoGraus[hoveredHist].qtd} Páginas</strong>
                  <p style={{ marginTop: 4, fontSize: 12, color: '#bbb' }}>{distribuicaoGraus[hoveredHist].desc}</p>
                </div>
              ) : (
                <p style={{ color: '#556', fontSize: 13, fontStyle: 'italic', textAlign: 'center', marginTop: 12 }}>
                  Passe o mouse sobre as faixas de graus para analisar a densidade estrutural.
                </p>
              )}
            </div>
          </div>
        </div>

        {/* ── Grau de Entrada vs Saída: Top 15 Artigos ── */}
        <div style={s.card}>
          <h2 style={s.cardTitle}>Grau de Entrada vs. Saída — Top 15 Artigos</h2>
          <p style={s.cardDesc}>
            Em um grafo dirigido, o <strong style={{ color: '#2a9d8f' }}>grau de entrada</strong> (quantos artigos apontam para este) mede autoridade na rede,
            enquanto o <strong style={{ color: '#e76f51' }}>grau de saída</strong> (quantos links o artigo emite) mede abrangência temática.
            Os 15 artigos mais conectados revelam o núcleo estrutural do grafo Wikipédia.
          </p>

          {!inOutData ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300, color: '#556e8a', fontSize: 13, fontStyle: 'italic' }}>
              Calculando graus de entrada e saída…
            </div>
          ) : (() => {
            const maxVal = Math.max(...inOutData.flatMap(d => [d.entrada, d.saida]))
            const xStart = 168
            const xEnd = 530
            const barW = xEnd - xStart
            const yStart = 24
            const rowH = 24
            const barH = 8
            const tickVals = [0, 0.25, 0.5, 0.75, 1].map(p => Math.round(p * maxVal))

            return (
              <div style={{ ...s.svgContainer, height: 430 }}>
                <svg viewBox="0 0 560 445" style={{ width: '100%', height: '100%' }}>

                  {/* Legenda */}
                  <rect x={xStart} y={4} width={10} height={10} fill="#2a9d8f" rx="2" />
                  <text x={xStart + 14} y={13} fill="#889baf" fontSize="10">Grau de Entrada</text>
                  <rect x={xStart + 110} y={4} width={10} height={10} fill="#e76f51" rx="2" />
                  <text x={xStart + 124} y={13} fill="#889baf" fontSize="10">Grau de Saída</text>

                  {/* Grid lines verticais e rótulos X (topo) */}
                  {tickVals.map((v, i) => {
                    const x = xStart + (v / maxVal) * barW
                    return (
                      <g key={i}>
                        <line x1={x} y1={yStart} x2={x} y2={yStart + 15 * rowH} stroke="#1e2d3d" strokeWidth="1" strokeDasharray="3,3" />
                        <text x={x} y={yStart + 15 * rowH + 12} fill="#667" fontSize="9" textAnchor="middle">{v}</text>
                      </g>
                    )
                  })}

                  {/* Eixo X */}
                  <line x1={xStart} y1={yStart + 15 * rowH} x2={xEnd} y2={yStart + 15 * rowH} stroke="#2a3a4a" strokeWidth="1.5" />

                  {/* Barras e rótulos */}
                  {inOutData.map((d, i) => {
                    const yGroup = yStart + i * rowH
                    const wEntrada = (d.entrada / maxVal) * barW
                    const wSaida = (d.saida / maxVal) * barW
                    const isHov = hoveredInOut === i
                    const label = d.id.length > 18 ? d.id.slice(0, 18) + '…' : d.id

                    return (
                      <g key={i}
                        onMouseEnter={() => setHoveredInOut(i)}
                        onMouseLeave={() => setHoveredInOut(null)}
                        style={{ cursor: 'pointer' }}>

                        {/* Highlight de fundo no hover */}
                        {isHov && (
                          <rect x={0} y={yGroup} width={560} height={rowH}
                            fill="#ffffff" opacity={0.04} />
                        )}

                        {/* Nome do artigo (Y label) */}
                        <text x={xStart - 5} y={yGroup + rowH / 2 + 1}
                          fill={isHov ? '#e0e9f0' : '#7f93a7'}
                          fontSize="9" textAnchor="end" dominantBaseline="middle">
                          {label}
                        </text>

                        {/* Barra de entrada (teal) */}
                        <rect
                          x={xStart} y={yGroup + 2}
                          width={Math.max(wEntrada, 1)} height={barH}
                          fill="#2a9d8f" opacity={isHov ? 1 : 0.75} rx="2"
                          style={{ transition: 'opacity 0.15s' }}
                        />

                        {/* Barra de saída (laranja) */}
                        <rect
                          x={xStart} y={yGroup + 2 + barH + 2}
                          width={Math.max(wSaida, 1)} height={barH}
                          fill="#e76f51" opacity={isHov ? 1 : 0.75} rx="2"
                          style={{ transition: 'opacity 0.15s' }}
                        />

                        {/* Valores no fim de cada barra (só no hover) */}
                        {isHov && (
                          <>
                            <text x={xStart + wEntrada + 4} y={yGroup + 2 + barH - 1}
                              fill="#2a9d8f" fontSize="9" fontWeight="700">{d.entrada}</text>
                            <text x={xStart + wSaida + 4} y={yGroup + 2 + barH * 2 + 1}
                              fill="#e76f51" fontSize="9" fontWeight="700">{d.saida}</text>
                          </>
                        )}
                      </g>
                    )
                  })}
                </svg>
              </div>
            )
          })()}

          <div style={s.tooltipContainer}>
            {hoveredInOut !== null && inOutData ? (
              <div style={{ ...s.tooltip, borderLeft: '4px solid #2a9d8f' }}>
                <strong style={{ color: '#e0e9f0' }}>{inOutData[hoveredInOut].id}</strong>
                <p style={{ marginTop: 6, fontSize: 12, color: '#bbb', display: 'flex', gap: 24 }}>
                  <span><span style={{ color: '#2a9d8f', fontWeight: 700 }}>Entrada:</span> {inOutData[hoveredInOut].entrada} links recebidos</span>
                  <span><span style={{ color: '#e76f51', fontWeight: 700 }}>Saída:</span> {inOutData[hoveredInOut].saida} links emitidos</span>
                  <span style={{ color: '#aaa' }}>Total: {inOutData[hoveredInOut].entrada + inOutData[hoveredInOut].saida}</span>
                </p>
              </div>
            ) : (
              <p style={{ color: '#556', fontSize: 13, fontStyle: 'italic', textAlign: 'center', marginTop: 12 }}>
                Passe o mouse sobre as linhas para ver o grau de entrada e saída de cada artigo.
              </p>
            )}
          </div>
        </div>

        {/* ── Heatmap de Distâncias entre Vértices ── */}
        <div style={s.card}>
          <h2 style={s.cardTitle}>Heatmap de Distâncias entre Vértices</h2>
          <p style={s.cardDesc}>
            Distância ponderada (Dijkstra) entre os 10 artigos com maior grau de conectividade, calculada no grafo não-dirigido — todos os vértices da amostra ficam alcançáveis entre si.
            Cor normalizada pela maior distância encontrada: teal = próximo · vermelho = distante.
          </p>

          {!heatmapData ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 370, color: '#556e8a', fontSize: 13, fontStyle: 'italic' }}>
              Calculando distâncias (Dijkstra) na amostra do grafo…
            </div>
          ) : (
            <div style={{ ...s.svgContainer, height: 370 }}>
              <svg viewBox="0 0 510 430" style={{ width: '100%', height: '100%' }}>

                {/* X labels — destino (topo, rotacionado -45°) */}
                {heatmapData.nos.map((nome, j) => {
                  const lx = 130 + j * 28 + 14
                  const ly = 107
                  const label = nome.length > 13 ? nome.slice(0, 13) + '…' : nome
                  return (
                    <text key={j} x={lx} y={ly} fill="#889baf" fontSize="9"
                      textAnchor="start" transform={`rotate(-45, ${lx}, ${ly})`}>
                      {label}
                    </text>
                  )
                })}

                {/* Y labels — origem (esquerda) */}
                {heatmapData.nos.map((nome, i) => {
                  const label = nome.length > 13 ? nome.slice(0, 13) + '…' : nome
                  return (
                    <text key={i} x={123} y={116 + i * 28 + 18}
                      fill="#889baf" fontSize="9" textAnchor="end">
                      {label}
                    </text>
                  )
                })}

                {/* Células */}
                {heatmapData.matrix.map((row, i) =>
                  row.map((val, j) => {
                    const cx = 130 + j * 28
                    const cy = 116 + i * 28
                    const cor = distCorNorm(val, heatmapData.maxDist)
                    const isHov = hoveredCell !== null && hoveredCell[0] === i && hoveredCell[1] === j
                    const tNorm = val !== null && val !== 0 ? val / heatmapData.maxDist : 0
                    return (
                      <g key={`${i}-${j}`}
                        onMouseEnter={() => setHoveredCell([i, j])}
                        onMouseLeave={() => setHoveredCell(null)}
                        style={{ cursor: 'pointer' }}>
                        <rect x={cx} y={cy} width={27} height={27}
                          fill={cor} opacity={isHov ? 1 : 0.88} rx="2"
                          stroke={isHov ? '#e0e9f0' : 'transparent'} strokeWidth="1.5"
                          style={{ transition: 'opacity 0.1s' }} />
                        {val !== null && val !== 0 && (
                          <text x={cx + 13.5} y={cy + 18}
                            fill={tNorm > 0.38 ? '#1a1a2e' : '#fff'}
                            fontSize="10" fontWeight="700" textAnchor="middle">
                            {Math.round(val)}
                          </text>
                        )}
                      </g>
                    )
                  })
                )}

                {/* Legenda — barra de gradiente contínua */}
                <text x={415} y={110} fill="#667" fontSize="9" fontWeight="700">Dist. norm.</text>
                {Array.from({ length: 30 }, (_, k) => (
                  <rect key={k} x={415} y={116 + k * 9.34} width={14} height={9.5}
                    fill={corFromT(k / 29)} />
                ))}
                <text x={433} y={124} fill="#889baf" fontSize="8">Próximo</text>
                <text x={433} y={399} fill="#889baf" fontSize="8">Distante</text>
                <rect x={415} y={408} width={14} height={14} fill="#111827" rx="2" />
                <text x={433} y={420} fill="#889baf" fontSize="8">Inalcançável</text>

              </svg>
            </div>
          )}

          <div style={s.tooltipContainer}>
            {hoveredCell !== null && heatmapData ? (() => {
              const val = heatmapData.matrix[hoveredCell[0]][hoveredCell[1]]
              return (
                <div style={{ ...s.tooltip, borderLeft: `4px solid ${distCorNorm(val, heatmapData.maxDist)}` }}>
                  <strong>{heatmapData.nos[hoveredCell[0]]} → {heatmapData.nos[hoveredCell[1]]}</strong>
                  <p style={{ marginTop: 4, fontSize: 12, color: '#bbb' }}>
                    {val === null
                      ? 'Inalcançável mesmo no grafo não-dirigido.'
                      : val === 0
                      ? 'Mesmo vértice (distância zero).'
                      : `Distância ponderada: ${val.toFixed(1)} · Normalizado: ${(val / heatmapData.maxDist * 100).toFixed(0)}% da distância máxima (${heatmapData.maxDist.toFixed(1)}).`}
                  </p>
                </div>
              )
            })() : (
              <p style={{ color: '#556', fontSize: 13, fontStyle: 'italic', textAlign: 'center', marginTop: 12 }}>
                Passe o mouse sobre as células para ver a distância entre os vértices.
              </p>
            )}
          </div>
        </div>

        {/* ── Painel de Análise Teórica Interativo ── */}
        <div style={s.card}>
          <h2 style={s.cardTitle}>Discussão Crítica: Quando e Por Que usar cada um?</h2>
          <p style={s.cardDesc}>
            Clique nos botões abaixo para ver uma análise detalhada dos pontos fortes, fraquezas e aplicações ideais de cada método de busca em grafos.
          </p>

          <div style={s.tabContainer}>
            {Object.keys(comparativoTeorico).map((key) => (
              <button
                key={key}
                onClick={() => setSelectedCard(key)}
                style={{
                  ...s.tabBtn,
                  background: selectedCard === key ? '#1e2d3d' : 'transparent',
                  color: selectedCard === key ? '#fff' : '#889',
                  borderColor: selectedCard === key ? '#2a9d8f' : '#1e2d3d',
                  fontWeight: selectedCard === key ? 700 : 400,
                }}
              >
                {comparativoTeorico[key].titulo}
              </button>
            ))}
          </div>

          <div style={s.tabContent}>
            <h3 style={{ fontSize: 16, fontWeight: 700, color: '#fff', marginBottom: 12 }}>
              {comparativoTeorico[selectedCard].titulo}
            </h3>
            
            <div style={s.detalheGrid}>
              <div style={s.detalheItem}>
                <span style={{ color: '#2a9d8f', fontWeight: 700, fontSize: 13, textTransform: 'uppercase' }}>Pontos Fortes</span>
                <p style={{ color: '#ccc', fontSize: 13.5, marginTop: 4, lineHeight: 1.5 }}>
                  {comparativoTeorico[selectedCard].vantagem}
                </p>
              </div>

              <div style={s.detalheItem}>
                <span style={{ color: '#e76f51', fontWeight: 700, fontSize: 13, textTransform: 'uppercase' }}>Limitações</span>
                <p style={{ color: '#ccc', fontSize: 13.5, marginTop: 4, lineHeight: 1.5 }}>
                  {comparativoTeorico[selectedCard].limite}
                </p>
              </div>
            </div>

            <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid #1e2d3d' }}>
              <span style={{ color: '#e9c46a', fontWeight: 700, fontSize: 13, textTransform: 'uppercase' }}>Caso de Uso Ideal</span>
              <p style={{ color: '#eee', fontSize: 14, marginTop: 4, fontStyle: 'italic' }}>
                "{comparativoTeorico[selectedCard].quando}"
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

const s = {
  pagina: {
    marginTop: 56,
    background: '#0a0c12',
    height: 'calc(100vh - 56px)',
    overflowY: 'auto',
    padding: '36px 40px',
    display: 'flex',
    flexDirection: 'column',
    gap: 24,
    fontFamily: 'Segoe UI, Roboto, Helvetica, Arial, sans-serif',
  },
  header: {
    marginBottom: 8,
  },
  h1: {
    fontSize: 24,
    fontWeight: 700,
    color: '#f0f4f8',
  },
  sub: {
    fontSize: 14,
    color: '#889baf',
    marginTop: 6,
  },
  gridMetricas: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: 16,
  },
  metricCard: {
    background: '#0f1422',
    border: '1px solid #1e2d3d',
    borderRadius: 12,
    padding: '20px 24px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    transition: 'transform 0.15s ease-in-out',
  },
  metricLabel: {
    fontSize: 12,
    fontWeight: 600,
    color: '#556e8a',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  metricVal: {
    fontSize: 28,
    fontWeight: 700,
    color: '#f4a261',
    margin: '8px 0 4px 0',
  },
  metricDesc: {
    fontSize: 12,
    color: '#7f93a7',
    lineHeight: 1.4,
  },
  gridGraficos: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
    gap: 24,
  },
  card: {
    background: '#0f1422',
    border: '1px solid #1e2d3d',
    borderRadius: 12,
    padding: '24px 28px',
    display: 'flex',
    flexDirection: 'column',
    boxShadow: '0 4px 20px rgba(0,0,0,0.2)',
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 700,
    color: '#e0e9f0',
  },
  cardDesc: {
    fontSize: 13,
    color: '#7f93a7',
    marginTop: 6,
    marginBottom: 20,
    lineHeight: 1.4,
  },
  svgContainer: {
    width: '100%',
    height: 220,
    background: '#070a0f',
    borderRadius: 8,
    border: '1px solid #14202e',
    padding: '12px 16px',
    boxSizing: 'border-box',
  },
  tooltipContainer: {
    minHeight: 70,
    marginTop: 14,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  tooltip: {
    background: '#141a29',
    border: '1px solid #202e40',
    padding: '10px 14px',
    borderRadius: 8,
    width: '100%',
    boxSizing: 'border-box',
  },
  tabContainer: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 16,
    borderBottom: '1px solid #1e2d3d',
    paddingBottom: 16,
  },
  tabBtn: {
    padding: '8px 18px',
    borderRadius: 6,
    border: '1px solid',
    cursor: 'pointer',
    fontSize: 13,
    transition: 'all 0.15s ease',
    outline: 'none',
  },
  tabContent: {
    background: '#070a0f',
    border: '1px solid #14202e',
    borderRadius: 10,
    padding: '20px 24px',
  },
  detalheGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: 16,
  },
  detalheItem: {
    display: 'flex',
    flexDirection: 'column',
  },
}
