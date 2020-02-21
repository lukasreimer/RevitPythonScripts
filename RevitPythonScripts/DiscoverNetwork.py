"""
Generate a grph structure from revit element and connection information.
"""

from __future__ import print_function


class Network:
    """Pipe/duct network class."""

    def __init__(self):
        """Initializer."""
        self.nodes = []  # [id1, id2, ...]
        self.edges = set()  # {(id1, id2), (id1, id3), ...}
        self.systems = []

    def discover(self, element):
        """Recursive network discovery method."""
        # TODO: Filter insulation objects?

        if isinstance(element, db.Plumbing.PipeInsulation):
            print("element is Insulation!")
            return

        element_id = element.Id.IntegerValue
        #print("element_id:", element_id)
        if element_id in self.nodes or element_id in self.edges:
            #print("element already discovered:", element)
            return 
        #print("discovering element:", element)
        self.nodes.append(element_id)

        if isinstance(element, db.MEPSystem):
            print("element is MEPSystem!", element_id)
            self.systems.append(element_id)
            return

        if isinstance(element, db.FamilyInstance):  # family instance (fittings, equipment)
            #print("element is FamilyInstance")
            connectors = element.MEPModel.ConnectorManager.Connectors
        else:  # pipes and ducts
            #print("element is not FamilyInstance")
            connectors = element.ConnectorManager.Connectors

        for connector in connectors:
            #print("checking connector:", connector)
            for reference in connector.AllRefs:
                #print("checking reference:", reference)
                owner = reference.Owner
                owner_id = owner.Id.IntegerValue
                if owner_id != element_id:
                    edge = tuple(sorted([element_id, owner_id]))
                    self.edges.add(edge)
                self.discover(owner)
        return
    
    def remove_systems(self):
        system_edges = []
        for system_id in self.systems:
            self.nodes.remove(system_id)
            for edge in self.edges:
                if system_id in edge:
                    system_edges.append(edge)
        for system_edge in system_edges:
                self.edges.remove(system_edge)

    def write(self, path):
        """Output the network to a file."""
        try:
            with open(path, mode="w") as file:
                for node in self.nodes:
                    file.write("node: {}\n".format(node))
                for edge in self.edges:
                    file.write("edge: {}, {}\n".format(edge[0], edge[1]))
        except Exception as exception:
            print(exception)


def main():
    """Main function."""
    if not selection:
        print("nothing selected")
        return

    element = selection[0]
    network = Network()
    network.discover(element)

    print(len(network.edges))
    network.remove_systems()
    print(len(network.edges))

    # print("nodes: # =", len(network.nodes))
    # for node in network.nodes:
    #     print(node)
    # print("edges: # =", len(network.edges))
    # for edge in network.edges:
    #     print(edge)

    network.write(r"C:\Users\lreimer\Desktop\network.txt")


if __name__ == "__main__":
    main()
