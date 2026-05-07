# Grafos-AVD
Projeto de grafos e avd

# Documentação

- No início do projeto escolhemos adicionar mais aeropotos, para completar o csv e termos aeroportos de todas as capitais do Brasil, tendo uma visualização melhor e completa. Com isso ficam 28 aeroportos no total (tendo repetido 2 aeroportos distintos para o estado de São Paulo)

## 1. Processo de pesquisa:
Decidimos realizar a pesquisa fielmente ao mundo real, então começamos buscando no site https://www.flightconnections.com/pt onde pudemos checar se existiam as conexões entre os aeroportos do nosso csv.

## 2. Inserção dos dados coletados na nossa base e definiçaõ do peso
Ao analisar os dados optamos por usar o tempo médio estimado do voo como peso das arestas que conectam os aeroportos (vértices), esse tempo sempre será representado em minutos.

Com esse e mais alguns dados é possível medir a ordem, tamanho e densidade de cada aeroporto, de cada região e de forma global.

## 3. Análise com os dados construídos
- Aeroporto mais conectado: o aeroporto mais conectado é o de Brasilía com 27 conexões, logo ele se conecta com todos os aeroportos, já que no total (contando com ele mesmo) são 28 aeroportos no csv.
- Aeroporto com maior densidade local: os aeroporto de Macapá (MCP) e o de Boa Vista (BVB), com exatos 0,5 de densidade.