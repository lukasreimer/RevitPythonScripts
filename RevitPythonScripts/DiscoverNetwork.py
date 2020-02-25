"""Generate a grph structure from revit element and connection information."""

from __future__ import print_function
import collections
import datetime
import json
import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui
clr.AddReference("System.Windows.Forms")
import System.Windows.Forms as swf

__name = "DiscoverNetwork.py"
__version = "0.1a"


class Network:
    """Pipe/duct network class."""

    def __init__(self):
        """Initializer."""
        self.nodes = {}  # {id1: [...], id2: [...], ...]
        self.edges = {}  # {(id1, id2): [...], (id1, id3): [...], ...}
        self.systems = []  # list of element ids of discovered systems
        self.meta = {}  # graph level metadata

    def discover(self, element):
        """Entry point for network discovery."""
        self.meta["model"] = doc.PathName
        self.meta["time"] = datetime.datetime.now().isoformat()
        self._discover(element)
        return self


    def _discover(self, element):
        """Private recursive network discovery method."""

        # Filter insulation and lining elements
        if isinstance(element, db.Plumbing.PipeInsulation) or\
            isinstance(element, db.Mechanical.DuctInsulation) or\
            isinstance(element, db.Mechanical.DuctLining):
            print("element is Insulation!")
            return  # don't store insulation and lining

        # Store element as node
        element_id = element.Id.IntegerValue
        if element_id in self.nodes:
            return  # element already discovered
        self.nodes[element_id] = {
            "id": element_id,
            "type": type(element).__name__}

        # Store systems for later
        if isinstance(element, db.MEPSystem):
            print("element is MEPSystem!", element_id)
            self.systems.append(element_id)

        # Discover references and store edges
        if isinstance(element, db.FamilyInstance):  # family instance (fittings, equipment, etc.)
            connectors = element.MEPModel.ConnectorManager.Connectors
        else:  # element is pipe or duct
            connectors = element.ConnectorManager.Connectors
        for connector in connectors:
            for reference in connector.AllRefs:
                owner = reference.Owner
                owner_id = owner.Id.IntegerValue
                if owner_id != element_id:
                    edge_key = tuple(sorted([element_id, owner_id]))  # undirected graph!
                    self.edges[edge_key] = {
                        "source": edge_key[0],
                        "target": edge_key[1]}
                self._discover(owner)
        return
    
    def split_systems(self):
        # TODO: split systems??
        raise NotImplementedError

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
    
    def write_json(self, path):
        """Output the network to a file in json format."""
        data = collections.OrderedDict([  # data structure to dump as json
            ("directed", False),
            ("multigraph", False),
            ("graph", self.meta),
            ("nodes", self.nodes.values()),
            ("links", self.edges.values())
        ])
        graph_data = json.dumps(data, indent=2)
        print(graph_data)
        try:
            with open(path, mode="w") as file:
                file.write(graph_data)
        except Exception as exception:
            print(exception)


def main():
    """Main function."""

    print("🐍 Running {name} version {ver}".format(name=__name, ver=__version))

    doc = __revit__.ActiveUIDocument.Document

    if not selection:
        print("✘ nothing selected.")
        return

    element = selection[0]
    network = Network()
    network.discover(element)

    print(len(network.nodes))
    print(len(network.edges))

    save_dialog = swf.SaveFileDialog()
    save_dialog.Title = "Save Discovered Network"
    save_dialog.Filter = "JSON files|*.json"
    save_dialog.FileName = "network.json"
    if save_dialog.ShowDialog() == swf.DialogResult.OK:
        file_path = save_dialog.FileName
        print("Writing report to {}".format(file_path))
        network.write_json(file_path)
        print("✔\nDone. 😊")
        return ui.Result.Succeeded
    else:
        print("🛈 File save dialog canceled.")
        return ui.Result.Cancelled


if __name__ == "__main__":
    #__window__.Hide()
    result = main()
    if result == ui.Result.Succeeded:
        __window__.Close()
