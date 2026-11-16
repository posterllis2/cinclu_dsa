"""Menu interativo em terminal do Cinclu."""
import os
import analise
import persistencia
from algoritmos import CHAVES, busca_sequencial
from dados_iniciais import carregar_exemplos
from lista_encadeada import IdDuplicadoError
from modelo import CATEGORIAS, LIMITES, Registro

ARQUIVO_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados", "servicos.json")

MENU = """
╭──────────────────────────────────────╮
│   cinclu · Cidade Inclusiva          │
╰──────────────────────────────────────╯
 1. Cadastrar serviço/orientação
 2. Consultar por ID
 3. Atualizar
 4. Excluir
 5. Pesquisar (título ou categoria)
 6. Listar / Ordenar
 7. Análise (resumo por categoria)
 8. Encerrar
"""


# ---------- leitura validada ----------
def ler_texto(msg, campo, obrigatorio=True, atual=None):
    limite = LIMITES.get(campo, 200)
    while True:
        v = input(msg).strip()
        if not v and atual is not None:
            return atual
        if not v and obrigatorio:
            print("  ⚠ Campo obrigatório.")
        elif len(v) > limite:
            print(f"  ⚠ Máximo de {limite} caracteres (você digitou {len(v)}).")
        else:
            return v


def ler_inteiro_positivo(msg):
    while True:
        v = input(msg).strip()
        if v.isdigit() and int(v) > 0:
            return int(v)
        print("  ⚠ Digite um número inteiro positivo.")


def escolher_categoria(atual=None):
    print("Categorias:")
    for i, c in enumerate(CATEGORIAS, 1):
        print(f"  {i}. {c}")
    while True:
        v = input("Escolha a categoria" + (" (Enter mantém)" if atual else "") + ": ").strip()
        if not v and atual:
            return atual
        if v.isdigit() and 1 <= int(v) <= len(CATEGORIAS):
            return CATEGORIAS[int(v) - 1]
        print(f"  ⚠ Opção inválida. Escolha de 1 a {len(CATEGORIAS)}.")


def escolher_opcao(msg, validas):
    while True:
        v = input(msg).strip()
        if v in validas:
            return v
        print(f"  ⚠ Opção inválida. Opções: {', '.join(validas)}.")


def salvar(lista):
    try:
        persistencia.salvar(lista, ARQUIVO_DADOS)
    except persistencia.ErroPersistencia as e:
        print(f"  ⚠ {e}")


# ---------- operações ----------
def cadastrar(lista):
    print("\n— Novo cadastro —")
    sugestao = lista.proximo_id_livre()
    while True:
        v = input(f"ID (Enter usa {sugestao}): ").strip()
        id_ = sugestao if not v else (int(v) if v.isdigit() and int(v) > 0 else None)
        if id_ is None:
            print("  ⚠ Digite um número inteiro positivo.")
        elif lista.existe_id(id_):
            print(f"  ⚠ O ID {id_} já existe. Escolha outro.")
        else:
            break
    reg = Registro(
        id_,
        ler_texto("Título: ", "titulo"),
        escolher_categoria(),
        ler_texto("Descrição: ", "descricao"),
        ler_texto("Requisitos: ", "requisitos"),
        ler_texto("Local de atendimento: ", "local"),
        ler_texto("Contato (opcional): ", "contato", obrigatorio=False),
    )
    try:
        lista.inserir_fim(reg)
    except IdDuplicadoError as e:
        print(f"  ⚠ {e}")
        return
    salvar(lista)
    print(f"  ✔ Registro {reg.id} cadastrado.")


def consultar(lista):
    if lista.esta_vazia():
        return print("  ℹ A lista está vazia.")
    reg = lista.buscar_por_id(ler_inteiro_positivo("ID a consultar: "))
    print("\n" + str(reg) if reg else "  ℹ Nenhum registro com esse ID.")


def atualizar(lista):
    if lista.esta_vazia():
        return print("  ℹ A lista está vazia.")
    reg = lista.buscar_por_id(ler_inteiro_positivo("ID a atualizar: "))
    if reg is None:
        return print("  ℹ Nenhum registro com esse ID.")
    print("\n" + str(reg) + "\n\n(Enter mantém o valor atual)")
    try:
        lista.atualizar(
            reg.id,
            titulo=ler_texto("Novo título: ", "titulo", atual=reg.titulo),
            categoria=escolher_categoria(reg.categoria),
            descricao=ler_texto("Nova descrição: ", "descricao", atual=reg.descricao),
            requisitos=ler_texto("Novos requisitos: ", "requisitos", atual=reg.requisitos),
            local=ler_texto("Novo local: ", "local", atual=reg.local),
            contato=ler_texto("Novo contato: ", "contato", obrigatorio=False, atual=reg.contato),
        )
    except ValueError as e:
        return print(f"  ⚠ {e} Nada foi alterado.")
    salvar(lista)
    print("  ✔ Registro atualizado.")


def excluir(lista):
    if lista.esta_vazia():
        return print("  ℹ A lista está vazia.")
    reg = lista.buscar_por_id(ler_inteiro_positivo("ID a excluir: "))
    if reg is None:
        return print("  ℹ Nenhum registro com esse ID.")
    print("\n" + str(reg))
    if escolher_opcao("Confirmar exclusão? (s/n): ", ("s", "n")) == "s":
        lista.remover(reg.id)
        salvar(lista)
        print("  ✔ Registro excluído.")
    else:
        print("  Exclusão cancelada.")


def pesquisar(lista):
    if lista.esta_vazia():
        return print("  ℹ A lista está vazia.")
    atributo = "titulo" if escolher_opcao("Pesquisar por 1) título  2) categoria: ", ("1", "2")) == "1" else "categoria"
    termo = ler_texto("Termo: ", "titulo")
    achados = busca_sequencial(lista, atributo, termo)
    if not achados:
        return print(f"  ℹ Nenhum registro encontrado para '{termo}' em {atributo}.")
    print(f"\n{len(achados)} resultado(s):")
    for r in achados:
        print("\n" + str(r))


def listar_ordenar(lista):
    if lista.esta_vazia():
        return print("  ℹ A lista está vazia.")
    crit = {"1": "id", "2": "titulo", "3": "categoria"}[
        escolher_opcao("Ordenar por 1) ID  2) título  3) categoria: ", ("1", "2", "3"))]
    algo = {"1": "merge", "2": "insertion"}[
        escolher_opcao("Algoritmo 1) Merge Sort  2) Insertion Sort: ", ("1", "2"))]
    rev = escolher_opcao("Ordem 1) crescente  2) decrescente: ", ("1", "2")) == "2"
    lista.ordenar(CHAVES[crit], algo, rev)
    salvar(lista)
    print(f"\n{len(lista)} registro(s), ordenados por {crit} ({algo} sort):")
    for r in lista:
        print(f"  [{r.id:>3}] {r.titulo}  ·  {r.categoria}")
    print("\nEstrutura: " + lista.diagrama())


def mostrar_analise(lista):
    print("\n" + analise.formatar_resumo(lista))


def carregar_lista():
    try:
        lista = persistencia.carregar(ARQUIVO_DADOS)
    except persistencia.ErroPersistencia as e:
        print(f"⚠ {e}")
        copia = ARQUIVO_DADOS + ".corrompido"
        try:                      # preserva o arquivo problemático antes de recriar os dados
            os.replace(ARQUIVO_DADOS, copia)
            print(f"  Uma cópia do arquivo foi guardada em: {copia}")
        except OSError:
            pass
        print("  Iniciando com os dados de exemplo.")
        lista = None
    if lista is None:
        lista = carregar_exemplos()
        salvar(lista)
    return lista


ACOES = {"1": cadastrar, "2": consultar, "3": atualizar, "4": excluir,
         "5": pesquisar, "6": listar_ordenar, "7": mostrar_analise}


def executar():
    lista = carregar_lista()
    while True:
        print(MENU)
        try:
            op = input("Opção: ").strip()
            if op == "8":
                print("Até logo! 🌈")
                return
            if op in ACOES:
                ACOES[op](lista)
            else:
                print("  ⚠ Opção inexistente. Escolha de 1 a 8.")
        except (KeyboardInterrupt, EOFError):
            print("\nEncerrando. Até logo! 🌈")
            return
