#!/usr/bin/env python3
"""Copia relatórios do TradingAgents para reports/, injeta a tarja de aviso e regenera o index.html.

Uso:
  aplicar_tarja.py <pasta_do_relatorio|complete_report.html> [--modelos "quick / deep"]
  aplicar_tarja.py --todos          # reprocessa tudo em ~/.tradingagents/logs/reports
  aplicar_tarja.py --so-index       # só regenera o index.html

O original em ~/.tradingagents nunca é alterado. Idempotente: rodar de novo não duplica a tarja.
A página tem CSP `style-src 'unsafe-inline'`, então a tarja usa só CSS inline (sem JS/imagens).
"""
import argparse, html, re, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "reports"
ORIGEM = Path.home() / ".tradingagents" / "logs" / "reports"
MARCA = "<!-- TARJA-AVISO -->"
AVISO = ("Experimento de pesquisa gerado por agentes de IA (modelos leves). "
         "Não é recomendação de investimento nem análise de valores mobiliários. "
         "Dados não verificados, podem estar incompletos ou errados. "
         "Decisões de investimento são de responsabilidade exclusiva do leitor.")

CSS = """<style>
.tarja-aviso{position:sticky;top:0;z-index:99;margin:0;padding:.7rem 1rem;background:#fff3cd;color:#5c4400;
border-bottom:2px solid #e0a800;font:600 14px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;text-align:center}
.tarja-aviso small{display:block;font-weight:400;opacity:.85;margin-top:.15rem}
@media (prefers-color-scheme:dark){.tarja-aviso{background:#3b2f00;color:#ffe9a6;border-bottom-color:#b88a00}}
</style>"""


def tarja(modelos: str | None, gerado: str | None) -> str:
    extra = []
    if modelos:
        extra.append(f"Modelos: {html.escape(modelos)}")
    if gerado:
        extra.append(f"Gerado em: {html.escape(gerado)}")
    pe = f"<small>{' · '.join(extra)}</small>" if extra else ""
    return f'{MARCA}{CSS}<div class="tarja-aviso" role="note">⚠ {html.escape(AVISO)}{pe}</div>'


def injetar(texto: str, modelos, gerado) -> str:
    if MARCA in texto:
        return texto
    novo, n = re.subn(r"(<body[^>]*>)", lambda m: m.group(1) + tarja(modelos, gerado), texto, count=1)
    if n != 1:
        sys.exit("ERRO: tag <body> não encontrada; formato do relatório mudou. Nada foi gravado.")
    return novo


def gerado_de(nome_pasta: str):
    """Só a DATA (dd/mm/aaaa); a hora da geração nunca é publicada."""
    m = re.search(r"_(\d{4})(\d{2})(\d{2})(?:_\d{6})?$", nome_pasta)
    return f"{m[3]}/{m[2]}/{m[1]}" if m else None


def nome_publico(nome_pasta: str) -> str:
    """TICKER_AAAAMMDD_HHMMSS -> TICKER_AAAAMMDD (sem hora no nome do arquivo).

    Mesmo ticker no mesmo dia gera o mesmo nome: a execução mais recente sobrescreve."""
    return re.sub(r"_(\d{8})_\d{6}$", r"_\1", nome_pasta)


def sem_hora(texto: str) -> str:
    """Tira a hora do campo 'Generated' que o próprio TradingAgents grava no relatório."""
    return re.sub(r"(<dt>Generated</dt><dd>\d{4}-\d{2}-\d{2})[ T]\d{2}:\d{2}(?::\d{2})?(</dd>)", r"\1\2", texto)


def processar(origem: Path, modelos):
    arq = origem / "complete_report.html" if origem.is_dir() else origem
    if not arq.is_file():
        sys.exit(f"ERRO: {arq} não existe")
    nome = arq.parent.name
    destino = SAIDA / f"{nome_publico(nome)}.html"
    SAIDA.mkdir(exist_ok=True)
    texto = sem_hora(arq.read_text(encoding="utf-8"))
    destino.write_text(injetar(texto, modelos, gerado_de(nome)), encoding="utf-8")
    print(f"ok: {destino.relative_to(AQUI)}")


def titulo(arq: Path) -> str:
    m = re.search(r"<title>(.*?)</title>", arq.read_text(encoding="utf-8"), re.S)
    return html.unescape(m[1]).replace(": TradingAgents report", "").strip() if m else arq.stem


def index():
    itens = sorted(SAIDA.glob("*.html"), key=lambda p: p.name.split("_", 1)[1] if "_" in p.name else p.name, reverse=True)
    linhas = "\n".join(
        f'<li><a href="reports/{html.escape(p.name)}">{html.escape(titulo(p))}</a>'
        f' <span>{html.escape(gerado_de(p.stem) or "")}</span></li>' for p in itens)
    (AQUI / "index.html").write_text(f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Relatórios TradingAgents</title>
<style>
:root{{--bg:#fbfbfa;--ink:#1c2126;--muted:#5d6670;--accent:#087a59}}
@media (prefers-color-scheme:dark){{:root{{--bg:#131a1f;--ink:#e4e8eb;--muted:#9aa6af;--accent:#14c290}}}}
body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}}
main{{max-width:46rem;margin:0 auto;padding:2rem 1.25rem 4rem}}a{{color:var(--accent)}}
li{{margin:.4rem 0}}li span{{color:var(--muted);font-size:.85em;margin-left:.5rem}}
.aviso{{background:#fff3cd;color:#5c4400;border:2px solid #e0a800;padding:.8rem 1rem;border-radius:6px;font-size:.95rem}}
@media (prefers-color-scheme:dark){{.aviso{{background:#3b2f00;color:#ffe9a6;border-color:#b88a00}}}}
</style></head><body><main>
<h1>Relatórios TradingAgents</h1>
<p class="aviso">⚠ {html.escape(AVISO)}</p>
<ul>
{linhas}
</ul></main></body></html>
""", encoding="utf-8")
    print(f"ok: index.html ({len(itens)} relatórios)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("alvo", nargs="?")
    ap.add_argument("--modelos")
    ap.add_argument("--todos", action="store_true")
    ap.add_argument("--so-index", action="store_true")
    a = ap.parse_args()
    if a.todos:
        for d in sorted(ORIGEM.glob("*/complete_report.html")):
            processar(d, a.modelos)
    elif a.alvo:
        processar(Path(a.alvo).expanduser(), a.modelos)
    elif not a.so_index:
        ap.error("informe a pasta do relatório, --todos ou --so-index")
    index()


if __name__ == "__main__":
    main()
