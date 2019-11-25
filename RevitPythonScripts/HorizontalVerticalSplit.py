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
    print("  ➜ Found {num} pipes = {len} m in the model.".format(
        num=len(pipes), len=total_length(pipes)))

    # STEP 2: Filter pipes
    print("Filtering pipes by system type...", end="")
    sorted_pipes = sort_pipes(pipes, doc)
    print("✔")
    for key in sorted_pipes.keys():
        print("  ➜ Found {num} pipes = {len} m of type '{key}' in the model.".format(
            num=len(sorted_pipes[key]), len=total_length(sorted_pipes[key]), key=key))

    # STEP 3: Categorize pipes
    print("Categorizing pipes...", end="")
    categorized_pipes = categorize_pipes(sorted_pipes)
    print("✔")
    for key in categorized_pipes.keys():
        print("  ➜ Found {numh} horizontal pipes = {lenh} m an {numv} vertical pipes = {lenv} m of type '{key}' in the model.".format(
            numh=len(categorized_pipes[key]["horizontal"]), lenh=total_length(categorized_pipes[key]["horizontal"]),
            numv=len(categorized_pipes[key]["vertical"]), lenv=total_length(categorized_pipes[key]["vertical"]),
            key=key))


# Helpers:
def sort_pipes(pipes, doc):
    """Sort pipes by theri systems name."""
    sorted_pipes = {}
    for pipe in pipes:
        system = pipe.MEPSystem
        system_type = doc.GetElement(system.GetTypeId())
        system_abbreviation = system_type.Abbreviation
        try:  # to add a pipe to a list
            sorted_pipes[system_abbreviation].append(pipe)
        except KeyError:  # create the list if it soes not exist yet
            sorted_pipes[system_abbreviation] = [pipe, ]
    return sorted_pipes

def categorize_pipes(sorted_pipes):
    """Categorize vertical/horizontal pipes."""
    categorized_pipes = {}
    for key, pipes in sorted_pipes.items():
        categories = {"vertical": [], "horizontal": []}
        for pipe in pipes:
            if is_vertical(pipe):
                categories["vertical"].append(pipe)
            else:
                categories["horizontal"].append(pipe)
        categorized_pipes[key] = categories
    return categorized_pipes

def is_vertical(pipe, tolerance=1):
    """Check if a pipe is vertical (within the given angle tolerance)."""
    curve = pipe.Location.Curve
    point1 = curve.GetEndPoint(0)
    point2 = curve.GetEndPoint(1)
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
