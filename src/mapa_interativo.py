from pathlib import Path
import pandas as pd
import json

COORDS_AEROPORTOS = {
    "REC": (-34.9236, -8.1264), "SSA": (-38.3225, -12.9086), "FOR": (-38.5326, -3.7763),
    "NAT": (-35.2477, -5.9114), "JPA": (-34.9508, -7.1458), "GRU": (-46.4731, -23.4356),
    "CGH": (-46.6564, -23.6261), "GIG": (-43.2505, -22.8099), "CNF": (-43.9719, -19.6244),
    "VIX": (-40.2864, -20.2581), "BSB": (-47.9186, -15.8711), "GYN": (-49.2206, -16.6319),
    "CWB": (-49.1758, -25.5285), "FLN": (-48.5478, -27.6703), "POA": (-51.1714, -29.9939),
    "MAO": (-60.0497, -3.0386), "BEL": (-48.4761, -1.3792), "PVH": (-63.9023, -8.7093),
    "RBR": (-67.8981, -9.8688), "THE": (-42.8236, -5.0600), "MCZ": (-35.7917, -9.5108),
    "SLZ": (-44.2350, -2.5897), "AJU": (-37.0703, -10.9842), "CGB": (-56.1167, -15.6528),
    "CGR": (-54.6725, -20.4697), "MCP": (-51.0722,  0.0507), "BVB": (-60.6922,  2.8413),
    "PMW": (-48.3569, -10.2915),
}

REGION_COLORS_MAP = {
    "Nordeste":     "#E9C46A",
    "Sudeste":      "#e84393",
    "Centro-Oeste": "#ff6b35",
    "Sul":          "#6c63ff",
    "Norte":        "#00c2a8",
}

ROUTE_COLORS = [
    "#f43f5e", "#f97316", "#eab308", "#22c55e", "#14b8a6",
    "#3b82f6", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16",
]


def gerar_mapa(pasta_projeto: Path) -> Path:
    pasta_out  = pasta_projeto / "out"
    pasta_data = pasta_projeto / "data"

    df_grau = pd.read_csv(pasta_out / "graus.csv")
    df_grau.columns = df_grau.columns.str.strip()

    df_aeroportos = pd.read_csv(pasta_data / "aeroportos_data.csv")
    df_aeroportos.columns = df_aeroportos.columns.str.strip()

    df_grau = df_grau.merge(
        df_aeroportos[["iata", "cidade", "regiao"]],
        left_on="aeroporto", right_on="iata", how="left",
    )

    df_ego = pd.read_csv(pasta_out / "ego_aeroportos.csv")
    df_ego.columns = df_ego.columns.str.strip()
    df_ego = df_ego.map(lambda v: v.strip() if isinstance(v, str) else v)

    df_adj = pd.read_csv(pasta_data / "adjacencias_aeroportos.csv")
    df_adj.columns = df_adj.columns.str.strip()
    df_adj = df_adj.map(lambda v: v.strip() if isinstance(v, str) else v)

    df_distancias = pd.read_csv(pasta_out / "distancias_rotas.csv")

    df = df_grau[["aeroporto", "grau", "cidade", "regiao"]].copy()
    df = df.merge(df_ego[["aeroporto", "densidade_ego"]], on="aeroporto", how="left")
    df["densidade_ego"] = df["densidade_ego"].astype(float)

    ap_data: dict = {}
    for _, row in df.iterrows():
        iata = row["aeroporto"]
        if iata not in COORDS_AEROPORTOS:
            continue
        lon, lat = COORDS_AEROPORTOS[iata]
        ap_data[iata] = {
            "cidade":        row["cidade"],
            "regiao":        row["regiao"],
            "lat":           lat,
            "lon":           lon,
            "color":         REGION_COLORS_MAP.get(row["regiao"], "#aaaaaa"),
            "grau":          int(row["grau"]),
            "densidade_ego": round(float(row["densidade_ego"]), 4),
        }

    edges_data = []
    for _, row in df_adj.iterrows():
        o = row["origem"].strip()
        d = row["destino"].strip()
        if o in ap_data and d in ap_data:
            edges_data.append({
                "from": o, "to": d,
                "tipo": row["tipo_conexao"].strip(),
                "peso": float(row["peso"]),
            })

    routes_data = []
    for i, (_, row) in enumerate(df_distancias.iterrows()):
        path = [n.strip() for n in row["caminho"].split("->")]
        routes_data.append({
            "label": f"{row['origem']} -> {row['destino']}",
            "path":  path,
            "custo": int(float(row["custo"])),
            "color": ROUTE_COLORS[i % len(ROUTE_COLORS)],
        })

    legend_data = [{"color": c, "label": r} for r, c in REGION_COLORS_MAP.items()]

    ap_json     = json.dumps(ap_data,     ensure_ascii=False)
    edges_json  = json.dumps(edges_data,  ensure_ascii=False)
    routes_json = json.dumps(routes_data, ensure_ascii=False)
    legend_json = json.dumps(legend_data, ensure_ascii=False)

    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
:root{{--bg:#0e1117;--surf:#161b22;--border:#30363d;--accent:#6c63ff;--text:#f0f6fc;--muted:#8b949e}}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{height:100%;overflow:hidden;font-family:'Segoe UI',sans-serif;
           background:var(--bg);color:var(--text);font-size:13px}}
#wrap{{display:flex;flex-direction:column;height:100vh}}
#topbar{{display:flex;align-items:center;gap:8px;padding:8px 14px;
         background:var(--surf);border-bottom:1px solid var(--border);
         flex-shrink:0;flex-wrap:wrap}}
#topbar-logo{{font-weight:800;font-size:.95rem;
              background:linear-gradient(90deg,#6c63ff,#00c2a8);
              -webkit-background-clip:text;-webkit-text-fill-color:transparent;
              white-space:nowrap;margin-right:4px}}
#search-box{{background:var(--bg);border:1px solid var(--border);color:var(--text);
             font-size:.75rem;padding:5px 10px;border-radius:4px;width:190px;
             outline:none;font-family:inherit;transition:border .2s}}
#search-box:focus{{border-color:var(--accent)}}
#search-box::placeholder{{color:#475569}}
#search-clear{{background:none;border:none;color:var(--muted);cursor:pointer;
               font-size:.85rem;padding:0 4px;display:none}}
.tbtn{{background:var(--bg);border:1px solid var(--border);color:var(--text);
       font-size:.7rem;padding:5px 11px;border-radius:4px;cursor:pointer;
       white-space:nowrap;transition:all .15s;font-family:inherit}}
.tbtn:hover{{background:var(--border)}}
.tbtn.active{{background:var(--accent);border-color:var(--accent);color:#fff}}
#main{{display:flex;flex:1;overflow:hidden;min-height:0}}
#plotly-map{{flex:1;min-width:0;min-height:0}}
#sidebar{{width:255px;background:var(--surf);border-left:1px solid var(--border);
          overflow-y:auto;padding:12px 10px;display:flex;
          flex-direction:column;gap:12px;flex-shrink:0}}
.stitle{{font-size:.6rem;text-transform:uppercase;letter-spacing:.15em;
         color:var(--muted);margin-bottom:6px;font-weight:700}}
.ibox{{background:var(--bg);border:1px solid var(--border);border-radius:5px;
       padding:9px;font-size:.68rem;line-height:1.75;color:var(--muted)}}
.ibox b{{color:var(--text)}}
.reg-filter{{display:flex;align-items:center;gap:6px;background:var(--bg);
             border:1px solid var(--border);color:var(--muted);font-size:.63rem;
             padding:4px 8px;border-radius:4px;cursor:pointer;width:100%;
             margin-bottom:3px;transition:all .15s;font-family:inherit;opacity:.35}}
.reg-filter.active{{color:var(--text);opacity:1;border-color:rgba(255,255,255,.12)}}
.reg-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0}}
.route-btn{{display:flex;align-items:center;gap:7px;width:100%;
            background:var(--bg);border:1px solid var(--border);
            border-radius:5px;padding:6px 9px;margin-bottom:4px;
            cursor:pointer;font-size:.65rem;color:var(--muted);
            text-align:left;transition:all .15s;font-family:inherit}}
.route-btn:hover{{border-color:#4a5568;color:var(--text)}}
.route-btn.active{{color:var(--text);font-weight:700;border-left-width:3px}}
.rdot{{width:9px;height:9px;border-radius:50%;flex-shrink:0}}
.rcost{{margin-left:auto;font-size:.6rem;opacity:.7;white-space:nowrap}}
.ap-row{{display:flex;align-items:center;gap:6px;padding:4px 6px;border-radius:4px;
         cursor:pointer;transition:background .1s;margin-bottom:1px}}
.ap-row:hover{{background:var(--border)}}
.ap-row.ap-sel{{background:rgba(108,99,255,.15);border-left:2px solid var(--accent);
                padding-left:4px}}
.ap-dot-s{{width:8px;height:8px;border-radius:50%;flex-shrink:0}}
.ap-name{{flex:1;min-width:0}}
.ap-iata-s{{font-size:.7rem;font-weight:700;color:var(--text);margin-right:3px}}
.ap-city-s{{font-size:.59rem;color:var(--muted);overflow:hidden;
            text-overflow:ellipsis;white-space:nowrap;display:block}}
.ap-grade{{font-size:.6rem;color:var(--muted);white-space:nowrap;flex-shrink:0}}
#statusbar{{font-size:.62rem;color:var(--muted);padding:4px 14px;
            background:var(--surf);border-top:1px solid var(--border);flex-shrink:0}}
</style>
</head>
<body>
<div id="wrap">

  <div id="topbar">
    <span id="topbar-logo">✈ Aeroportos do Brasil</span>
    <input id="search-box" placeholder="Buscar IATA ou cidade..." oninput="onSearch(this.value)"/>
    <button id="search-clear" onclick="clearSearch()">✕</button>
    <button class="tbtn" onclick="resetAll()">↺ Resetar</button>
  </div>

  <div id="main">
    <div id="plotly-map"></div>
    <div id="sidebar">

      <div>
        <div class="stitle">Filtrar por região</div>
        <div id="region-filters"></div>
      </div>

      <div>
        <div class="stitle">Aeroporto selecionado</div>
        <div class="ibox" id="node-info">Clique ou busque um aeroporto para ver detalhes.</div>
      </div>

      <div>
        <div class="stitle">Caminhos obrigatórios</div>
        <div id="routes-panel"></div>
        <button class="tbtn" style="width:100%;margin-top:2px" onclick="clearRoute()">✕ Limpar rota</button>
      </div>

      <div>
        <div class="stitle">Estatísticas</div>
        <div class="ibox" id="stats-box"></div>
      </div>

      <div>
        <div class="stitle">Aeroportos (<span id="ap-count">28</span>)</div>
        <div id="ap-list"></div>
      </div>

    </div>
  </div>

  <div id="statusbar">Carregando mapa...</div>
</div>

<script>
const AP     = {ap_json};
const EDGES  = {edges_json};
const ROUTES = {routes_json};
const LEGEND = {legend_json};

const GR_MAX = Math.max(...Object.values(AP).map(a => a.grau));
const GR_MIN = Math.min(...Object.values(AP).map(a => a.grau));

let selectedIata   = null;
let activeRouteIdx = null;
let activeRegions  = new Set(LEGEND.map(l => l.label));


const filtersEl = document.getElementById('region-filters');
LEGEND.forEach(it => {{
  const btn = document.createElement('button');
  btn.className = 'reg-filter active';
  btn.dataset.region = it.label;
  btn.innerHTML = `<span class="reg-dot" style="background:${{it.color}}"></span>${{it.label}}`;
  btn.onclick = () => toggleRegion(it.label);
  filtersEl.appendChild(btn);
}});

function toggleRegion(region) {{
  if (activeRegions.has(region)) {{
    if (activeRegions.size === 1) return;
    activeRegions.delete(region);
  }} else {{
    activeRegions.add(region);
  }}
  document.querySelectorAll('.reg-filter').forEach(b =>
    b.classList.toggle('active', activeRegions.has(b.dataset.region))
  );
  buildAirportList();
  Plotly.react('plotly-map', buildData(), baseLayout, config);
}}


const routesPanel = document.getElementById('routes-panel');
ROUTES.forEach((r, i) => {{
  const btn = document.createElement('button');
  btn.className = 'route-btn';
  btn.id = `rbtn-${{i}}`;
  btn.innerHTML =
    `<div class="rdot" style="background:${{r.color}}"></div>`+
    `<span>${{r.label}}</span>`+
    `<span class="rcost">${{r.custo}} min</span>`;
  btn.onclick = () => toggleRoute(i);
  routesPanel.appendChild(btn);
}});


function buildAirportList() {{
  const listEl = document.getElementById('ap-list');
  listEl.innerHTML = '';
  const filtered = Object.entries(AP)
    .filter(([, info]) => activeRegions.has(info.regiao))
    .sort((a, b) => b[1].grau - a[1].grau);
  document.getElementById('ap-count').textContent = filtered.length;
  const filtConns = EDGES.filter(e =>
    activeRegions.has(AP[e.from]?.regiao) && activeRegions.has(AP[e.to]?.regiao)
  ).length;
  document.getElementById('stats-box').innerHTML =
    `Aeroportos: <b>${{filtered.length}}</b> / ${{Object.keys(AP).length}}<br>`+
    `Conexões: <b>${{filtConns}}</b> / ${{EDGES.length}}<br>`+
    `Caminhos obrigatórios: <b>${{ROUTES.length}}</b><br>`+
    `Densidade: <b>0,4127</b>`;
  filtered.forEach(([iata, info]) => {{
    const row = document.createElement('div');
    row.className = 'ap-row' + (iata === selectedIata ? ' ap-sel' : '');
    row.innerHTML =
      `<div class="ap-dot-s" style="background:${{info.color}}"></div>`+
      `<div class="ap-name">`+
        `<span class="ap-iata-s">${{iata}}</span>`+
        `<span class="ap-city-s">${{info.cidade}}</span>`+
      `</div>`+
      `<span class="ap-grade">G:${{info.grau}}</span>`;
    row.onclick = () => highlightVertex(iata);
    listEl.appendChild(row);
  }});
}}

buildAirportList();


function getNeighbors(iata) {{
  const nb = new Set([iata]);
  EDGES.forEach(e => {{
    if (e.from === iata) nb.add(e.to);
    if (e.to   === iata) nb.add(e.from);
  }});
  return nb;
}}


function buildData() {{
  const nb    = selectedIata ? getNeighbors(selectedIata) : null;
  const route = activeRouteIdx !== null ? ROUTES[activeRouteIdx] : null;
  const traces = [];

  if (nb) {{
    const dLat=[],dLon=[],hLat=[],hLon=[];
    EDGES.forEach(e => {{
      const a=AP[e.from],b=AP[e.to];
      if (!a||!b) return;
      if (e.from===selectedIata||e.to===selectedIata) {{
        hLat.push(a.lat,b.lat,null); hLon.push(a.lon,b.lon,null);
      }} else {{
        dLat.push(a.lat,b.lat,null); dLon.push(a.lon,b.lon,null);
      }}
    }});
    if (dLat.length) traces.push({{type:'scattergeo',mode:'lines',lat:dLat,lon:dLon,
      line:{{color:'rgba(30,45,70,0.35)',width:0.7}},hoverinfo:'skip',showlegend:false}});
    if (hLat.length) traces.push({{type:'scattergeo',mode:'lines',lat:hLat,lon:hLon,
      line:{{color:AP[selectedIata].color,width:3}},hoverinfo:'skip',showlegend:false}});
  }} else if (route) {{
    const dLat=[],dLon=[];
    EDGES.forEach(e => {{
      const a=AP[e.from],b=AP[e.to];
      if (!a||!b) return;
      dLat.push(a.lat,b.lat,null); dLon.push(a.lon,b.lon,null);
    }});
    if (dLat.length) traces.push({{type:'scattergeo',mode:'lines',lat:dLat,lon:dLon,
      line:{{color:'rgba(20,30,50,0.25)',width:0.5}},hoverinfo:'skip',showlegend:false}});
    const rp=route.path.filter(p=>AP[p]);
    traces.push({{type:'scattergeo',mode:'lines',
      lat:rp.map(p=>AP[p].lat),lon:rp.map(p=>AP[p].lon),
      line:{{color:route.color,width:4}},hoverinfo:'skip',showlegend:false}});
  }} else {{
    const lat=[],lon=[];
    EDGES.forEach(e => {{
      const a=AP[e.from],b=AP[e.to];
      if (!a||!b) return;
      lat.push(a.lat,b.lat,null); lon.push(a.lon,b.lon,null);
    }});
    if (lat.length) traces.push({{type:'scattergeo',mode:'lines',lat,lon,
      line:{{color:'#2d3a55',width:1}},hoverinfo:'skip',showlegend:false}});
  }}

  const lat=[],lon=[],text=[],htext=[],color=[],sz=[],op=[],cdata=[];
  const routeSet=route ? new Set(route.path) : null;
  Object.entries(AP).forEach(([iata,info]) => {{
    lat.push(info.lat); lon.push(info.lon);
    text.push(iata); cdata.push(iata);
    sz.push(Math.round(8+((info.grau-GR_MIN)/(GR_MAX-GR_MIN||1))*16));
    const inFilter=activeRegions.has(info.regiao);
    let active;
    if (nb) active=nb.has(iata);
    else if (routeSet) active=routeSet.has(iata);
    else active=inFilter;
    color.push(active ? info.color : '#2a3040');
    op.push(nb||routeSet ? (active?1.0:0.12) : (active?1.0:0.06));
    htext.push(
      `<b>${{iata}}</b> — ${{info.cidade}}<br>`+
      `Região: ${{info.regiao}}<br>`+
      `Grau: ${{info.grau}}<br>`+
      `Densidade ego: ${{info.densidade_ego}}`
    );
  }});
  traces.push({{
    type:'scattergeo',mode:'markers+text',
    lat,lon,text,customdata:cdata,hovertext:htext,
    marker:{{size:sz,color,opacity:op,
      line:{{color:'rgba(255,255,255,0.55)',width:1.5}},sizemode:'diameter'}},
    textfont:{{size:8,color:'rgba(255,255,255,0.85)'}},
    textposition:'top center',
    hoverinfo:'text',showlegend:false,name:'airports'
  }});
  return traces;
}}

const baseLayout = {{
  geo:{{
    scope:'world',
    showland:true,  landcolor:'#1a2035',
    showocean:true, oceancolor:'#080f1c',
    showlakes:true, lakecolor:'#0c1525',
    showrivers:false,
    showcountries:true, countrycolor:'#334155',
    showsubunits:true,  subunitcolor:'#253545',
    showcoastlines:true,coastlinecolor:'#2d4060',
    center:{{lat:-15,lon:-52}},
    projection:{{type:'natural earth'}},
    bgcolor:'#0d0d14',
  }},
  paper_bgcolor:'#0d0d14',
  plot_bgcolor:'#0d0d14',
  margin:{{l:0,r:0,t:0,b:0}},
  clickmode:'event',
  dragmode:'zoom',
  uirevision:'static',
  showlegend:false,
}};

const config = {{
  displayModeBar:true,
  modeBarButtonsToRemove:['select2d','lasso2d','toImage'],
  responsive:true,scrollZoom:true,
}};

Plotly.newPlot('plotly-map',buildData(),baseLayout,config).then(()=>{{
  window.dispatchEvent(new Event('resize'));
}});
window.addEventListener('resize',()=>{{ Plotly.Plots.resize('plotly-map'); }});

document.getElementById('plotly-map').on('plotly_click',function(data){{
  if (!data?.points?.length) return;
  const iata=data.points[0].customdata;
  if (!iata||!AP[iata]) return;
  if (selectedIata===iata) {{
    selectedIata=null; updateInfo(null);
  }} else {{
    selectedIata=iata; activeRouteIdx=null;
    document.querySelectorAll('.route-btn').forEach(b=>b.classList.remove('active'));
    updateInfo(iata);
  }}
  buildAirportList();
  Plotly.react('plotly-map',buildData(),baseLayout,config);
}});

function highlightVertex(iata) {{
  if (!AP[iata]) return;
  selectedIata=iata; activeRouteIdx=null;
  document.querySelectorAll('.route-btn').forEach(b=>b.classList.remove('active'));
  updateInfo(iata);
  buildAirportList();
  Plotly.react('plotly-map',buildData(),baseLayout,config);
}}

function updateInfo(iata) {{
  if (!iata) {{
    document.getElementById('node-info').innerHTML=
      'Clique ou busque um aeroporto para ver detalhes.';
    setStatus(`${{Object.keys(AP).length}} aeroportos | ${{EDGES.length}} conexões`);
    return;
  }}
  const info=AP[iata],nb=getNeighbors(iata);
  document.getElementById('node-info').innerHTML=
    `<b style="color:${{info.color}}">${{iata}}</b> — ${{info.cidade}}<br>`+
    `Região: ${{info.regiao}}<br>`+
    `Grau: <b>${{info.grau}}</b><br>`+
    `Densidade ego: <b>${{info.densidade_ego}}</b>`;
  setStatus(`${{iata}} (${{info.cidade}}) — ${{nb.size-1}} conexões. Clique novamente para desfazer.`);
}}

function onSearch(raw) {{
  const q=raw.trim().toUpperCase();
  document.getElementById('search-clear').style.display=q?'inline':'none';
  if (!q) return;
  if (AP[q]) {{highlightVertex(q);return;}}
  const match=Object.entries(AP).find(([,info])=>info.cidade.toUpperCase().includes(q));
  if (match) highlightVertex(match[0]);
}}

function clearSearch() {{
  document.getElementById('search-box').value='';
  document.getElementById('search-clear').style.display='none';
  selectedIata=null; updateInfo(null);
  buildAirportList();
  Plotly.react('plotly-map',buildData(),baseLayout,config);
}}

function toggleRoute(idx) {{
  selectedIata=null;
  if (activeRouteIdx===idx) {{
    activeRouteIdx=null;
    document.querySelectorAll('.route-btn').forEach(b=>b.classList.remove('active'));
    updateInfo(null);
  }} else {{
    activeRouteIdx=idx;
    document.querySelectorAll('.route-btn').forEach((b,i)=>b.classList.toggle('active',i===idx));
    const r=ROUTES[idx];
    document.getElementById('node-info').innerHTML=
      `Caminho: <b>${{r.path.join(' → ')}}</b><br>Custo: <b>${{r.custo}} min</b>`;
    setStatus(`${{r.label}}: ${{r.path.join(' → ')}} (${{r.custo}} min)`);
  }}
  buildAirportList();
  Plotly.react('plotly-map',buildData(),baseLayout,config);
}}

function clearRoute() {{
  activeRouteIdx=null;
  document.querySelectorAll('.route-btn').forEach(b=>b.classList.remove('active'));
  if (!selectedIata) updateInfo(null);
  buildAirportList();
  Plotly.react('plotly-map',buildData(),baseLayout,config);
}}

function resetAll() {{
  selectedIata=null; activeRouteIdx=null;
  activeRegions=new Set(LEGEND.map(l=>l.label));
  document.querySelectorAll('.route-btn').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.reg-filter').forEach(b=>b.classList.add('active'));
  document.getElementById('search-box').value='';
  document.getElementById('search-clear').style.display='none';
  updateInfo(null);
  buildAirportList();
  baseLayout.uirevision=Date.now().toString();
  Plotly.react('plotly-map',buildData(),baseLayout,config);
}}

function setStatus(msg){{document.getElementById('statusbar').textContent=msg;}}
setStatus(`Grafo pronto — ${{Object.keys(AP).length}} aeroportos, ${{EDGES.length}} conexões.`);
</script>
</body>
</html>"""

    output = pasta_out / "mapa_interativo.html"
    output.write_text(html, encoding="utf-8")
    return output


if __name__ == "__main__":
    pasta_projeto = Path(__file__).resolve().parent.parent
    saida = gerar_mapa(pasta_projeto)
    print(f"✓ Mapa gerado em {saida}")
