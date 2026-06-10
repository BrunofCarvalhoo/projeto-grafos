/**
 * algoritmos.js
 * Implementações de BFS, DFS, Dijkstra e Bellman-Ford
 * para grafos direcionados com pesos representados como
 * listas de adjacência { id → [{vizinho, peso}] }.
 */

// ── BFS ──────────────────────────────────────────────────────────
export function bfs(adj, origem) {
  const nivel   = { [origem]: 0 }
  const anterior = { [origem]: null }
  const fila    = [origem]
  const ordem   = []

  while (fila.length > 0) {
    const atual = fila.shift()
    ordem.push(atual)
    for (const { vizinho } of (adj[atual] ?? [])) {
      if (!(vizinho in nivel)) {
        nivel[vizinho]    = nivel[atual] + 1
        anterior[vizinho] = atual
        fila.push(vizinho)
      }
    }
  }

  return { nivel, anterior, ordem }
}

// ── DFS ──────────────────────────────────────────────────────────
export function dfs(adj, origem) {
  const profundidade = { [origem]: 0 }
  const anterior     = { [origem]: null }
  const ordem        = []
  const pilha        = [origem]

  while (pilha.length > 0) {
    const atual = pilha.pop()
    if (ordem.includes(atual)) continue
    ordem.push(atual)
    for (const { vizinho } of (adj[atual] ?? [])) {
      if (!(vizinho in profundidade)) {
        profundidade[vizinho] = profundidade[atual] + 1
        anterior[vizinho]     = atual
        pilha.push(vizinho)
      }
    }
  }

  return { profundidade, anterior, ordem }
}

// ── MIN-HEAP (auxiliar para Dijkstra) ───────────────────────────
class MinHeap {
  constructor() { this.h = [] }
  push(custo, no) {
    this.h.push([custo, no])
    let i = this.h.length - 1
    while (i > 0) {
      const p = (i - 1) >> 1
      if (this.h[p][0] <= this.h[i][0]) break
      ;[this.h[p], this.h[i]] = [this.h[i], this.h[p]]
      i = p
    }
  }
  pop() {
    const topo = this.h[0]
    const ult  = this.h.pop()
    if (this.h.length > 0) {
      this.h[0] = ult
      let i = 0
      const n = this.h.length
      while (true) {
        let m = i, l = 2*i+1, r = 2*i+2
        if (l < n && this.h[l][0] < this.h[m][0]) m = l
        if (r < n && this.h[r][0] < this.h[m][0]) m = r
        if (m === i) break
        ;[this.h[m], this.h[i]] = [this.h[i], this.h[m]]
        i = m
      }
    }
    return topo
  }
  get tamanho() { return this.h.length }
}

// ── DIJKSTRA ─────────────────────────────────────────────────────
export function dijkstra(adj, nos, origem) {
  const dist     = {}
  const anterior = {}
  for (const n of nos) { dist[n] = Infinity; anterior[n] = null }
  dist[origem] = 0

  const heap = new MinHeap()
  heap.push(0, origem)

  while (heap.tamanho > 0) {
    const [custoAtual, atual] = heap.pop()
    if (custoAtual > dist[atual]) continue
    for (const { vizinho, peso } of (adj[atual] ?? [])) {
      const novo = dist[atual] + peso
      if (novo < dist[vizinho]) {
        dist[vizinho]     = novo
        anterior[vizinho] = atual
        heap.push(novo, vizinho)
      }
    }
  }

  return { dist, anterior }
}

// ── BELLMAN-FORD ─────────────────────────────────────────────────
export function bellmanFord(adj, nos, arestas, origem) {
  const dist     = {}
  const anterior = {}
  for (const n of nos) { dist[n] = Infinity; anterior[n] = null }
  dist[origem] = 0

  const V = nos.length
  let atualizado = true

  for (let i = 0; i < V - 1 && atualizado; i++) {
    atualizado = false
    for (const { u, v, peso } of arestas) {
      if (dist[u] + peso < dist[v]) {
        dist[v]     = dist[u] + peso
        anterior[v] = u
        atualizado  = true
      }
    }
  }

  // Verificação de ciclo negativo
  let ciclonegativo = false
  for (const { u, v, peso } of arestas) {
    if (dist[u] + peso < dist[v]) { ciclonegativo = true; break }
  }

  return { dist, anterior, ciclonegativo }
}

// ── Reconstruir caminho ──────────────────────────────────────────
export function reconstruirCaminho(anterior, destino) {
  const caminho = []
  let atual = destino
  const vistos = new Set()
  while (atual !== null && !vistos.has(atual)) {
    caminho.push(atual)
    vistos.add(atual)
    atual = anterior[atual]
  }
  return caminho.reverse()
}

// ── Montar lista de adjacência a partir dos links do JSON ────────
export function montarAdj(links) {
  const adj = {}
  const arestas = []
  for (const link of links) {
    const u = link.source?.id ?? link.source
    const v = link.target?.id ?? link.target
    const p = link.peso ?? 1
    if (!adj[u]) adj[u] = []
    adj[u].push({ vizinho: v, peso: p })
    arestas.push({ u, v, peso: p })
  }
  return { adj, arestas }
}
