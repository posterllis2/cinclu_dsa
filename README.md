# Cinclu · Cidade Inclusiva

Protótipo do **Citizen Assist AI** (Global Solution 2026.2 · Data Structures and Algorithms) com foco em apoio à
população LGBTQIA+: saúde, direitos e documentação, denúncia e proteção, acolhimento e educação/trabalho.

**Autores:** Enzo Posterlli Strinta (RM 570035) · Giovanna Tristão Lopes (RM 572552)· Leonardo Robert Maulicino (RM 570329)

## Requisitos
- Python 3.8 ou superior. Apenas biblioteca padrão (sem `pip install`).
- Tkinter para a interface gráfica (já vem no Python do Windows/macOS; no Linux: `sudo apt install python3-tk`).
- Opcional: fontes *Bricolage Grotesque* e *Instrument Sans* (a interface usa Helvetica se não estiverem instaladas).

## Como executar
```bash
python main.py          # interface gráfica (modo principal)
python main.py --cli    # menu em terminal
```
Os dados ficam em `dados/servicos.json` (criado na primeira execução com 14 registros de exemplo).
Para voltar ao conjunto inicial, apague esse arquivo.

## Testes
```bash
python -m unittest discover -s testes -v   # 82 casos (15 de interface gráfica exigem Tkinter e tela)
python testes/evidencias.py                # tabela entrada / esperado / observado (+ testes/evidencias.json)
```

## Estrutura
| Arquivo | Função |
|---|---|
| `modelo.py` | Classe `Registro`, categorias e validação |
| `lista_encadeada.py` | `No` e `ListaEncadeada` (inserção, percurso, consulta, remoção, atualização, diagrama) |
| `algoritmos.py` | Busca sequencial, Merge Sort e Insertion Sort (implementação própria) |
| `analise.py` | Contagem por categoria e percentuais |
| `persistencia.py` | Gravação/leitura em JSON (opcional) |
| `dados_iniciais.py` | Registros de exemplo (revisar antes de divulgar) |
| `cli.py` / `gui.py` / `main.py` | Menu em terminal, interface gráfica e ponto de entrada |
| `testes/` | Casos de teste e gerador de evidências |

> Os registros de exemplo são ilustrativos: confira telefones, endereços e normas antes de qualquer uso real.
