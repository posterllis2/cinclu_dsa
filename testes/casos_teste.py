"""Casos de teste do Cinclu (fonte única para unittest e para a tabela de evidências).

Cada caso registra: área, descrição, entrada, resultado ESPERADO e uma função que
devolve o resultado OBSERVADO (texto). O caso passa se observado == esperado.
O resultado esperado é escrito à mão ou calculado por um "oráculo" independente
(ex.: sorted() do Python, usado SÓ nos testes para conferir nossos algoritmos).
"""
import io
import os
import random
import sys
import tempfile
from contextlib import redirect_stdout
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import analise
import cli
import persistencia
from algoritmos import CHAVES, busca_sequencial
from dados_iniciais import carregar_exemplos
from lista_encadeada import IdDuplicadoError, ListaEncadeada
from modelo import CATEGORIAS, Registro

CASOS = []


class Caso:
    def __init__(self, area, descricao, entrada, esperado, fn, requer_gui):
        self.id = f"CT{len(CASOS) + 1:02d}"
        self.area, self.descricao, self.entrada = area, descricao, entrada
        self.esperado_def, self.fn, self.requer_gui = esperado, fn, requer_gui

    def esperado(self):
        return self.esperado_def() if callable(self.esperado_def) else self.esperado_def

    def executar(self):
        try:
            obs = self.fn()
        except Exception as e:  # erro não previsto no próprio teste
            obs = f"ERRO INESPERADO {type(e).__name__}: {e}"
        esp = self.esperado()
        return obs, esp, obs == esp


def caso(area, descricao, entrada, esperado, requer_gui=False):
    def deco(fn):
        CASOS.append(Caso(area, descricao, entrada, esperado, fn, requer_gui))
        return fn
    return deco


# ---------------- utilitários ----------------
def reg(id_, titulo=None, cat=None):
    return Registro(id_, titulo or f"Título {id_}", cat or CATEGORIAS[0], "desc", "req", "local")


def lista_de(*ids):
    l = ListaEncadeada()
    for i in ids:
        l.inserir_fim(reg(i))
    return l


def ids(l):
    return [r.id for r in l]


def erro(fn):
    try:
        fn()
        return "sem erro"
    except Exception as e:
        return f"{type(e).__name__}: {e}"


def embaralhada(semente=7):
    regs = list(carregar_exemplos())
    random.Random(semente).shuffle(regs)
    l = ListaEncadeada()
    for r in regs:
        l.inserir_fim(r)
    return l


def estado(l):
    c = l.cabeca.dado.id if l.cabeca else None
    t = l.cauda.dado.id if l.cauda else None
    return f"{ids(l)} | cabeça={c} | cauda={t}"


def msgs(saida):
    marcas = ("⚠", "ℹ", "✔", "Nenhum registro cadastrado", "Exclusão cancelada", "Encerrando")
    return " / ".join(l.strip() for l in saida.splitlines() if l.strip().startswith(marcas))


def rodar_cli(entradas, vazia=False):
    arq = os.path.join(tempfile.mkdtemp(), "servicos.json")
    it = iter(entradas)

    def entrada_falsa(prompt=""):
        try:
            return next(it)
        except StopIteration:
            raise EOFError

    buf = io.StringIO()
    with patch.object(cli, "ARQUIVO_DADOS", arq), patch("builtins.input", entrada_falsa), redirect_stdout(buf):
        if vazia:
            with patch.object(cli, "carregar_lista", lambda: ListaEncadeada()):
                cli.executar()
        else:
            cli.executar()
    return buf.getvalue(), arq


# ================= LISTA ENCADEADA =================
A = "Lista encadeada"


@caso(A, "Inserir 3 registros no fim de uma lista vazia", "inserir_fim(ID 1, 2, 3)", "3 | [1, 2, 3]")
def _():
    l = lista_de(1, 2, 3)
    return f"{len(l)} | {ids(l)}"


@caso(A, "Inserir no início", "lista [1, 2]; inserir_inicio(ID 9)", "[9, 1, 2] | cabeça=9 | cauda=2")
def _():
    l = lista_de(1, 2)
    l.inserir_inicio(reg(9))
    return estado(l)


@caso(A, "Inserir em lista vazia", "lista vazia; inserir_fim(ID 5)", "1 | cabeça é cauda: True")
def _():
    l = ListaEncadeada()
    l.inserir_fim(reg(5))
    return f"{len(l)} | cabeça é cauda: {l.cabeca is l.cauda}"


@caso(A, "Identificador duplicado", "lista [1, 2, 3]; inserir_fim(ID 2)",
      "IdDuplicadoError: Já existe um registro com o ID 2. | tamanho=3")
def _():
    l = lista_de(1, 2, 3)
    return f"{erro(lambda: l.inserir_fim(reg(2)))} | tamanho={len(l)}"


@caso(A, "Percurso em lista vazia", "lista vazia; percorrer", "[]")
def _():
    return str(ids(ListaEncadeada()))


@caso(A, "Remover a cabeça", "lista [1, 2, 3]; remover(1)", "[2, 3] | cabeça=2 | cauda=3")
def _():
    l = lista_de(1, 2, 3)
    l.remover(1)
    return estado(l)


@caso(A, "Remover do meio", "lista [1, 2, 3]; remover(2)", "[1, 3] | cabeça=1 | cauda=3")
def _():
    l = lista_de(1, 2, 3)
    l.remover(2)
    return estado(l)


@caso(A, "Remover a cauda e inserir depois (integridade)", "lista [1, 2, 3]; remover(3); inserir_fim(7)",
      "[1, 2, 7] | cabeça=1 | cauda=7")
def _():
    l = lista_de(1, 2, 3)
    l.remover(3)
    l.inserir_fim(reg(7))
    return estado(l)


@caso(A, "Remover o único elemento", "lista [4]; remover(4)", "[] | vazia=True | cauda=None")
def _():
    l = lista_de(4)
    l.remover(4)
    return f"{ids(l)} | vazia={l.esta_vazia()} | cauda={l.cauda}"


@caso(A, "Remover ID inexistente", "lista [1, 2, 3]; remover(99)", "None | tamanho=3")
def _():
    l = lista_de(1, 2, 3)
    return f"{l.remover(99)} | tamanho={len(l)}"


@caso(A, "Remover com lista vazia", "lista vazia; remover(1)", "None | tamanho=0")
def _():
    l = ListaEncadeada()
    return f"{l.remover(1)} | tamanho={len(l)}"


@caso(A, "Consultar ID existente", "lista [1, 2, 3]; buscar_por_id(2)", "Título 2")
def _():
    return lista_de(1, 2, 3).buscar_por_id(2).titulo


@caso(A, "Consultar ID inexistente", "lista [1, 2, 3]; buscar_por_id(50)", "None")
def _():
    return str(lista_de(1, 2, 3).buscar_por_id(50))


@caso(A, "Consultar em lista vazia", "lista vazia; buscar_por_id(1)", "None")
def _():
    return str(ListaEncadeada().buscar_por_id(1))


@caso(A, "Atualizar registro existente", "atualizar(1, titulo='Novo', categoria='Saúde Mental')",
      "Novo | Saúde Mental | id=1")
def _():
    l = lista_de(1, 2)
    r = l.atualizar(1, titulo="Novo", categoria="Saúde Mental")
    return f"{r.titulo} | {r.categoria} | id={r.id}"


@caso(A, "Atualização inválida preserva o registro", "atualizar(1, titulo='   ')",
      "ValueError: O campo 'titulo' é obrigatório. | título preservado: Título 1")
def _():
    l = lista_de(1)
    e = erro(lambda: l.atualizar(1, titulo="   "))
    return f"{e} | título preservado: {l.buscar_por_id(1).titulo}"


@caso(A, "Atualizar ID inexistente", "atualizar(77, titulo='X')", "None")
def _():
    return str(lista_de(1).atualizar(77, titulo="X"))


@caso(A, "Atualização não altera o ID", "atualizar(1, id=500, titulo='Y')", "id=1 | título=Y")
def _():
    r = lista_de(1).atualizar(1, id=500, titulo="Y")
    return f"id={r.id} | título={r.titulo}"


# ================= MODELO / VALIDAÇÃO =================
M = "Validação do modelo"


def _tenta(**kw):
    base = dict(id=1, titulo="T", categoria=CATEGORIAS[0], descricao="d", requisitos="r", local="l", contato="")
    base.update(kw)
    return erro(lambda: Registro(**base))


@caso(M, "ID negativo", "Registro(id=-3)", "ValueError: O identificador deve ser um número inteiro positivo.")
def _():
    return _tenta(id=-3)


@caso(M, "ID zero", "Registro(id=0)", "ValueError: O identificador deve ser um número inteiro positivo.")
def _():
    return _tenta(id=0)


@caso(M, "ID não numérico", "Registro(id='abc')", "ValueError: O identificador deve ser um número inteiro positivo.")
def _():
    return _tenta(id="abc")


@caso(M, "Categoria inexistente", "Registro(categoria='Esportes')", "ValueError: Categoria inexistente.")
def _():
    return _tenta(categoria="Esportes")


@caso(M, "Título acima do limite", "título com 81 caracteres", "ValueError: O campo 'titulo' excede 80 caracteres.")
def _():
    return _tenta(titulo="a" * 81)


@caso(M, "Descrição só com espaços", "descricao='    '", "ValueError: O campo 'descricao' é obrigatório.")
def _():
    return _tenta(descricao="    ")


@caso(M, "Registro válido com contato opcional vazio", "contato=''", "sem erro")
def _():
    return _tenta()


# ================= BUSCA =================
B = "Busca"


@caso(B, "Categoria sem acento e em maiúsculas", "pesquisar categoria 'SAUDE' (dados de exemplo)",
      "5 resultado(s): [6, 7, 8, 9, 10]")
def _():
    r = busca_sequencial(carregar_exemplos(), "categoria", "SAUDE")
    return f"{len(r)} resultado(s): {[x.id for x in r]}"


@caso(B, "Título parcial", "pesquisar título 'prep'", "1 resultado(s): [6]")
def _():
    r = busca_sequencial(carregar_exemplos(), "titulo", "prep")
    return f"{len(r)} resultado(s): {[x.id for x in r]}"


@caso(B, "Nenhum registro encontrado", "pesquisar título 'zzz'", "0 resultado(s): []")
def _():
    r = busca_sequencial(carregar_exemplos(), "titulo", "zzz")
    return f"{len(r)} resultado(s): {[x.id for x in r]}"


@caso(B, "Termo vazio", "pesquisar título '   '", "0 resultado(s)")
def _():
    return f"{len(busca_sequencial(carregar_exemplos(), 'titulo', '   '))} resultado(s)"


@caso(B, "Busca em lista vazia", "pesquisar título 'a' em lista vazia", "0 resultado(s)")
def _():
    return f"{len(busca_sequencial(ListaEncadeada(), 'titulo', 'a'))} resultado(s)"


# ================= ORDENAÇÃO =================
O = "Ordenação"


def _caso_ordem(nome, crit, algo, rev):
    def esperado():
        return str([r.id for r in sorted(embaralhada(), key=CHAVES[crit], reverse=rev)])

    def fn():
        l = embaralhada()
        l.ordenar(CHAVES[crit], algo, rev)
        return str(ids(l))

    sentido = "decrescente" if rev else "crescente"
    caso(O, f"{nome} por {crit} ({sentido})", f"ordenar(chave={crit}, algoritmo={algo}, reverso={rev}) em lista embaralhada",
         esperado)(fn)


_caso_ordem("Merge Sort", "titulo", "merge", False)
_caso_ordem("Insertion Sort", "titulo", "insertion", False)
_caso_ordem("Merge Sort", "categoria", "merge", True)
_caso_ordem("Insertion Sort", "id", "insertion", True)
_caso_ordem("Merge Sort", "id", "merge", False)


@caso(O, "Ordenar lista vazia", "lista vazia; ordenar (merge e insertion)", "[] | []")
def _():
    a, b = ListaEncadeada(), ListaEncadeada()
    a.ordenar(CHAVES["id"], "merge")
    b.ordenar(CHAVES["id"], "insertion")
    return f"{ids(a)} | {ids(b)}"


@caso(O, "Ordenar lista com um elemento", "lista [8]; ordenar", "[8] | cabeça=8 | cauda=8")
def _():
    l = lista_de(8)
    l.ordenar(CHAVES["id"], "merge")
    return estado(l)


@caso(O, "Lista já ordenada permanece igual", "lista [1..5]; ordenar por id", "[1, 2, 3, 4, 5]")
def _():
    l = lista_de(1, 2, 3, 4, 5)
    l.ordenar(CHAVES["id"], "insertion")
    return str(ids(l))


def _esperado_estavel():
    ordem = [r.id for r in sorted(embaralhada(), key=lambda r: r.categoria)]
    return f"{ordem} | {ordem}"


@caso(O, "Estabilidade: chaves iguais mantêm a ordem",
      "lista embaralhada; chave = categoria (bruta); Merge e Insertion", _esperado_estavel)
def _():
    a, b = embaralhada(), embaralhada()
    a.ordenar(lambda r: r.categoria, "merge")
    b.ordenar(lambda r: r.categoria, "insertion")
    return f"{ids(a)} | {ids(b)}"


@caso(O, "Integridade após ordenar (cauda e inserção)", "lista [3, 1, 2]; ordenar por id; inserir_fim(ID 10)",
      "[1, 2, 3, 10] | cabeça=1 | cauda=10")
def _():
    l = lista_de(3, 1, 2)
    l.ordenar(CHAVES["id"], "merge")
    l.inserir_fim(reg(10))
    return estado(l)


def _esperado_estavel_desc():
    ordem = [r.id for r in sorted(embaralhada(), key=lambda r: r.categoria, reverse=True)]
    return f"{ordem} | {ordem}"


@caso(O, "Estabilidade na ordem decrescente",
      "lista embaralhada; chave = categoria (bruta); reverso=True; Merge e Insertion", _esperado_estavel_desc)
def _():
    a, b = embaralhada(), embaralhada()
    a.ordenar(lambda r: r.categoria, "merge", True)
    b.ordenar(lambda r: r.categoria, "insertion", True)
    return f"{ids(a)} | {ids(b)}"


@caso(O, "Insertion Sort em lista em ordem inversa", "lista [5, 4, 3, 2, 1]; ordenar por id crescente",
      "[1, 2, 3, 4, 5] | cabeça=1 | cauda=5")
def _():
    l = lista_de(5, 4, 3, 2, 1)
    l.ordenar(CHAVES["id"], "insertion")
    return estado(l)


@caso(O, "Algoritmo desconhecido", "ordenar(algoritmo='bubble')", "ValueError: Algoritmo de ordenação desconhecido.")
def _():
    return erro(lambda: lista_de(1, 2).ordenar(CHAVES["id"], "bubble"))


@caso(A, "Representação da cadeia de nós", "lista [3, 1, 2]; diagrama()",
      "cabeça → [3] → [1] → [2] → None   |   cauda = [2]   |   tamanho = 3")
def _():
    return lista_de(3, 1, 2).diagrama()


@caso(A, "Representação de lista vazia", "lista vazia; diagrama()", "cabeça → None   (lista vazia)")
def _():
    return ListaEncadeada().diagrama()


# ================= ANÁLISE =================
N = "Análise"


@caso(N, "Contagem por categoria (dados de exemplo)", "resumo(lista de exemplo)",
      "total=14 | [3, 2, 3, 2, 2, 2] | predominante=Saúde")
def _():
    r = analise.resumo(carregar_exemplos())
    return f"total={r['total']} | {list(r['por_categoria'].values())} | predominante={r['categoria_predominante']}"


@caso(N, "Análise de lista vazia", "formatar_resumo(lista vazia)", "Nenhum registro cadastrado ainda.")
def _():
    return analise.formatar_resumo(ListaEncadeada())


@caso(N, "Análise reflete exclusão", "excluir ID 6 (Saúde) e reanalisar", "total=13 | Saúde=2")
def _():
    l = carregar_exemplos()
    l.remover(6)
    r = analise.resumo(l)
    return f"total={r['total']} | Saúde={r['por_categoria']['Saúde']}"


# ================= PERSISTÊNCIA =================
P = "Persistência"


@caso(P, "Salvar e carregar (ida e volta)", "salvar 14 registros ordenados por título e carregar",
      "14 registros | ordem preservada: True")
def _():
    l = carregar_exemplos()
    l.ordenar(CHAVES["titulo"], "merge")
    arq = os.path.join(tempfile.mkdtemp(), "d.json")
    persistencia.salvar(l, arq)
    n = persistencia.carregar(arq)
    return f"{len(n)} registros | ordem preservada: {ids(n) == ids(l)}"


@caso(P, "Arquivo inexistente", "carregar('nao_existe.json')", "None")
def _():
    return str(persistencia.carregar(os.path.join(tempfile.mkdtemp(), "nao_existe.json")))


def _arquivo_com(texto):
    arq = os.path.join(tempfile.mkdtemp(), "d.json")
    with open(arq, "w", encoding="utf-8") as f:
        f.write(texto)
    return arq


def _erro_carga(texto):
    e = erro(lambda: persistencia.carregar(_arquivo_com(texto)))
    return e.split(" (")[0]


@caso(P, "JSON corrompido", "arquivo com '{ isto nao e json'", "ErroPersistencia: Arquivo de dados inválido")
def _():
    return _erro_carga("{ isto nao e json")


@caso(P, "IDs duplicados no arquivo", "arquivo com dois registros de ID 1", "ErroPersistencia: Arquivo de dados inválido")
def _():
    d = '{"id":1,"titulo":"a","categoria":"Saúde","descricao":"d","requisitos":"r","local":"l"}'
    return _erro_carga(f"[{d},{d}]")


@caso(P, "Registro inválido no arquivo", "arquivo com categoria inexistente", "ErroPersistencia: Arquivo de dados inválido")
def _():
    return _erro_carga('[{"id":1,"titulo":"a","categoria":"X","descricao":"d","requisitos":"r","local":"l"}]')


# ================= MENU EM TERMINAL =================
C = "Menu (terminal)"


@caso(C, "Opção inexistente e não numérica", "digitar '9', 'abc' e depois '8'",
      "⚠ Opção inexistente. Escolha de 1 a 8. / ⚠ Opção inexistente. Escolha de 1 a 8.")
def _():
    return msgs(rodar_cli(["9", "abc", "8"])[0])


@caso(C, "Cadastro: ID duplicado, ID inválido e sucesso",
      "opção 1; ID '1' (duplicado); ID 'abc'; ID '100'; campos válidos",
      "⚠ O ID 1 já existe. Escolha outro. / ⚠ Digite um número inteiro positivo. / ✔ Registro 100 cadastrado.")
def _():
    return msgs(rodar_cli(["1", "1", "abc", "100", "Título CLI", "1", "Desc", "Req", "Local", "", "8"])[0])


@caso(C, "Cadastro: campo vazio e categoria inválida",
      "opção 1; ID (Enter); título vazio; categoria '9'; depois valores válidos",
      "⚠ Campo obrigatório. / ⚠ Opção inválida. Escolha de 1 a 6. / ✔ Registro 15 cadastrado.")
def _():
    return msgs(rodar_cli(["1", "", "", "T", "9", "2", "D", "R", "L", "", "8"])[0])


@caso(C, "Persistência após cadastrar", "cadastrar ID 15 e reler o arquivo JSON", "15 registros | ID 15 presente: True")
def _():
    _, arq = rodar_cli(["1", "", "Novo", "1", "D", "R", "L", "", "8"])
    l = persistencia.carregar(arq)
    return f"{len(l)} registros | ID 15 presente: {l.existe_id(15)}"


@caso(C, "Consulta: ID inexistente", "opção 2; ID 999", "ℹ Nenhum registro com esse ID.")
def _():
    return msgs(rodar_cli(["2", "999", "8"])[0])


@caso(C, "Consulta: IDs inválidos (-5, 0, texto) e depois válido", "opção 2; '-5', '0', 'x', '3'",
      "⚠ Digite um número inteiro positivo. / ⚠ Digite um número inteiro positivo. / ⚠ Digite um número inteiro positivo.")
def _():
    return msgs(rodar_cli(["2", "-5", "0", "x", "3", "8"])[0])


@caso(C, "Atualização mantendo valores (Enter)", "opção 3; ID 1; Enter em todos os campos", "✔ Registro atualizado.")
def _():
    return msgs(rodar_cli(["3", "1", "", "", "", "", "", "", "8"])[0])


@caso(C, "Atualização: ID inexistente", "opção 3; ID 888", "ℹ Nenhum registro com esse ID.")
def _():
    return msgs(rodar_cli(["3", "888", "8"])[0])


@caso(C, "Exclusão: cancelar e depois confirmar", "opção 4; ID 1; 'n'; opção 4; ID 1; 's'",
      "Exclusão cancelada. / ✔ Registro excluído.")
def _():
    return msgs(rodar_cli(["4", "1", "n", "4", "1", "s", "8"])[0])


@caso(C, "Exclusão: ID inexistente", "opção 4; ID 777", "ℹ Nenhum registro com esse ID.")
def _():
    return msgs(rodar_cli(["4", "777", "8"])[0])


@caso(C, "Pesquisa sem resultado", "opção 5; título; 'zzz'", "ℹ Nenhum registro encontrado para 'zzz' em titulo.")
def _():
    return msgs(rodar_cli(["5", "1", "zzz", "8"])[0])


@caso(C, "Operações com a lista vazia", "lista vazia; opções 2, 3, 4, 5, 6 e 7",
      "ℹ A lista está vazia. / ℹ A lista está vazia. / ℹ A lista está vazia. / ℹ A lista está vazia. / "
      "ℹ A lista está vazia. / Nenhum registro cadastrado ainda.")
def _():
    return msgs(rodar_cli(["2", "3", "4", "5", "6", "7", "8"], vazia=True)[0])


@caso(C, "Arquivo de dados corrompido na inicialização", "servicos.json com texto inválido; abrir e encerrar",
      "aviso exibido: True | cópia .corrompido criada: True | 14 registros recriados")
def _():
    arq = os.path.join(tempfile.mkdtemp(), "servicos.json")
    with open(arq, "w", encoding="utf-8") as f:
        f.write("{ isto nao e json")
    it = iter(["8"])
    buf = io.StringIO()
    with patch.object(cli, "ARQUIVO_DADOS", arq), patch("builtins.input", lambda p="": next(it)), redirect_stdout(buf):
        cli.executar()
    n = len(persistencia.carregar(arq))
    return (f"aviso exibido: {'Arquivo de dados inválido' in buf.getvalue()} | "
            f"cópia .corrompido criada: {os.path.exists(arq + '.corrompido')} | {n} registros recriados")


@caso(C, "Interrupção (EOF / Ctrl+D)", "entrada encerrada sem digitar '8'", "Encerrando. Até logo! 🌈")
def _():
    return msgs(rodar_cli([])[0])


# ================= INTERFACE GRÁFICA =================
G = "Interface gráfica"


def gui_disponivel():
    try:
        import tkinter as tk
        r = tk.Tk()
        r.destroy()
        return True
    except Exception:
        return False


def com_gui(acao, vazia=False):
    import gui
    arq = os.path.join(tempfile.mkdtemp(), "servicos.json")
    avisos = []
    with patch.object(cli, "ARQUIVO_DADOS", arq), patch.object(gui, "ARQUIVO_DADOS", arq), \
            patch.object(gui.messagebox, "showwarning", lambda *a, **k: avisos.append(a)), \
            patch.object(gui.messagebox, "askyesno", lambda *a, **k: True), redirect_stdout(io.StringIO()):
        app = gui.CincluApp()
        try:
            if vazia:
                app.lista = ListaEncadeada()
                app.atualizar_tabela()
            app.update()
            return acao(app)
        finally:
            app.destroy()


def _preencher(app, id_, titulo="Serviço GUI", cat="Saúde"):
    app.novo()
    app.var_id.set(id_)
    app.var_titulo.set(titulo)
    app.var_cat.set(cat)
    app.txt_desc.insert("1.0", "descrição")
    app.txt_req.insert("1.0", "requisitos")
    app.var_local.set("local")


@caso(G, "Cadastro válido", "ID sugerido (15) + campos válidos; Cadastrar",
      "✔ Registro 15 cadastrado. | 15 linhas", requer_gui=True)
def _():
    def a(app):
        _preencher(app, app.lista.proximo_id_livre())
        app.salvar()
        return f"{app.status.get()} | {len(app.tabela.get_children())} linhas"
    return com_gui(a)


@caso(G, "Cadastro com ID duplicado", "ID 3 já existente; Cadastrar",
      "⚠ Já existe um registro com o ID 3. | 14 linhas", requer_gui=True)
def _():
    def a(app):
        _preencher(app, "3")
        app.salvar()
        return f"{app.status.get()} | {len(app.tabela.get_children())} linhas"
    return com_gui(a)


@caso(G, "Cadastro com ID não numérico", "ID 'abc'; Cadastrar", "⚠ O ID deve ser um número inteiro positivo.", requer_gui=True)
def _():
    def a(app):
        _preencher(app, "abc")
        app.salvar()
        return app.status.get()
    return com_gui(a)


@caso(G, "Cadastro com título vazio", "título vazio; Cadastrar",
      "⚠ O campo 'titulo' é obrigatório. Nada foi alterado.", requer_gui=True)
def _():
    def a(app):
        _preencher(app, "50", titulo="")
        app.salvar()
        return app.status.get()
    return com_gui(a)


@caso(G, "Consulta por ID existente", "Consultar ID 6", "Registro 6 encontrado (busca sequencial por ID). | 1 linha(s)", requer_gui=True)
def _():
    def a(app):
        app.var_busca_id.set("6")
        app.consultar_id()
        return f"{app.status.get()} | {len(app.tabela.get_children())} linha(s)"
    return com_gui(a)


@caso(G, "Consulta por ID inexistente", "Consultar ID 999", "ℹ Nenhum registro com o ID 999. | 0 linha(s)", requer_gui=True)
def _():
    def a(app):
        app.var_busca_id.set("999")
        app.consultar_id()
        return f"{app.status.get()} | {len(app.tabela.get_children())} linha(s)"
    return com_gui(a)


@caso(G, "Consulta por ID inválido", "Consultar ID 'abc'", "⚠ Digite um ID numérico positivo para consultar.", requer_gui=True)
def _():
    def a(app):
        app.var_busca_id.set("abc")
        app.consultar_id()
        return app.status.get()
    return com_gui(a)


@caso(G, "Pesquisa por categoria", "categoria; 'saude mental'", "2 resultado(s) para 'saude mental' em categoria. | 2 linha(s)", requer_gui=True)
def _():
    def a(app):
        app.var_attr.set("categoria")
        app.var_termo.set("saude mental")
        app.pesquisar()
        return f"{app.status.get()} | {len(app.tabela.get_children())} linha(s)"
    return com_gui(a)


@caso(G, "Pesquisa sem resultado", "título; 'zzz'", "ℹ Nenhum registro encontrado para 'zzz' em titulo. | 0 linha(s)", requer_gui=True)
def _():
    def a(app):
        app.var_termo.set("zzz")
        app.pesquisar()
        return f"{app.status.get()} | {len(app.tabela.get_children())} linha(s)"
    return com_gui(a)


@caso(G, "Atualização de registro selecionado", "selecionar ID 1; alterar título; Atualizar",
      "✔ Registro 1 atualizado. | Disque 100 (atualizado)", requer_gui=True)
def _():
    def a(app):
        app.tabela.selection_set("1")
        app.ao_selecionar(None)
        app.var_titulo.set("Disque 100 (atualizado)")
        app.salvar()
        return f"{app.status.get()} | {app.lista.buscar_por_id(1).titulo}"
    return com_gui(a)


@caso(G, "Exclusão de registro selecionado", "selecionar ID 5; Excluir (confirmar)",
      "✔ Registro 5 excluído. Restam 13. | 13 linhas", requer_gui=True)
def _():
    def a(app):
        app.tabela.selection_set("5")
        app.ao_selecionar(None)
        app.excluir()
        return f"{app.status.get()} | {len(app.tabela.get_children())} linhas"
    return com_gui(a)


@caso(G, "Exclusão sem seleção", "Excluir sem selecionar linha", "⚠ Selecione um registro na tabela para excluir.", requer_gui=True)
def _():
    return com_gui(lambda app: (app.excluir(), app.status.get())[1])


@caso(G, "Ordenação decrescente por ID (Insertion Sort)", "id; Insertion Sort; decrescente",
      "primeira linha: 14 | última linha: 1", requer_gui=True)
def _():
    def a(app):
        app.var_crit.set("id")
        app.var_algo.set("Insertion Sort")
        app.var_ordem.set("Decrescente")
        app.ordenar()
        f = app.tabela.get_children()
        return f"primeira linha: {f[0]} | última linha: {f[-1]}"
    return com_gui(a)


@caso(G, "Análise por categoria", "botão Análise", "Análise: categoria predominante = Saúde.", requer_gui=True)
def _():
    def a(app):
        app.mostrar_analise()
        return app.status.get()
    return com_gui(a)


@caso(G, "Operações com lista vazia", "lista vazia; pesquisar, ordenar e excluir",
      "ℹ A lista está vazia. / ℹ A lista está vazia: nada a ordenar. / ⚠ A lista está vazia: não há o que excluir.", requer_gui=True)
def _():
    def a(app):
        app.var_termo.set("x")
        app.pesquisar()
        s1 = app.status.get()
        app.ordenar()
        s2 = app.status.get()
        app.excluir()
        return f"{s1} / {s2} / {app.status.get()}"
    return com_gui(a, vazia=True)
