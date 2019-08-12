"""Tag vertical risers in current view."""

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
__version = "0.2a"


# TODO: research and implement categorization according to pipe connectors (IN, OUT) -> flow direction
def main():
    """Main Script

    This script is tagging all vertical pipe risers in the current view.
    """
    
    print("Running {fname} version {ver}...".format(fname=__name, ver=__version))

    # STEP 0: Setup
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

     # STEP 1: Get all available System Types in the project
    print("Getting all available piping system types from the model...")
    system_types = db.FilteredElementCollector(doc)\
                        .OfClass(db.Plumbing.PipingSystemType)\
                        .ToElements()
    systems = {}  # system_name: system
    for system in system_types:
        name = system.get_Parameter(db.BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
        systems[name] = system

    # STEP 2: Get all available Pipe Tags in the project
    print("Getting all available pipe tags from the model...")
    tag_types = db.FilteredElementCollector(doc)\
                  .OfCategory(db.BuiltInCategory.OST_PipeTags)\
                  .WhereElementIsElementType()\
                  .ToElements()
    tags = {}  # tag_title: tag_type
    for tag_type in tag_types:
        tag_family_name = tag_type.get_Parameter(db.BuiltInParameter.SYMBOL_FAMILY_NAME_PARAM).AsString()
        tag_type_name = tag_type.get_Parameter(db.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        full_tag_name = "{f_name} - {t_name}".format(f_name=tag_family_name, t_name=tag_type_name)
        tags[full_tag_name] = tag_type

    # STEP 3: Try if the mapping between types and tags works
    print("Trying matching pipe systems and tags...")
    # TODO

    print("Current view is: '{v}' {t}".format(v=view.Name, t=type(view)))
    if type(view) is db.ViewPlan:
               
        # STEP 4: Get all vertical pipes in the view
        print("Getting all pipes from the currently active view...")
        pipes = db.FilteredElementCollector(doc, view.Id)\
                  .OfCategory(db.BuiltInCategory.OST_PipeCurves)\
                  .ToElements()
        print("Found {num} pipes in the currently active view.".format(num=len(pipes)))
        vertical_pipes = [pipe for pipe in pipes if is_vertical(pipe)]
        print("Found {num} vertical pipes in the view.".format(num=len(vertical_pipes)))

        # STEP 5: Filter all pipes crossing upper and lower view range boundary
        top, bottom = top_and_bottom_elevation(doc, view)  
        print("Top boundary elevation is {0} ft".format(top))
        print("Bottom boundary elevation is {0} ft".format(bottom))
        upper_pipes = [pipe for pipe in vertical_pipes if cuts_top_only(pipe, top, bottom)]
        lower_pipes = [pipe for pipe in vertical_pipes if cuts_bottom_only(pipe, top, bottom)]
        both_pipes =[pipe for pipe in vertical_pipes if cuts_top_and_bottom(pipe, top, bottom)]
        print("Found {num} pipes crossing upper boundary only.".format(num=len(upper_pipes)))
        print("Found {num} pipes crossing lower boundary only.".format(num=len(lower_pipes)))
        print("Found {num} pipes crossing both boundaries.".format(num=len(both_pipes)))

        # STEP 6: Place tags at the pipes
        print("Creating tags...")
        transaction = db.Transaction(doc)
        transaction.Start("{name} - v{ver}".format(name=__name, ver=__version))
        try:
            # for pipe in upper_pipes:
            #     point = pipe_location(pipe, top)
            #     new_tag = db.IndependentTag.Create(doc, view.Id, db.Reference(pipe), False, db.TagMode.TM_ADDBY_CATEGORY, db.TagOrientation.Horizontal, point)
            #     new_tag.ChangeTypeId(selected_top_tag.Id)
            # for pipe in lower_pipes:
            #     point = pipe_location(pipe, bottom)
            #     new_tag = db.IndependentTag.Create(doc, view.Id, db.Reference(pipe), False, db.TagMode.TM_ADDBY_CATEGORY, db.TagOrientation.Horizontal, point)
            #     new_tag.ChangeTypeId(selected_bottom_tag.Id)
            # for pipe in both_pipes:
            #     point = pipe_location(pipe, top)
            #     new_tag = db.IndependentTag.Create(doc, view.Id, db.Reference(pipe), False, db.TagMode.TM_ADDBY_CATEGORY, db.TagOrientation.Horizontal, point)
            #     new_tag.ChangeTypeId(selected_both_tag.Id)
            pass  # TODO
        except Exception as ex:
            print("Exception:\n {0}".format(ex))
            transaction.RollBack()
        else:
            transaction.Commit()
            print("Done.")
    else:  # type(view) != dbViewPlan
        print("Currently active view is not a plan view!")

# Helpers:

def get_points(pipe):
    """Get the start and end point of a pipe."""
    curve = pipe.Location.Curve
    start = curve.GetEndPoint(0)
    end = curve.GetEndPoint(1)
    return start, end

def get_high_low(first, second):
    """Get the high and the low point from two arbitrary points."""
    high = max(first.Z, second.Z)
    low = min(first.Z, second.Z)
    return high, low

def is_vertical(pipe, tolerance=1.0e-6):
    """Check if a pipe is vertical (within the given tolerance)."""
    start, end = get_points(pipe)
    dz = abs(start.Z - end.Z)
    if dz > tolerance:
        dx = abs(start.X - end.X)
        dy = abs(start.X - end.X)
        if dx < tolerance and dy < tolerance:
            return True
    return False

def top_and_bottom_elevation(doc, view):
    """Extract top and bottom elevation of a plan view."""
    view_range = view.GetViewRange()
    # get clip plane ids
    top_plane = view_range.GetLevelId(db.PlanViewPlane.TopClipPlane)
    bottom_plane = view_range.GetLevelId(db.PlanViewPlane.BottomClipPlane)
    # get clip plane levels
    top_level = doc.GetElement(top_plane)
    bottom_level = doc.GetElement(bottom_plane)
    # get clip plane offsets
    top_offset = view_range.GetOffset(db.PlanViewPlane.TopClipPlane)
    bottom_offset = view_range.GetOffset(db.PlanViewPlane.BottomClipPlane)
    # calculate clip plane elevations
    top_elevation = top_level.Elevation + top_offset
    bottom_elevation = bottom_level.Elevation + bottom_offset
    assert top_elevation >= bottom_elevation
    return top_elevation, bottom_elevation

def cuts_top_only(pipe, top, bottom):
    """Checks if the pipe only intersects the top elevation."""
    high, low = get_high_low(*get_points(pipe))
    if high >= top and top >= low >= bottom:
        return True
    return False

def cuts_bottom_only(pipe, top, bottom):
    """Checks if the pipe only intersects the botom elevation."""
    high, low = get_high_low(*get_points(pipe))
    if low <= bottom and bottom <= high <= top:
        return True
    return False

def cuts_top_and_bottom(pipe, top, bottom):
    """Checks if the pipe intersects both elevations."""
    high, low = get_high_low(*get_points(pipe))
    if high >= top and bottom >= low:
        return True
    return False

def pipe_location(pipe, elevation):
    """Returns the intersetion point of the pipe with the elevation."""
    # ! Assuming the pipe is vertical for now !
    curve = pipe.Location.Curve
    pipe_point = curve.GetEndPoint(0)
    point = db.XYZ(pipe_point.X, pipe_point.Y, elevation)
    return point


if __name__ == "__main__":
    # __window__.Hide()
    main()
    # __window__.Close()
