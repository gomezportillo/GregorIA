import json
import os
from glob import glob

import matplotlib.pyplot as plt
import networkx as nx

# Config
input_dir = "./letters/json/"
output_path = "./out/img/graph.png"


def extract_fields(letter_json):
    """
    Extrae los campos relevantes de una carta JSON.
    """
    sender = letter_json.get("sender_name") or letter_json.get("sender", {}).get("sender_name", "Unknown sender")
    recipient = letter_json.get("recipient_name") or letter_json.get("recipient", {}).get(
        "recipient_name", "Unknown recipient"
    )
    intent = letter_json.get("semantics", {}).get("intent") or letter_json.get("intent", "unknown")
    summary = letter_json.get("summary", "")

    return {
        "sender": sender,
        "recipient": recipient,
        "intent": intent,
        "summary": summary,
    }


def save_image(output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    print(f"Grafo combinado guardado en {output_path}")
    plt.show()


def main():
    # Create graph
    G = nx.DiGraph()

    for json_file in glob(os.path.join(input_dir, "*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            letter = json.load(f)
        fields = extract_fields(letter)
        G.add_node(fields["sender"])
        G.add_node(fields["recipient"])
        G.add_edge(fields["sender"], fields["recipient"], intent=fields["intent"], summary=fields["summary"])

    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(14, 10))
    nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=1500)
    nx.draw_networkx_edges(G, pos, arrowsize=20)
    labels = {n: n.replace(", ", "\n") for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10)

    save_image(output_path)


if __name__ == "__main__":
    main()
