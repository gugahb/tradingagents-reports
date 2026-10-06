# Relatórios TradingAgents

Relatórios gerados com o [TradingAgents](https://github.com/TauricResearch/TradingAgents) (agentes de IA, modelos leves do Gemini), publicados com uma tarja de aviso.

> ⚠ Experimento de pesquisa. Não é recomendação de investimento nem análise de valores mobiliários. Dados não verificados, podem estar incompletos ou errados.

## Gerar um novo relatório

```bash
./analisar.sh HOOD                       # data = ontem, analistas = market,news,fundamentals
./analisar.sh BBAS3.SA 2026-10-05        # ações da B3 levam o sufixo .SA
./analisar.sh NVDA 2026-10-05 market     # só um analista (mais rápido e barato)
```

O script roda o TradingAgents (clone em `~/DEV-PESSOAL/tradingagents`), copia o HTML para `reports/` com a tarja e regenera o `index.html`. O original em `~/.tradingagents/logs/reports/` não é alterado.

Reprocessar tudo: `python3 aplicar_tarja.py --todos --modelos "quick / deep"`. Só o índice: `python3 aplicar_tarja.py --so-index`.

## Publicar (GitHub Pages)

Faça commit e push desta pasta e ative Pages na raiz da branch. O `index.html` lista os relatórios. Pages grátis exige repo público; pense no aviso acima antes de tornar público.

## Limites

- Fundamentos de ações brasileiras vêm vazios (a fonte é focada em EUA); só a parte técnica é confiável.
- Sem dados macro (falta `FRED_API_KEY`).
- Nenhuma chave de API é lida ou gravada aqui; ficam só no `.env` do clone.
