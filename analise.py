"""Processamento: informações úteis a partir da lista."""
from modelo import CATEGORIAS


def contar_por_categoria(lista):
    """Percorre a lista uma vez. O(n). Inclui categorias com zero registros."""
    contagem = {c: 0 for c in CATEGORIAS}
    for reg in lista:
        contagem[reg.categoria] += 1
    return contagem


def resumo(lista):
    total = len(lista)
    contagem = contar_por_categoria(lista)
    maior = None
    for cat, qtd in contagem.items():
        if qtd > 0 and (maior is None or qtd > contagem[maior]):
            maior = cat
    return {"total": total, "por_categoria": contagem, "categoria_predominante": maior}


def formatar_resumo(lista):
    r = resumo(lista)
    if r["total"] == 0:
        return "Nenhum registro cadastrado ainda."
    linhas = [f"Total de registros: {r['total']}", "Distribuição por categoria:"]
    for cat, qtd in r["por_categoria"].items():
        pct = qtd * 100 / r["total"]
        linhas.append(f"  {cat:<34} {qtd:>3}  ({pct:5.1f}%)  {'█' * qtd}")
    linhas.append(f"Categoria com mais registros: {r['categoria_predominante']}")
    return "\n".join(linhas)
