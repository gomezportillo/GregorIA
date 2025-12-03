# Vars
VENV_DIR := gregoria-env
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

# Directories
TXT_DIR := letters/txt
OUTPUT_DIR := out/graph

# Dependencies
REQS := networkx matplotlib pyvis

.PHONY: all setup install run clean parse

all: setup run

# Crear entorno virtual
$(VENV_DIR)/bin/activate:
	python3 -m venv $(VENV_DIR)

activate:
	@echo "Run 'source $(VENV_DIR)/bin/activate' in your shell to activate the environment"

# Instalar dependencias en entorno virtual
install: $(VENV_DIR)/bin/activate
	$(PIP) install --upgrade pip
	$(PIP) install $(REQS)

setup: install

# Ejecutar el script principal
run:
	$(PYTHON) src/build_graph.py

# Parsear las epístolas
parse:
	$(PYTHON) src/parse_epistolarum.py

# Limpiar archivos generados
clean:
	rm -rf $(VENV_DIR)
	rm -rf $(OUTPUT_DIR) $(TXT_DIR)
