#!/usr/bin/env bash
# Roda o TradingAgents e publica o relatório (com tarja) em reports/ + index.html.
# Uso: ./analisar.sh TICKER [AAAA-MM-DD] [analistas]
#   ./analisar.sh HOOD
#   ./analisar.sh BBAS3.SA 2026-10-05 market,news
# Padrões: data = ontem (D-1), analistas = market,news,fundamentals. Tickers da B3 levam o sufixo .SA.
set -euo pipefail
TICKER="${1:?uso: ./analisar.sh TICKER [AAAA-MM-DD] [analistas]}"
DATA="${2:-$(date -d yesterday +%F)}"
ANALISTAS="${3:-market,news,fundamentals}"
AQUI="$(cd "$(dirname "$0")" && pwd)"
TA="$HOME/DEV-PESSOAL/tradingagents"
ENVF="$TA/.env"
# lê só os nomes dos modelos do .env (nunca a chave)
modelo() { grep -E "^$1=" "$ENVF" | head -1 | cut -d= -f2-; }
MODELOS="$(modelo TRADINGAGENTS_QUICK_THINK_LLM) / $(modelo TRADINGAGENTS_DEEP_THINK_LLM)"

INICIO="$(mktemp)"; trap 'rm -f "$INICIO"' EXIT
cd "$TA" && source .venv/bin/activate
echo ">> Analisando $TICKER em $DATA ($ANALISTAS) — leva de 2 a 5 minutos"
TRADINGAGENTS_OUTPUT_LANGUAGE="${TRADINGAGENTS_OUTPUT_LANGUAGE:-Portuguese}" \
TRADINGAGENTS_MAX_DEBATE_ROUNDS="${TRADINGAGENTS_MAX_DEBATE_ROUNDS:-1}" \
TRADINGAGENTS_MAX_RISK_ROUNDS="${TRADINGAGENTS_MAX_RISK_ROUNDS:-1}" \
  tradingagents --ticker "$TICKER" --date "$DATA" --analysts "$ANALISTAS" --save --no-show 2>&1 \
  | grep -v -E "^[│╭╰]|automatic function"

# relatório mais novo deste ticker, criado depois do início da execução
PASTA="$(find "$HOME/.tradingagents/logs/reports" -maxdepth 1 -type d -name "${TICKER}_*" -newer "$INICIO" | sort | tail -1 || true)"
[ -n "$PASTA" ] || { echo "ERRO: relatório não encontrado (a análise falhou?)"; exit 1; }
python3 "$AQUI/aplicar_tarja.py" "$PASTA" --modelos "$MODELOS"
echo ">> Pronto. Abra: $AQUI/reports/$(basename "$PASTA" | sed -E 's/_([0-9]{8})_[0-9]{6}$/_\1/').html"
echo ">> Falta só commitar e dar push da pasta $AQUI (feito por você)."
