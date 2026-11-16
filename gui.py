"""Interface gráfica do Cinclu (Tkinter) – funcionalidade opcional."""

import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk, messagebox

import analise
import persistencia
from algoritmos import CHAVES, busca_sequencial
from cli import ARQUIVO_DADOS, carregar_lista
from lista_encadeada import IdDuplicadoError
from modelo import CATEGORIAS, Registro

# ---- identidade visual ----
AMEIXA, VIOLETA, MENTA = "#281250", "#946BF5", "#70D3A5"
ROSA, AMARELO, AZUL, LILAS = "#EC6A77", "#F2B245", "#668CF7", "#F1EEF9"
BRANCO, TEXTO_SUAVE, BORDA = "#FFFFFF", "#5B5278", "#DDD5F0"
CORES_CATEGORIAS = [VIOLETA, ROSA, MENTA, AMARELO, AZUL, AMEIXA]


def escolher_fonte(preferidas, reserva):
    instaladas = set(tkfont.families())
    for nome in preferidas:
        if nome in instaladas:
            return nome
    return reserva


class Logo(tk.Canvas):
    def __init__(self, master, tamanho=48, fundo=AMEIXA):
        super().__init__(master, width=tamanho, height=tamanho, bg=fundo, highlightthickness=0)
        m, esp = tamanho * 0.12, max(5, tamanho // 8)
        caixa = (m, m, tamanho - m, tamanho - m)
        inicio, passo = 40, 56                      # abertura à direita (≈ 80°)
        for i, cor in enumerate([VIOLETA, ROSA, AMARELO, MENTA, AZUL]):
            self.create_arc(*caixa, start=inicio + i * passo, extent=passo + 1,
                            style="arc", outline=cor, width=esp)
        c, r = tamanho / 2, tamanho * 0.07
        self.create_oval(tamanho * 0.74 - r, c - r, tamanho * 0.74 + r, c + r, fill=BRANCO, outline=BRANCO)


class CincluApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("cinclu · Cidade Inclusiva")
        self.geometry("1120x700")
        self.minsize(980, 620)
        self.configure(bg=LILAS)

        self.f_titulo = escolher_fonte(["Bricolage Grotesque"], "Helvetica")
        self.f_texto = escolher_fonte(["Instrument Sans"], "Helvetica")

        self.lista = carregar_lista()
        self.id_em_edicao = None       # None = modo "novo cadastro"

        self._estilos()
        self._cabecalho()
        self._barra_ferramentas()
        self._corpo()
        self.status = tk.StringVar()
        tk.Label(self, textvariable=self.status, anchor="w", bg=AMEIXA, fg=BRANCO,
                 font=(self.f_texto, 10), padx=16, pady=6).pack(side="bottom", fill="x")
        self.atualizar_tabela()
        self.novo()
        self.msg(f"{len(self.lista)} registro(s) carregado(s).")

    # ---------- construção da interface ----------
    def _estilos(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", background=LILAS, foreground=AMEIXA, font=(self.f_texto, 10))
        s.configure("Card.TFrame", background=BRANCO)
        s.configure("Card.TLabel", background=BRANCO, foreground=TEXTO_SUAVE)
        s.configure("TButton", background=BRANCO, foreground=AMEIXA, bordercolor=BORDA, padding=(12, 6))
        s.map("TButton", background=[("active", LILAS)])
        s.configure("Primary.TButton", background=VIOLETA, foreground=BRANCO, bordercolor=VIOLETA)
        s.map("Primary.TButton", background=[("active", AMEIXA)])
        s.configure("Danger.TButton", background=ROSA, foreground=BRANCO, bordercolor=ROSA)
        s.map("Danger.TButton", background=[("active", "#D4505E")])
        s.configure("Treeview", background=BRANCO, fieldbackground=BRANCO, rowheight=28, bordercolor=BORDA)
        s.configure("Treeview.Heading", background=AMEIXA, foreground=BRANCO,
                    font=(self.f_titulo, 10, "bold"), padding=6)
        s.map("Treeview", background=[("selected", VIOLETA)], foreground=[("selected", BRANCO)])
        s.configure("TEntry", fieldbackground=BRANCO, bordercolor=BORDA, padding=4)
        s.configure("TCombobox", fieldbackground=BRANCO, bordercolor=BORDA, padding=4)
        s.map("TCombobox", fieldbackground=[("readonly", BRANCO)], foreground=[("readonly", AMEIXA)])
        self.option_add("*TCombobox*Listbox.font", (self.f_texto, 10))

    def _cabecalho(self):
        topo = tk.Frame(self, bg=AMEIXA)
        topo.pack(fill="x")
        Logo(topo).pack(side="left", padx=(20, 10), pady=12)
        tk.Label(topo, text="cinclu", bg=AMEIXA, fg=BRANCO,
                 font=(self.f_titulo, 28, "bold")).pack(side="left")
        tk.Label(topo, text="Cidade Inclusiva · apoio, direitos e acolhimento para pessoas LGBTQIA+",
                 bg=AMEIXA, fg="#CFC4EA", font=(self.f_texto, 11)).pack(side="left", padx=20)

    def _barra_ferramentas(self):
        barra = ttk.Frame(self, padding=(16, 12, 16, 4))
        barra.pack(fill="x")

        # busca por ID
        ttk.Label(barra, text="ID:").grid(row=0, column=0, sticky="w")
        self.var_busca_id = tk.StringVar()
        ttk.Entry(barra, textvariable=self.var_busca_id, width=6).grid(row=0, column=1, padx=(4, 4))
        ttk.Button(barra, text="Consultar ID", command=self.consultar_id).grid(row=0, column=2, padx=(0, 18))

        # pesquisa por atributo
        ttk.Label(barra, text="Pesquisar em:").grid(row=0, column=3)
        self.var_attr = tk.StringVar(value="titulo")
        ttk.Combobox(barra, textvariable=self.var_attr, values=("titulo", "categoria"),
                     state="readonly", width=10).grid(row=0, column=4, padx=4)
        self.var_termo = tk.StringVar()
        e = ttk.Entry(barra, textvariable=self.var_termo, width=22)
        e.grid(row=0, column=5, padx=4)
        e.bind("<Return>", lambda _: self.pesquisar())
        ttk.Button(barra, text="Pesquisar", command=self.pesquisar).grid(row=0, column=6, padx=2)
        ttk.Button(barra, text="Mostrar todos", command=self.mostrar_todos).grid(row=0, column=7, padx=(2, 0))

        # ordenação
        ttk.Label(barra, text="Ordenar por:").grid(row=1, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.var_crit = tk.StringVar(value="titulo")
        self.var_algo = tk.StringVar(value="Merge Sort")
        self.var_ordem = tk.StringVar(value="Crescente")
        linha = ttk.Frame(barra)
        linha.grid(row=1, column=2, columnspan=6, sticky="w", pady=(10, 0))
        for var, vals, larg in ((self.var_crit, ("id", "titulo", "categoria"), 10),
                                (self.var_algo, ("Merge Sort", "Insertion Sort"), 14),
                                (self.var_ordem, ("Crescente", "Decrescente"), 12)):
            ttk.Combobox(linha, textvariable=var, values=vals, state="readonly",
                         width=larg).pack(side="left", padx=(0, 6))
        ttk.Button(linha, text="Ordenar", command=self.ordenar).pack(side="left", padx=(0, 6))
        ttk.Button(linha, text="Ver estrutura", command=self.mostrar_estrutura).pack(side="left", padx=(12, 6))
        ttk.Button(linha, text="Análise", style="Primary.TButton",
                   command=self.mostrar_analise).pack(side="left", padx=(6, 0))

    def _corpo(self):
        corpo = ttk.Frame(self, padding=(16, 8, 16, 12))
        corpo.pack(fill="both", expand=True)
        corpo.columnconfigure(0, weight=3)
        corpo.columnconfigure(1, weight=2)
        corpo.rowconfigure(0, weight=1)

        # tabela
        esq = ttk.Frame(corpo)
        esq.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        esq.rowconfigure(0, weight=1)
        esq.columnconfigure(0, weight=1)
        self.tabela = ttk.Treeview(esq, columns=("id", "titulo", "categoria"), show="headings", selectmode="browse")
        for col, txt, larg in (("id", "ID", 50), ("titulo", "Título", 255), ("categoria", "Categoria", 245)):
            self.tabela.heading(col, text=txt)
            self.tabela.column(col, width=larg, anchor="center" if col == "id" else "w")
        self.tabela.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(esq, orient="vertical", command=self.tabela.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.tabela.configure(yscrollcommand=sb.set)
        self.tabela.bind("<<TreeviewSelect>>", self.ao_selecionar)

        # formulário
        card = ttk.Frame(corpo, style="Card.TFrame", padding=16)
        card.grid(row=0, column=1, sticky="nsew")
        card.columnconfigure(1, weight=1)
        self.lbl_modo = tk.Label(card, text="", bg=BRANCO, fg=AMEIXA, font=(self.f_titulo, 14, "bold"), anchor="w")
        self.lbl_modo.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        self.var_id, self.var_titulo = tk.StringVar(), tk.StringVar()
        self.var_cat, self.var_local, self.var_contato = tk.StringVar(), tk.StringVar(), tk.StringVar()
        ttk.Label(card, text="ID", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=3)
        self.ent_id = ttk.Entry(card, textvariable=self.var_id, width=8)
        self.ent_id.grid(row=1, column=1, sticky="w", pady=3)
        ttk.Label(card, text="Título", style="Card.TLabel").grid(row=2, column=0, sticky="w", pady=3)
        ttk.Entry(card, textvariable=self.var_titulo).grid(row=2, column=1, sticky="ew", pady=3)
        ttk.Label(card, text="Categoria", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=3)
        ttk.Combobox(card, textvariable=self.var_cat, values=CATEGORIAS, state="readonly").grid(row=3, column=1, sticky="ew", pady=3)
        ttk.Label(card, text="Descrição", style="Card.TLabel").grid(row=4, column=0, sticky="nw", pady=3)
        self.txt_desc = self._caixa_texto(card, 4)
        ttk.Label(card, text="Requisitos", style="Card.TLabel").grid(row=5, column=0, sticky="nw", pady=3)
        self.txt_req = self._caixa_texto(card, 5)
        ttk.Label(card, text="Local", style="Card.TLabel").grid(row=6, column=0, sticky="w", pady=3)
        ttk.Entry(card, textvariable=self.var_local).grid(row=6, column=1, sticky="ew", pady=3)
        ttk.Label(card, text="Contato", style="Card.TLabel").grid(row=7, column=0, sticky="w", pady=3)
        ttk.Entry(card, textvariable=self.var_contato).grid(row=7, column=1, sticky="ew", pady=3)

        botoes = ttk.Frame(card, style="Card.TFrame")
        botoes.grid(row=8, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(botoes, text="Novo", command=self.novo).pack(side="left", padx=4)
        ttk.Button(botoes, text="Excluir", style="Danger.TButton", command=self.excluir).pack(side="left", padx=4)
        self.btn_salvar = ttk.Button(botoes, text="Salvar", style="Primary.TButton", command=self.salvar)
        self.btn_salvar.pack(side="left", padx=4)

    def _caixa_texto(self, pai, linha):
        t = tk.Text(pai, height=4, width=30, wrap="word", font=(self.f_texto, 10), relief="solid", bd=1,
                    highlightthickness=0, bg=BRANCO, fg=AMEIXA)
        t.grid(row=linha, column=1, sticky="ew", pady=3)
        return t

    # ---------- utilidades ----------
    def msg(self, texto):
        self.status.set(texto)

    def aviso(self, texto):
        self.msg("⚠ " + texto)
        messagebox.showwarning("Atenção", texto, parent=self)

    def gravar(self):
        try:
            persistencia.salvar(self.lista, ARQUIVO_DADOS)
        except persistencia.ErroPersistencia as e:
            self.aviso(str(e))

    def atualizar_tabela(self, registros=None):
        """Mostra a lista inteira (percorrendo os nós) ou uma lista de resultados."""
        self.tabela.delete(*self.tabela.get_children())
        for r in (self.lista if registros is None else registros):
            self.tabela.insert("", "end", iid=str(r.id), values=(r.id, r.titulo, r.categoria))

    # ---------- formulário ----------
    def novo(self):
        self.id_em_edicao = None
        self.tabela.selection_remove(self.tabela.selection())
        self.var_id.set(str(self.lista.proximo_id_livre()))
        self.ent_id.state(["!disabled"])
        self.var_titulo.set("")
        self.var_cat.set("")
        self.var_local.set("")
        self.var_contato.set("")
        self.txt_desc.delete("1.0", "end")
        self.txt_req.delete("1.0", "end")
        self.lbl_modo.config(text="Novo cadastro")
        self.btn_salvar.config(text="Cadastrar")

    def ao_selecionar(self, _):
        sel = self.tabela.selection()
        if not sel:
            return
        reg = self.lista.buscar_por_id(int(sel[0]))
        if reg is None:
            return
        self.id_em_edicao = reg.id
        self.var_id.set(str(reg.id))
        self.ent_id.state(["disabled"])
        self.var_titulo.set(reg.titulo)
        self.var_cat.set(reg.categoria)
        self.var_local.set(reg.local)
        self.var_contato.set(reg.contato)
        self.txt_desc.delete("1.0", "end"); self.txt_desc.insert("1.0", reg.descricao)
        self.txt_req.delete("1.0", "end"); self.txt_req.insert("1.0", reg.requisitos)
        self.lbl_modo.config(text=f"Editando registro {reg.id}")
        self.btn_salvar.config(text="Atualizar")

    def _campos_formulario(self):
        return dict(titulo=self.var_titulo.get().strip(), categoria=self.var_cat.get(),
                    descricao=self.txt_desc.get("1.0", "end-1c").strip(),
                    requisitos=self.txt_req.get("1.0", "end-1c").strip(),
                    local=self.var_local.get().strip(), contato=self.var_contato.get().strip())

    # ---------- operações ----------
    def salvar(self):
        campos = self._campos_formulario()
        try:
            if self.id_em_edicao is None:                         # CADASTRAR
                txt = self.var_id.get().strip()
                if not txt.isdigit() or int(txt) <= 0:
                    return self.aviso("O ID deve ser um número inteiro positivo.")
                reg = Registro(int(txt), **campos)
                self.lista.inserir_fim(reg)
                self.msg(f"✔ Registro {reg.id} cadastrado.")
            else:                                                 # ATUALIZAR
                self.lista.atualizar(self.id_em_edicao, **campos)
                self.msg(f"✔ Registro {self.id_em_edicao} atualizado.")
        except IdDuplicadoError as e:
            return self.aviso(str(e))
        except ValueError as e:
            return self.aviso(f"{e} Nada foi alterado.")
        self.gravar()
        self.atualizar_tabela()
        self.novo()

    def excluir(self):
        if self.lista.esta_vazia():
            return self.aviso("A lista está vazia: não há o que excluir.")
        if self.id_em_edicao is None:
            return self.aviso("Selecione um registro na tabela para excluir.")
        reg = self.lista.buscar_por_id(self.id_em_edicao)
        if not messagebox.askyesno("Confirmar exclusão", f"Excluir \"{reg.titulo}\"?", parent=self):
            return
        self.lista.remover(reg.id)
        self.gravar()
        self.atualizar_tabela()
        self.novo()
        self.msg(f"✔ Registro {reg.id} excluído. Restam {len(self.lista)}.")

    def consultar_id(self):
        txt = self.var_busca_id.get().strip()
        if not txt.isdigit() or int(txt) <= 0:
            return self.aviso("Digite um ID numérico positivo para consultar.")
        if self.lista.esta_vazia():
            return self.msg("ℹ A lista está vazia.")
        reg = self.lista.buscar_por_id(int(txt))
        if reg is None:
            self.atualizar_tabela([])
            return self.msg(f"ℹ Nenhum registro com o ID {txt}.")
        self.atualizar_tabela([reg])
        self.tabela.selection_set(str(reg.id))
        self.msg(f"Registro {reg.id} encontrado (busca sequencial por ID).")

    def pesquisar(self):
        termo = self.var_termo.get().strip()
        if not termo:
            return self.aviso("Digite um termo para pesquisar.")
        if self.lista.esta_vazia():
            return self.msg("ℹ A lista está vazia.")
        achados = busca_sequencial(self.lista, self.var_attr.get(), termo)
        self.atualizar_tabela(achados)
        if achados:
            self.msg(f"{len(achados)} resultado(s) para '{termo}' em {self.var_attr.get()}.")
        else:
            self.msg(f"ℹ Nenhum registro encontrado para '{termo}' em {self.var_attr.get()}.")

    def mostrar_todos(self):
        self.atualizar_tabela()
        self.msg(f"Mostrando todos os {len(self.lista)} registro(s).")

    def ordenar(self):
        if self.lista.esta_vazia():
            return self.msg("ℹ A lista está vazia: nada a ordenar.")
        algo = "merge" if self.var_algo.get() == "Merge Sort" else "insertion"
        self.lista.ordenar(CHAVES[self.var_crit.get()], algo, self.var_ordem.get() == "Decrescente")
        self.gravar()
        self.atualizar_tabela()
        self.msg(f"✔ Ordenado por {self.var_crit.get()} ({self.var_ordem.get().lower()}) com {self.var_algo.get()}.")

    def mostrar_estrutura(self):
        """Mostra a cadeia real de nós (cabeça → ... → None) para a demonstração."""
        win = tk.Toplevel(self)
        win.title("Estrutura · lista encadeada")
        win.configure(bg=LILAS)
        win.geometry("760x240")
        tk.Label(win, text="Lista encadeada (percurso da cabeça até a cauda)", bg=LILAS, fg=AMEIXA,
                 font=(self.f_titulo, 14, "bold")).pack(anchor="w", padx=20, pady=(16, 8))
        t = tk.Text(win, wrap="word", font=(self.f_texto, 11), bg=BRANCO, fg=AMEIXA,
                    relief="solid", bd=1, padx=12, pady=12)
        t.insert("1.0", self.lista.diagrama())
        t.config(state="disabled")
        t.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        self.msg(f"Estrutura exibida: {len(self.lista)} nó(s).")

    def mostrar_analise(self):
        dados = analise.resumo(self.lista)
        win = tk.Toplevel(self)
        win.title("Análise · cinclu")
        win.configure(bg=LILAS)
        win.geometry("640x470")
        tk.Label(win, text="Análise dos registros", bg=LILAS, fg=AMEIXA,
                 font=(self.f_titulo, 18, "bold")).pack(anchor="w", padx=20, pady=(16, 0))
        tk.Label(win, text=f"Total: {dados['total']} registro(s)", bg=LILAS, fg=TEXTO_SUAVE,
                 font=(self.f_texto, 11)).pack(anchor="w", padx=20)
        if dados["total"] == 0:
            tk.Label(win, text="Nenhum registro cadastrado ainda.", bg=LILAS, fg=AMEIXA).pack(pady=40)
            return
        c = tk.Canvas(win, bg=BRANCO, highlightthickness=1, highlightbackground=BORDA)
        c.pack(fill="both", expand=True, padx=20, pady=14)
        maior = max(dados["por_categoria"].values())
        for i, (cat, qtd) in enumerate(dados["por_categoria"].items()):
            y = 20 + i * 52
            pct = qtd * 100 / dados["total"]
            c.create_text(16, y, anchor="w", text=cat, fill=AMEIXA, font=(self.f_texto, 10, "bold"))
            comp = 0 if maior == 0 else int(380 * qtd / maior)
            c.create_rectangle(16, y + 12, 16 + max(comp, 2), y + 32, fill=CORES_CATEGORIAS[i], outline="")
            c.create_text(24 + max(comp, 2), y + 22, anchor="w", fill=TEXTO_SUAVE,
                          text=f"{qtd}  ({pct:.1f}%)", font=(self.f_texto, 10))
        self.msg(f"Análise: categoria predominante = {dados['categoria_predominante']}.")


def executar():
    CincluApp().mainloop()
