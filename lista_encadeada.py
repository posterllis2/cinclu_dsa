"""Lista encadeada simples implementada sem list/deque do Python
como armazenamento. Cada nó guarda um Registro e uma referência ao próximo."""

from modelo import Registro


class IdDuplicadoError(ValueError):
    pass


class No:
    __slots__ = ("dado", "proximo")

    def __init__(self, dado, proximo=None):
        self.dado = dado
        self.proximo = proximo


class ListaEncadeada:
    def __init__(self):
        self.cabeca = None
        self.cauda = None
        self._tamanho = 0

    # ---------- consultas básicas ----------
    def __len__(self):
        return self._tamanho

    def esta_vazia(self):
        return self.cabeca is None

    def __iter__(self):
        """Percurso: visita cada nó do início ao fim. O(n)."""
        atual = self.cabeca
        while atual is not None:
            yield atual.dado
            atual = atual.proximo

    def buscar_por_id(self, id):
        """Busca sequencial por identificador. O(n). Retorna None se não achar."""
        for reg in self:
            if reg.id == id:
                return reg
        return None

    def existe_id(self, id):
        return self.buscar_por_id(id) is not None

    def proximo_id_livre(self):
        """Maior id + 1 (sugestão para o usuário). O(n)."""
        maior = 0
        for reg in self:
            if reg.id > maior:
                maior = reg.id
        return maior + 1

    # ---------- inserção ----------
    def inserir_inicio(self, registro):
        """Insere no início. O(n) pela verificação de id único (O(1) sem ela)."""
        self._checar_duplicado(registro)
        self.cabeca = No(registro, self.cabeca)
        if self.cauda is None:
            self.cauda = self.cabeca
        self._tamanho += 1

    def inserir_fim(self, registro):
        """Insere no fim (ponteiro para a cauda). O(n) pela checagem de id único;
        a ligação do nó em si é O(1)."""
        self._checar_duplicado(registro)
        novo = No(registro)
        if self.cauda is None:
            self.cabeca = self.cauda = novo
        else:
            self.cauda.proximo = novo
            self.cauda = novo
        self._tamanho += 1

    def _checar_duplicado(self, registro):
        if not isinstance(registro, Registro):
            raise TypeError("Só é possível inserir objetos Registro.")
        if self.existe_id(registro.id):
            raise IdDuplicadoError(f"Já existe um registro com o ID {registro.id}.")

    # ---------- remoção ----------
    def remover(self, id):
        """Remove o nó com o id informado e devolve o Registro (ou None). O(n).
        Trata remoção na cabeça, no meio e na cauda, mantendo cabeca/cauda/tamanho."""
        anterior, atual = None, self.cabeca
        while atual is not None and atual.dado.id != id:
            anterior, atual = atual, atual.proximo
        if atual is None:
            return None
        if anterior is None:
            self.cabeca = atual.proximo
        else:
            anterior.proximo = atual.proximo
        if atual is self.cauda:
            self.cauda = anterior
        self._tamanho -= 1
        removido = atual.dado
        atual.proximo = None
        return removido

    # ---------- atualização ----------
    def atualizar(self, id, /, **novos_campos):
        """Atualiza campos (exceto id). Valida antes de gravar: se algo for
        inválido, o registro original permanece intacto. O(n)."""
        novos_campos.pop("id", None)
        atual = self.cabeca
        while atual is not None and atual.dado.id != id:
            atual = atual.proximo
        if atual is None:
            return None
        dados = atual.dado.para_dict()
        dados.update(novos_campos)
        atual.dado = Registro(**dados)  # levanta ValueError se inválido
        return atual.dado

    # ---------- ordenação (delegada a algoritmos.py) ----------
    def ordenar(self, chave, algoritmo="merge", reverso=False):
        import algoritmos
        if algoritmo == "merge":
            self.cabeca = algoritmos.merge_sort(self.cabeca, chave, reverso)
        elif algoritmo == "insertion":
            self.cabeca = algoritmos.insertion_sort(self.cabeca, chave, reverso)
        else:
            raise ValueError("Algoritmo de ordenação desconhecido.")
        # recalcula a cauda após religar os nós
        self.cauda = None
        atual = self.cabeca
        while atual is not None:
            self.cauda = atual
            atual = atual.proximo

    def diagrama(self):
        """Texto que mostra a cadeia de nós, da cabeça até None. O(n)."""
        if self.esta_vazia():
            return "cabeça → None   (lista vazia)"
        nos = " → ".join(f"[{r.id}]" for r in self)
        return f"cabeça → {nos} → None   |   cauda = [{self.cauda.dado.id}]   |   tamanho = {self._tamanho}"

    def limpar(self):
        self.cabeca = self.cauda = None
        self._tamanho = 0
