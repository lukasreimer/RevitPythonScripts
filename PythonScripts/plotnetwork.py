import json
import networkx as nx
import pyvis


def read_file(path):
    """Read graph from file."""
    graph = nx.Graph()

    try:
        with open(path, mode="r") as file:
            for line in file:
                element, data = line.split(":")
                if element == "node":
                    graph.add_node(data.strip())
                elif element == "edge":
                    left, right = data.strip().split(",")
                    graph.add_edge(left.strip(), right.strip())
    except Exception as exception:
        pritn(exception)
    return graph


def main():
    """Main function."""
    
    # graph = read_file(r"C:\Users\lreimer\Desktop\network.txt")
    # print(graph)

    graph = None
    with open(r"C:\Users\lreimer\Desktop\example.json") as file:
        content = file.read()
        data = json.loads(content)
        graph = nx.readwrite.json_graph.node_link_graph(data)
    print(graph)

    network = pyvis.network.Network()
    network.from_nx(graph)
    print(network)

    network.show_buttons(filter_=['physics'])
    network.show(r"C:\Users\lreimer\Desktop\examplenetwork.html")


if __name__ == "__main__":
    main()
