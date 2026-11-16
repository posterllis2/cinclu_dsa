"""Testes automatizados.  Execute na pasta do projeto:
    python -m unittest discover -s testes -v
Cada CasoTeste de casos_teste.py vira um teste (observado deve ser igual ao esperado).
"""
import unittest

import casos_teste as ct


class TestCinclu(unittest.TestCase):
    pass


def _fabricar(caso):
    def teste(self):
        if caso.requer_gui and not ct.gui_disponivel():
            self.skipTest("Tkinter/display indisponível")
        obs, esp, ok = caso.executar()
        self.assertEqual(obs, esp)
    teste.__doc__ = f"{caso.area}: {caso.descricao}"
    return teste


for _c in ct.CASOS:
    setattr(TestCinclu, f"test_{_c.id}", _fabricar(_c))

if __name__ == "__main__":
    unittest.main()
