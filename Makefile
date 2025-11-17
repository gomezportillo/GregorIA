# Vars
VENV_DIR := gregoria-env
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

JSON_DIR := letters/json
PDF_DIR := letters/raw
OUTPUT_DIR := out/graph

# Dependencies
REQS := networkx plotly pandas jsonschema lxml pdfplumber

.PHONY: all setup install run clean

all: setup run

# Crear entorno virtual
$(VENV_DIR)/bin/activate:
	python3 -m venv $(VENV_DIR)

# Instalar dependencias en entorno virtual
install: $(VENV_DIR)/bin/activate
	$(PIP) install --upgrade pip
	$(PIP) install $(REQS)

setup: install

# Ejecutar el script
run:
	$(PYTHON) src/build_graph.py

# Limpiar archivos generados
clean:
	rm -rf $(VENV_DIR)
	rm -rf $(OUTPUT_DIR)
