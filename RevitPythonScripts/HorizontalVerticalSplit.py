"""Split all pipes into horizontal and vertical pipes."""

from __future__ import print_function
import math
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
import System.Windows.Forms as swf
import System.Drawing as sd

__name = "HorizontalVerticalSplit.py"
__version = "0.1a"

# Constsants:
FEET_2_METER = 0.3048

# Variables:
FILTER = "SWL"  # TODO: detect all available system names and run analysis for all at once


def main():
    """Main Script. """
    
    print("🐍 Running {fname} version {ver}...".format(fname=__name, ver=__version))

    # STEP 0: Setup
    doc = __revit__.ActiveUIDocument.Document
    view = doc.ActiveView

    # STEP 1: Get all pipes in the model
    print("Getting all pipe from the model...", end="")
    pipes = db.FilteredElementCollector(doc)\
              .OfCategory(db.BuiltInCategory.OST_PipeCurves)\
              .WhereElementIsNotElementType()\
              .ToElements()
    print("✔")
    print("  ➜ Found {num} pipes in the model.".format(num=len(pipes)))

    # STEP 2: Filter pipes
    print("Filtering pipes by system type...", end="")
    interesting_pipes = []
    for pipe in pipes:
        system = pipe.MEPSystem
        system_type = doc.GetElement(system.GetTypeId())
        system_name = system_type.get_Parameter(db.BuiltInParameter.RBS_SYSTEM_ABBREVIATION_PARAM).AsString()
        if system_name == FILTER:
            interesting_pipes.append(pipe)
    print("✔")
    print("  ➜ Found {num} interesting pipes in the model. Filtered for '{fil}'.".format(num=len(interesting_pipes), fil=FILTER))

    # STEP 3: Categorize pipes
    print("Categorizing pipes...", end="")
    categorized_pipes = categorize_pipes(interesting_pipes)
    print("✔")
    print("  ➜ Found {num} horizontal pipes in the model.".format(num=len(categorized_pipes["horizontal"])))
    print("  ➜ Found {num} vertical pipes in the model.".format(num=len(categorized_pipes["vertical"])))

    # Step 4: Calculate total lengths and print results
    print("Results:")
    print("  ➜ Found {len} m of horizontal pipes in the model.".format(len=total_length(categorized_pipes["horizontal"])))
    print("  ➜ Found {len} m of vertical pipes in the model.".format(len=total_length(categorized_pipes["vertical"])))


# Helpers:
def get_connectors(pipe):
    """Get the connector elements of a pipe."""
    connector_set = pipe.ConnectorManager.Connectors
    connectors = [connector for connector in connector_set.GetEnumerator()]
    assert len(connectors) == 2
    return connectors

def categorize_pipes(pipes):
    """Categorize vertical pipes based on location in the view and flow.

    Default to assuming downward flow (gravity) when no flow information is
    available for the investigated pipe element.
    """
    categorized_pipes = {"vertical": [], "horizontal": []}
    for pipe in pipes:
        if is_vertical(pipe):
            categorized_pipes["vertical"].append(pipe)
        else:
            categorized_pipes["horizontal"].append(pipe)
    return categorized_pipes

def get_points(pipe):
    """Get the start and end point of a pipe."""
    curve = pipe.Location.Curve
    point0 = curve.GetEndPoint(0)
    point1 = curve.GetEndPoint(1)
    return point0, point1

def is_vertical(pipe, tolerance=1):
    """Check if a pipe is vertical (within the given angle tolerance)."""
    point1, point2 = get_points(pipe)
    dz = abs(point1.Z - point2.Z)
    if dz:  # is not horizontal
        dx = abs(point1.X - point2.X)
        dy = abs(point1.Y - point2.Y)
        dxy = math.sqrt(dx ** 2 + dy ** 2)
        alpha = math.degrees(math.atan2(dxy, dz))
        if alpha < tolerance:
            return True  # is vertical
    return False  # is not vertical

def total_length(pipes):
    """Calculate the total length of a list of pipes."""
    total_length_m = 0
    for pipe in pipes:
    	parameter = pipe.get_Parameter(db.BuiltInParameter.CURVE_ELEM_LENGTH)
    	length_m = parameter.AsDouble() * FEET_2_METER
    	total_length_m += length_m
    return total_length_m


if __name__ == "__main__":
    #__window__.Hide()
    result = main()
    if result == ui.Result.Succeeded:
        __window__.Close()
