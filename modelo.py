"""Modelo de dados do Cinclu: o registro de serviço/orientação."""

CATEGORIAS = (
    "Saúde",
    "Saúde Mental",
    "Direitos e Documentação",
    "Denúncia e Proteção",
    "Acolhimento e Assistência Social",
    "Educação e Trabalho",
)

LIMITES = {"titulo": 80, "descricao": 500, "requisitos": 300, "local": 150, "contato": 100}


class Registro:
    """Um serviço ou orientação cadastrado no Cinclu."""

    CAMPOS = ("id", "titulo", "categoria", "descricao", "requisitos", "local", "contato")

    def __init__(self, id, titulo, categoria, descricao, requisitos, local, contato=""):
        self.id = id
        self.titulo = titulo
        self.categoria = categoria
        self.descricao = descricao
        self.requisitos = requisitos
        self.local = local
        self.contato = contato
        self.validar()

    def validar(self):
        """Levanta ValueError com mensagem amigável se algum campo for inválido."""
        if isinstance(self.id, bool) or not isinstance(self.id, int) or self.id <= 0:
            raise ValueError("O identificador deve ser um número inteiro positivo.")
        if self.categoria not in CATEGORIAS:
            raise ValueError("Categoria inexistente.")
        for campo in ("titulo", "descricao", "requisitos", "local"):
            valor = getattr(self, campo)
            if not isinstance(valor, str) or not valor.strip():
                raise ValueError(f"O campo '{campo}' é obrigatório.")
        for campo, limite in LIMITES.items():
            valor = getattr(self, campo)
            if not isinstance(valor, str):
                raise ValueError(f"O campo '{campo}' deve ser texto.")
            if len(valor) > limite:
                raise ValueError(f"O campo '{campo}' excede {limite} caracteres.")

    def para_dict(self):
        return {c: getattr(self, c) for c in self.CAMPOS}

    @classmethod
    def de_dict(cls, d):
        try:
            return cls(**{c: d[c] for c in cls.CAMPOS if c in d})
        except TypeError as e:  # campos obrigatórios ausentes
            raise ValueError(f"Registro incompleto: {e}")

    def __str__(self):
        linhas = [
            f"[{self.id}] {self.titulo}",
            f"  Categoria : {self.categoria}",
            f"  Descrição : {self.descricao}",
            f"  Requisitos: {self.requisitos}",
            f"  Local     : {self.local}",
        ]
        if self.contato:
            linhas.append(f"  Contato   : {self.contato}")
        return "\n".join(linhas)
