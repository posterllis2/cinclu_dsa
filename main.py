"""Ponto de entrada do Cinclu.
    python main.py        -> interface gráfica (modo principal)
    python main.py --cli  -> menu em terminal
"""
import sys

if __name__ == "__main__":
    if "--cli" in sys.argv:
        import cli
        cli.executar()
    else:
        try:
            import gui
        except ImportError:
            print("Tkinter não está disponível neste Python. Usando o modo terminal.")
            import cli
            cli.executar()
        else:
            gui.executar()
