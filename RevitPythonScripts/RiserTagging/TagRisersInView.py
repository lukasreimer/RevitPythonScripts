"""Tag all vertical risers in current view with the according symbol.

This script is finding all vertical pipes in the current plan view and
categorizes them based on flow (if available) and location. If the flow
nformation is not available on a pipe the script assumes downward flow as a
default.
After categorization the script places pipe riser tags at the pipes based on the
acquired information. It therefor uses a hardcoded mapping of categories to
annotation symbol family types.
"""

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

__name = "TagRisersInView.py"
__version = "0.2b"

# Constants
FEET_TO_METER = 0.3048  # meter/feet
TAG_FAMILY_NAME = "BHE_DE_PipeTag_FlowArrow"
TAG_TYPE_NAME_MAPPING = {  # hard coded tag names to use
    "Steigleitung": TAG_FAMILY_NAME + " - Steigleitung",
    "Fallleitung": TAG_FAMILY_NAME + " - Fallleitung",
    "VonOben": TAG_FAMILY_NAME + " - VonOben",
    "NachOben": TAG_FAMILY_NAME + " - NachOben",
    "VonUnten": TAG_FAMILY_NAME + " - VonUnten",
    "NachUnten": TAG_FAMILY_NAME + " - NachUnten",
}


def main():
    """Main Script. """
    
    print("🐍 Running {fname} version {ver}...".format(fname=__name, ver=__version))

    # STEP 0: Setup
    doc = __revit__.ActiveUIDocument.Document
    view = doc.ActiveView

    # STEP 1: Get all available Pipe Tags in the project
    print("Getting all available pipe tags from the model...", end="")
    tag_types = db.FilteredElementCollector(doc)\
                  .OfCategory(db.BuiltInCategory.OST_PipeTags)\
                  .WhereElementIsElementType()\
                  .ToElements()
    print("✔")
    tags = {}  # tag_title: tag_type
    for tag_type in tag_types:
        tag_family_name = tag_type.get_Parameter(db.BuiltInParameter.SYMBOL_FAMILY_NAME_PARAM).AsString()
        tag_type_name = tag_type.get_Parameter(db.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        full_tag_name = "{f_name} - {t_name}".format(f_name=tag_family_name, t_name=tag_type_name)
        tags[full_tag_name] = tag_type

    # STEP 2: Check if setup tags actually exist in project
    print("Checking if expected tag family (and types) exist(s)... ", end="")
    all_tags_available = True
    for tag_name in TAG_TYPE_NAME_MAPPING.values():
        if not tag_name in tags:
            print("✘ Error: {tag_name} not available!".format(tag_name=tag_name))
            all_tags_available = False
    if not all_tags_available:
        print("✘ Error: Not all required tags are available in the project! See above.")
        return ui.Result.Failed
    print("✔")

    # STEP 3: Check if the current view a plan view
    print("🛈 Current view is: '{v}' {t}".format(v=view.Name, t=type(view)))
    if type(view) is not db.ViewPlan:
        print("✘ Error: Currently active view is not a plan view!")
        return ui.Result.Failed
            
    # STEP 4: Get all pipes in the view
    print("Getting all pipes from the currently active view... ", end="")
    pipes = db.FilteredElementCollector(doc, view.Id)\
                .OfCategory(db.BuiltInCategory.OST_PipeCurves)\
                .ToElements()
    print("✔")
    print("  ➜ Found {num} pipes in the currently active view.".format(num=len(pipes)))

    # STEP 5: Filter for vertical pipes
    print("Filtering vertical pipes... ", end="")
    vertical_pipes = [pipe for pipe in pipes if is_vertical(pipe)]
    print("✔")
    print("  ➜ Found {num} vertical pipes in the view.".format(num=len(vertical_pipes)))

    # STEP 6: Get the top and bottom view range elevations
    print("Finding views boundary elevations... ", end="")
    top, bottom = top_and_bottom_elevation(doc, view)
    print("✔")
    print("  ➜ Top boundary elevation is {0} ft (= {1} m)".format(top, top*FEET_TO_METER))
    print("  ➜ Bottom boundary elevation is {0} ft (= {1} m)".format(bottom, bottom*FEET_TO_METER))

    # STEP 7: Categorize pipes according to location and flow
    print("Categorizing vertical pipes... ", end="")
    categorized_pipes, _ = categorize_pipes(vertical_pipes, top, bottom)
    print("✔")
    for category, pipes in categorized_pipes.items():
        print("  ➜ Found {num} pipes in category '{cat}'".format(num=len(pipes), cat=category))

    # STEP 8: Place tags at the pipes TODO: avoid creating duplicate tags
    print("Creating tags... ", end="")
    transaction = db.Transaction(doc)
    transaction.Start("{name} - v{ver}".format(name=__name, ver=__version))
    try:
        for category, pipes in categorized_pipes.items():
            tag_type_id = tags[TAG_TYPE_NAME_MAPPING[category]].Id
            for pipe in pipes:
                point = pipe_location(pipe, top)
                new_tag = db.IndependentTag.Create(doc, view.Id, db.Reference(pipe), False, db.TagMode.TM_ADDBY_CATEGORY, db.TagOrientation.Horizontal, point)
                new_tag.ChangeTypeId(tag_type_id)
    except Exception as ex:
        print("\n✘ Exception:\n {ex}".format(ex=ex))
        transaction.RollBack()
        return ui.Result.Failed
    else:
        transaction.Commit()
        print("✔\nDone. 😊")
        return ui.Result.Succeeded


# Helpers:
def get_connectors(pipe):
    """Get the connector elements of a pipe."""
    connector_set = pipe.ConnectorManager.Connectors
    connectors = [connector for connector in connector_set.GetEnumerator()]
    assert len(connectors) == 2
    return connectors

def categorize_pipes(vertical_pipes, top, bottom):
    """Categorize vertical pipes based on location in the view and flow.

    Default to assuming downward flow (gravity) when no flow information is
    available for the investigated pipe element.
    """
    categorized_pipes = {key: [] for key in TAG_TYPE_NAME_MAPPING.keys()}
    uncategorized_pipes = []
    for pipe in vertical_pipes:
        # connector_set = pipe.ConnectorManager.Connectors
        # connectors = [connector for connector in connector_set.GetEnumerator()]
        # assert len(connectors) == 2
        connectors = get_connectors(pipe)
        # print(connectors)
        if any([connector.Direction == db.FlowDirectionType.Bidirectional for connector in connectors]):
            start, end = get_high_low(pipe)
        else:
            start, end = get_in_out(pipe)
        if start >= end:  # → pipe going down
            if start >= top and bottom >= end:
                categorized_pipes["Fallleitung"].append(pipe)
            elif start >= top and top >= end >= bottom:
                categorized_pipes["VonOben"].append(pipe)
            elif top >= start >= bottom and bottom >= end:
                categorized_pipes["NachUnten"].append(pipe)
            else:  # pipe does not extend out of the view range
                uncategorized_pipes.append(pipe)
        else:  # start < end --> pipe going up
            if end >= top and bottom >= start:
                categorized_pipes["Steigleitung"].append(pipe)
            elif end >= top and top >= start >= bottom:
                categorized_pipes["NachOben"].append(pipe)
            elif top >= end >= bottom and bottom >= start:
                categorized_pipes["VonUnten"].append(pipe)
            else:  # pipe does not extend out of the view range
                uncategorized_pipes.append(pipe)
    return categorized_pipes, uncategorized_pipes

def get_in_out(pipe):
    """Get the inflow and the outflow elevations from two arbitrary points."""
    # assert len(connectors) >= 2
    # first = connectors[0]
    # second = connectors[1]
    first, second = get_connectors(pipe)
    direction1, direction2 = first.Direction, second.Direction
    #direction2 = second.Direction
    if direction1 == db.FlowDirectionType.In and direction2 == db.FlowDirectionType.Out:
        inflow = first.Origin.Z
        outflow = second.Origin.Z
    elif direction1 == db.FlowDirectionType.Out and direction2 == db.FlowDirectionType.In:
        inflow = second.Origin.Z
        outflow = first.Origin.Z
    else:  # some connector is bidirectional or both are equal, use high/low
        inflow, outflow = get_high_low(pipe)
    return inflow, outflow

def get_high_low(pipe):
    """Get the higher and the lower elevations from two arbitrary points."""
    # assert len(connectors) >= 2
    # first = connectors[0]
    # second = connectors[1]
    first, second = get_connectors(pipe)
    point1, point2 = first.Origin, second.Origin
    #point2 = second.Origin
    high = max(point1.Z, point2.Z)
    low = min(point1.Z, point2.Z)
    return high, low

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


def top_and_bottom_elevation(doc, view):
    """Extract top and bottom elevation of a plan view.
    
    If undefined "Level Above" or "Level Below" are specified in the View Range,
    the generating level of the view and the according offset (top / bottom)
    are used for specifying the top and bottom elevations.
    """
    view_level = view.GenLevel
    #print("view level =", view_level)
    view_range = view.GetViewRange()
    #print("view_range =", view_range)
    top_level_id = view_range.GetLevelId(db.PlanViewPlane.TopClipPlane)
    #print("top_level_id =", top_level_id)
    if top_level_id == view_range.LevelAbove:
        #print("'Level Above' Specified for top plane!!! --> using View Level.")
        top_level = view_level
    else:
        top_level = doc.GetElement(top_level_id)
    #print("top_level =", top_level)
    bottom_level_id = view_range.GetLevelId(db.PlanViewPlane.BottomClipPlane)
    #print("bottom_level_id =", bottom_level_id)
    if bottom_level_id == view_range.LevelBelow:
        #print("Level Below Specified for bottom plane!!! --> using View Level.")
        bottom_level = view_level
    else:
        bottom_level = doc.GetElement(bottom_level_id)
    #print("bottom_level =", bottom_level)
    top_offset = view_range.GetOffset(db.PlanViewPlane.TopClipPlane)
    #print("top_offset =", top_offset)
    bottom_offset = view_range.GetOffset(db.PlanViewPlane.BottomClipPlane)
    #print("bottom_offset =", bottom_offset)
    top_elevation = top_level.ProjectElevation + top_offset
    #print("top_elevation =", top_elevation)
    bottom_elevation = bottom_level.ProjectElevation + bottom_offset
    #print("bottom_elevation =", bottom_elevation)
    assert top_elevation >= bottom_elevation
    return top_elevation, bottom_elevation


def pipe_location(pipe, elevation):
    """Returns the intersetion point of the pipe with the elevation."""
    # ! Assuming the pipe is vertical for now ! TODO: implement level/pipe intersection
    curve = pipe.Location.Curve
    pipe_point = curve.GetEndPoint(0)
    point = db.XYZ(pipe_point.X, pipe_point.Y, elevation)
    return point


if __name__ == "__main__":
    #__window__.Hide()
    result = main()
    # if result == ui.Result.Succeeded:
    #     __window__.Close()
