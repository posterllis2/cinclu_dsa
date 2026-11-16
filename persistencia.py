"""Persistência em arquivo JSON (funcionalidade opcional)."""
import json
import os
from lista_encadeada import ListaEncadeada, IdDuplicadoError
from modelo import Registro


class ErroPersistencia(Exception):
    pass


def salvar(lista, caminho):
    """Grava de forma atômica (arquivo temporário + os.replace) para não corromper."""
    pasta = os.path.dirname(os.path.abspath(caminho))
    os.makedirs(pasta, exist_ok=True)
    tmp = caminho + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump([r.para_dict() for r in lista], f, ensure_ascii=False, indent=2)
        os.replace(tmp, caminho)
    except OSError as e:
        raise ErroPersistencia(f"Não foi possível salvar: {e}")


def carregar(caminho):
    """Devolve ListaEncadeada, ou None se o arquivo não existir."""
    if not os.path.exists(caminho):
        return None
    lista = ListaEncadeada()
    try:
        with open(caminho, encoding="utf-8") as f:
            dados = json.load(f)
        if not isinstance(dados, list):
            raise ValueError("formato inesperado")
        for d in dados:
            lista.inserir_fim(Registro.de_dict(d))
    except (OSError, json.JSONDecodeError, ValueError, IdDuplicadoError, TypeError) as e:
        raise ErroPersistencia(f"Arquivo de dados inválido ({e}).")
    return lista
