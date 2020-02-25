"""Read and display a graph from a json file."""

import json
import networkx as nx
import pyvis

from PySide2.QtWidgets import QApplication, QFileDialog


def main():
    """Main function."""

    app = QApplication()
    input_filename, _ = QFileDialog.getOpenFileName(
        None, "Open a Network for Display", "", "JSON file (*.json)")
    print(input_filename)

    if not input_filename:
        print("No input file name specified")
        return
    
    with open(input_filename, mode="r") as file:
        content = file.read()
        data = json.loads(content)
        graph = nx.readwrite.json_graph.node_link_graph(data)
    #print(graph)

    network = pyvis.network.Network(
        height="100%", width="75%", bgcolor="#222222", font_color="white")
    network.from_nx(graph)
    #print(network)
    
    output_filename, _ = QFileDialog.getSaveFileName(
        None, "Choose Output File Path", "network.html", "HTML file (*.html)")

    if not output_filename:
        print("No output file name specified")
        return

    network.show_buttons(filter_=["physics", "interaction"])
    network.show(output_filename)


if __name__ == "__main__":
    main()
