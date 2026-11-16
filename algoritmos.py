"""Algoritmos próprios de busca e ordenação (nenhum usa sorted()/list.sort()).

Ordenação: Merge Sort e Insertion Sort, ambos religando nós da lista encadeada.
Ambos são ESTÁVEIS: registros com chave igual mantêm a ordem relativa.
"""

import unicodedata


def normalizar(texto):
    """Minúsculas e sem acentos, para comparar 'Saude' == 'saúde'."""
    decomposto = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in decomposto if not unicodedata.combining(c)).casefold()


# ======================= BUSCA =======================
def busca_sequencial(lista, atributo, termo):
    """Percorre a lista inteira e devolve (Python list) os registros cujo
    `atributo` contém `termo` (sem diferenciar acento/maiúscula).
    Complexidade: O(n * m), n = nº de registros, m = tamanho do texto; ~O(n).
    Sem correspondência, devolve lista vazia (quem chama decide a mensagem)."""
    alvo = normalizar(termo).strip()
    achados = []
    if not alvo:
        return achados
    for reg in lista:
        if alvo in normalizar(getattr(reg, atributo)):
            achados.append(reg)
    return achados


# ======================= ORDENAÇÃO =======================
def _vem_antes_ou_igual(a, b, chave, reverso):
    ka, kb = chave(a), chave(b)
    return ka >= kb if reverso else ka <= kb


def _dividir(cabeca):
    """Divide a lista ao meio com ponteiros lento/rápido. O(n)."""
    lento, rapido = cabeca, cabeca.proximo
    while rapido is not None and rapido.proximo is not None:
        lento = lento.proximo
        rapido = rapido.proximo.proximo
    segunda = lento.proximo
    lento.proximo = None
    return cabeca, segunda


def _intercalar(a, b, chave, reverso):
    """Intercala duas listas já ordenadas, religando nós. O(n)."""
    from lista_encadeada import No
    sentinela = No(None)
    ponta = sentinela
    while a is not None and b is not None:
        if _vem_antes_ou_igual(a.dado, b.dado, chave, reverso):  # <= garante estabilidade
            ponta.proximo, a = a, a.proximo
        else:
            ponta.proximo, b = b, b.proximo
        ponta = ponta.proximo
    ponta.proximo = a if a is not None else b
    return sentinela.proximo


def merge_sort(cabeca, chave, reverso=False):
    """Merge Sort em lista encadeada. Tempo O(n log n) em todos os casos;
    espaço extra O(log n) (pilha de recursão), pois só religa nós."""
    if cabeca is None or cabeca.proximo is None:
        return cabeca
    esquerda, direita = _dividir(cabeca)
    return _intercalar(merge_sort(esquerda, chave, reverso),
                       merge_sort(direita, chave, reverso), chave, reverso)


def insertion_sort(cabeca, chave, reverso=False):
    """Insertion Sort em lista encadeada, religando nós.
    Mantém um ponteiro para o ÚLTIMO nó da parte já ordenada: se o nó atual
    pertence ao fim, entra em O(1). Assim:
      melhor caso (entrada já ordenada): O(n);  pior/médio: O(n²);  espaço extra: O(1).
    É estável (chaves iguais entram depois das existentes)."""
    ordenada = ultimo = None
    atual = cabeca
    while atual is not None:
        proximo = atual.proximo
        atual.proximo = None
        if ordenada is None:                                     # primeiro nó
            ordenada = ultimo = atual
        elif _vem_antes_ou_igual(ultimo.dado, atual.dado, chave, reverso):
            ultimo.proximo = atual                               # vai para o fim: O(1)
            ultimo = atual
        elif not _vem_antes_ou_igual(ordenada.dado, atual.dado, chave, reverso):
            atual.proximo = ordenada                             # vai para a frente: O(1)
            ordenada = atual
        else:                                                    # meio: varre a parte ordenada
            p = ordenada
            while _vem_antes_ou_igual(p.proximo.dado, atual.dado, chave, reverso):
                p = p.proximo
            atual.proximo = p.proximo
            p.proximo = atual
        atual = proximo
    return ordenada


# Chaves de ordenação disponíveis no menu
CHAVES = {
    "id": lambda r: r.id,
    "titulo": lambda r: normalizar(r.titulo),
    "categoria": lambda r: (normalizar(r.categoria), normalizar(r.titulo)),
}
