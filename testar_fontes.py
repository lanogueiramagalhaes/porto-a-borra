
name: Testar fontes e recolher eventos

on:
  workflow_dispatch:
  push:
    paths:
      - "fontes.py"
      - "testar_fontes.py"
      - "recolher_eventos.py"
      - "requirements.txt"
      - ".github/workflows/testar-fontes.yml"

jobs:
  testar-e-recolher:
    runs-on: ubuntu-latest

    steps:
      - name: Obter código
        uses: actions/checkout@v4

      - name: Preparar Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Instalar dependências
        run: pip install -r requirements.txt

      - name: Testar fontes
        run: python testar_fontes.py

      - name: Recolher eventos
        run: python recolher_eventos.py

      - name: Guardar ficheiro de eventos
        uses: actions/upload-artifact@v4
        with:
          name: eventos-recolhidos
          path: eventos.json
          if-no-files-found: error
          retention-days: 7
