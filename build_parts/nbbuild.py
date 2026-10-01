"""nbbuild.py — utilidades para construir los notebooks del curso de robótica.

Cada notebook se describe como una lista de celdas (markdown o código) y este
módulo la convierte en un fichero .ipynb con:
  - tema oscuro (una celda de estilo al principio),
  - kernel 'robotica' (el venv del proyecto),
  - metadatos limpios.

Uso desde un script de build (por ejemplo build_parts/nb00.py):

    from nbbuild import md, code, build
    cells = [ md("# Título"), code("print('hola')"), ... ]
    build("notebooks/NB00_...ipynb", cells, title="NB00 · ...")

Regenerar y verificar un notebook:

    cd robotica && source venv/bin/activate
    python build_parts/nb00.py
    python -m jupyter nbconvert --to notebook --execute --inplace \
        --ExecutePreprocessor.timeout=600 notebooks/NB00_*.ipynb
"""
from __future__ import annotations
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell


# --- Tema oscuro -----------------------------------------------------------
# Se inyecta como primera celda (markdown con un bloque <style>). Da fondo
# oscuro y tipografía cómoda tanto en Jupyter como en nbviewer / VS Code.
DARK_CSS = """<style>
.jp-Notebook, .jp-Cell, body.jp-Notebook, .cell, div#notebook, .notebook {
  background-color: #0f1115 !important;
}
.jp-RenderedMarkdown, .rendered_html, .jp-RenderedHTMLCommon {
  color: #e6e6e6 !important; font-size: 16px; line-height: 1.6;
}
.jp-RenderedMarkdown h1, .jp-RenderedMarkdown h2, .jp-RenderedMarkdown h3,
.rendered_html h1, .rendered_html h2, .rendered_html h3 { color: #8ec7ff !important; }
.jp-RenderedMarkdown h1, .rendered_html h1 {
  border-bottom: 2px solid #2b4a6f; padding-bottom: .2em;
}
.jp-RenderedMarkdown a, .rendered_html a { color: #7fd1c1 !important; }
.jp-RenderedMarkdown code, .rendered_html code {
  background: #1b2430 !important; color: #ffd479 !important;
  padding: 1px 5px; border-radius: 4px;
}
.jp-RenderedMarkdown pre, .rendered_html pre {
  background: #1b2430 !important; color: #e6e6e6 !important;
  border-left: 3px solid #2b4a6f; padding: .6em .9em; border-radius: 6px;
}
.jp-RenderedMarkdown blockquote, .rendered_html blockquote {
  border-left: 4px solid #7fd1c1; color: #bcd; background: #141a22;
  padding: .3em 1em; border-radius: 0 6px 6px 0;
}
.jp-RenderedMarkdown table, .rendered_html table { color: #e6e6e6; }
.jp-RenderedMarkdown th, .rendered_html th { background: #1b2430 !important; }
</style>
"""


def md(text: str):
    return ("md", text)


def code(text: str):
    return ("code", text)


def code_err(text: str):
    """Celda de código que FALLA a propósito (para enseñar a leer errores).

    Lleva la etiqueta 'raises-exception': al verificar con nbconvert, el error se
    muestra en la salida pero no detiene la ejecución del resto del notebook.
    """
    return ("code_err", text)


def build(path: str, cells, title: str | None = None, add_theme: bool = True):
    """Escribe un .ipynb a partir de la lista de celdas."""
    nb = new_notebook()
    out = []
    if add_theme:
        out.append(new_markdown_cell(DARK_CSS))
    for kind, text in cells:
        if kind == "md":
            out.append(new_markdown_cell(text))
        elif kind == "code":
            out.append(new_code_cell(text))
        elif kind == "code_err":
            out.append(new_code_cell(text, metadata={"tags": ["raises-exception"]}))
        else:
            raise ValueError(f"Tipo de celda desconocido: {kind!r}")
    nb.cells = out
    nb.metadata["kernelspec"] = {
        "name": "robotica",
        "display_name": "Python (robotica)",
        "language": "python",
    }
    nb.metadata["language_info"] = {"name": "python"}
    if title:
        nb.metadata["title"] = title
    nbf.write(nb, path)
    n_code = sum(1 for k, _ in cells if k in ("code", "code_err"))
    print(f"escrito {path}  ({len(cells)} celdas, {n_code} de código)")
    return path
