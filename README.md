# GregorIA - Visualización de las cartas de Gregorio Magno

Proyecto para procesar el corpus epistolar de Gregorio Magno y generar un grafo interactivo 3D que muestra las relaciones entre emisores, destinatarios y entidades mencionadas.

## Requisitos

- Python 3.8 o superior  
- [venv](https://docs.python.org/3/library/venv.html) para entorno virtual  
- Dependencias instaladas vía pip (se automatiza con Makefile)

---

## Cómo usarlo

1. Clona este repositorio y entra en la carpeta:

    ```bash
    git clone https://github.com/gomezportillo/gregoria.git
    cd tu-repositorio
    ```

2. Comandos Make disponibles

    ```
    make setup: crea el entorno y solo instala dependencias
    make run: ejecuta el script (requiere entorno y dependencias ya instaladas)
    make clean: elimina el entorno virtual y los archivos generados
    ```

3. Resultado

Abre `out/graph/gregory_letters_3d.html` con tu navegador para la visualización 3D interactiva.

---

## Licencia

Este proyecto es libre para uso académico y personal.
