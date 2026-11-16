"""Executa todos os casos e gera a tabela de evidências (terminal + JSON).
    python testes/evidencias.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import casos_teste as ct


def main():
    gui_ok = ct.gui_disponivel()
    resultados = []
    for c in ct.CASOS:
        if c.requer_gui and not gui_ok:
            resultados.append(dict(id=c.id, area=c.area, descricao=c.descricao, entrada=c.entrada,
                                   esperado=c.esperado(), observado="(ignorado: sem Tkinter/display)", status="IGNORADO"))
            continue
        obs, esp, ok = c.executar()
        resultados.append(dict(id=c.id, area=c.area, descricao=c.descricao, entrada=c.entrada,
                               esperado=esp, observado=obs, status="PASSOU" if ok else "FALHOU"))
    for r in resultados:
        print(f"{r['id']} [{r['status']}] {r['area']} – {r['descricao']}")
        print(f"     entrada : {r['entrada']}\n     esperado: {r['esperado']}\n     observado: {r['observado']}")
    n_ok = sum(r["status"] == "PASSOU" for r in resultados)
    print(f"\n{n_ok}/{len(resultados)} casos passaram.")
    saida = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidencias.json")
    with open(saida, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    return 0 if n_ok == len(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
