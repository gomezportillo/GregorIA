import json
import os
from glob import glob

import matplotlib.pyplot as plt
import networkx as nx
from pyvis.network import Network

INPUT_DIR = "./letters/json/"
OUTPUT_IMG = "./out/img/graph.png"
OUTPUT_HTML = "./out/html/graph.html"


def extract_fields(letter):
    """
    Extrae campos clave de la carta JSON.
    """
    sender = letter.get("sender_name") or letter.get("sender", {}).get("sender_name", "Unknown sender")
    recipient = letter.get("recipient_name") or letter.get("recipient", {}).get("recipient_name", "Unknown recipient")
    intent = letter.get("semantics", {}).get("intent") or letter.get("intent", "unknown")
    summary = letter.get("summary", "")
    year = letter.get("date", {}).get("year") or letter.get("year", "unknown")

    return sender, recipient, intent, summary, year


def build_graph(input_dir):
    """
    Construye un grafo dirigido a partir de los JSONs en input_dir.
    """
    G = nx.DiGraph()
    json_files = glob(f"{input_dir}/*.json")

    if not json_files:
        print(f"⚠️ No se encontraron archivos JSON en {input_dir}")
        return G

    for json_file in json_files:
        with open(json_file, "r", encoding="utf-8") as f:
            letter = json.load(f)
        sender, recipient, intent, summary, year = extract_fields(letter)
        G.add_node(sender)
        G.add_node(recipient)
        G.add_edge(
            sender,
            recipient,
            intent=intent,
            summary=summary,
            year=year,
        )

        # Personas mencionadas
        secondary = letter.get("entities_secondary", {}).get("people_secondary", [])
        for person in secondary:
            name = person.get("name")
            if not name:
                continue

            G.add_node(name)
            G.add_edge(
                sender,
                name,
                style="dashed",
                reference=True,
                year=year,
            )

    return G


def save_graph_image(G, output_img):
    """
    Dibuja y guarda el grafo como imagen PNG.
    """
    os.makedirs(os.path.dirname(output_img), exist_ok=True)

    plt.figure(figsize=(14, 10))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=1500)
    nx.draw_networkx_edges(G, pos, arrowsize=20)
    labels = {n: n.replace(", ", "\n") for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10)

    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_img)
    plt.close()
    print(f"✔ Imagen PNG guardada en {output_img}")


def save_graph_html(G, output_html):
    """
    Genera y guarda grafo interactivo en HTML usando PyVis.
    """
    os.makedirs(os.path.dirname(output_html), exist_ok=True)

    net = Network(height="800px", width="100%", directed=True)
    # Convertir grafo a PyVis con estilos
    for u, v, data in G.edges(data=True):
        edge_color = "#000000"
        dashes = False
        if data.get("reference"):
            edge_color = "#999999"
            dashes = True
        net.add_node(u, label=u)
        net.add_node(v, label=v)

        reference = "Reference\n" if data.get("reference") else ""
        intent = f"Intent: {data.get('intent')}\n" if data.get("intent") else ""
        year = f"Year: {data.get('year')}\n" if data.get("year") else ""
        summary = f"Summary: {data.get('summary')}" if not reference and data.get("summary") else ""

        net.add_edge(u, v, color=edge_color, dashes=dashes, title=f"{reference} {intent} {year} {summary}")

    net.force_atlas_2based()
    # net.show_buttons(filter_=['physics'])
    net.write_html(output_html)

    print(f"✔ Grafo HTML interactivo guardado en {output_html}")


def main():
    G = build_graph(INPUT_DIR)

    if len(G) == 0:
        print("❌ Grafo vacío, nada que hacer.")
        return

    save_graph_image(G, OUTPUT_IMG)
    save_graph_html(G, OUTPUT_HTML)


if __name__ == "__main__":
    main()
