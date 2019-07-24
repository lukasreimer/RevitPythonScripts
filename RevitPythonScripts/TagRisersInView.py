"""Tag vertical risers in current view."""

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui


def main():
    """Main Script

    This script is tagging all vertical pipe risers in the current view.
    """
    print("Running TagRisersInView.py script...")

    # STEP 0: Setup
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # STEP 1: Get all vertical pipes in the view
    pipes = db.FilteredElementCollector(doc, view.Id)\
              .OfCategory(db.BuiltInCategory.OST_PipeCurves)\
              .ToElements()
    print("Found {num} pipes in the currently active view.".format(num=len(pipes)))
    # print(pipes)
    vertical_pipes = [pipe for pipe in pipes if is_vertical(pipe)]
    print("Found {num} vertical pipes in the view.".format(num=len(vertical_pipes)))
    # print(vertical_pipes)

    # STEP 2: Filter all pipes crossing upper and lower view range boundary
    top, bottom = top_and_bottom_elevation(doc, view)
    print("Top boundary elevation is {0} ft".format(top))
    print("Bottom boundary elevation is {0} ft".format(bottom))

    upper_pipes = [pipe for pipe in vertical_pipes if cuts_top_only(pipe, top, bottom)]
    lower_pipes = [pipe for pipe in vertical_pipes if cuts_bottom_only(pipe, top, bottom)]
    both_pipes =[pipe for pipe in vertical_pipes if cuts_top_and_bottom(pipe, top, bottom)]
    print("Found {num} pipes crossing upper boundary only.".format(num=len(upper_pipes)))
    # print(upper_pipes)
    print("Found {num} pipes crossing lower boundary only.".format(num=len(lower_pipes)))
    # print(lower_pipes)
    print("Found {num} pipes crossing both boundaries.".format(num=len(both_pipes)))
    # print(both_pipes)

    #TODO: extract list of valid pipe tag ids
    print("Querying pipe tags...")
    transaction = db.Transaction(doc)
    transaction.Start("TagRisersInView.py - Query pipe tags")
    try:
        some_pipe = pipes[0]
        some_tag = db.IndependentTag.Create(doc, view.Id, db.Reference(some_pipe), False, db.TagMode.TM_ADDBY_CATEGORY, db.TagOrientation.Horizontal, db.XYZ(0, 0, 0))
        valid_type_ids = some_tag.GetValidTypes()
        print(valid_type_ids)
        valid_types = [doc.GetElement(valid_type_id).FamilyName for valid_type_id in valid_type_ids]
        print(valid_types)
    except Exception as ex:
        print("Exception:\n {0}".format(ex))
        transaction.RollBack()
    else:
        transaction.Commit()
        print("Done.")


    #TODO: STEP 3: Place tags at the pipes
    print("Crating tags...")
    transaction = db.Transaction(doc)
    transaction.Start("TagRisersInView.py - Create pipe tags")
    try:
        for pipe in upper_pipes:
            point = pipe_location(pipe, top)
            new_tag = db.IndependentTag.Create(doc, view.Id, db.Reference(pipe), False, db.TagMode.TM_ADDBY_CATEGORY, db.TagOrientation.Horizontal, point)
            #print(new_tag)
            new_tag.ChangeTypeId(valid_type_ids[0])
    except Exception as ex:
        print("Exception:\n {0}".format(ex))
        transaction.RollBack()
    else:
        transaction.Commit()
        print("Done.")


# Helpers:
def is_vertical(pipe, tolerance=1.0e-6):
    """Check if a pipe is vertical."""
    curve = pipe.Location.Curve
    start = curve.GetEndPoint(0)
    end = curve.GetEndPoint(1)
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
    curve = pipe.Location.Curve
    start = curve.GetEndPoint(0)
    end = curve.GetEndPoint(1)
    high = max(start.Z, end.Z)
    low = min(start.Z, end.Z)
    if high >= top and top >= low >= bottom:
        return True
    return False


def cuts_bottom_only(pipe, top, bottom):
    """Checks if the pipe only intersects the botom elevation."""
    curve = pipe.Location.Curve
    start = curve.GetEndPoint(0)
    end = curve.GetEndPoint(1)
    high = max(start.Z, end.Z)
    low = min(start.Z, end.Z)
    if low <= bottom and bottom <= high <= top:
        return True
    return False


def cuts_top_and_bottom(pipe, top, bottom):
    """Checks if the pipe intersects both elevations."""
    curve = pipe.Location.Curve
    start = curve.GetEndPoint(0)
    end = curve.GetEndPoint(1)
    high = max(start.Z, end.Z)
    low = min(start.Z, end.Z)
    if high >= top and bottom >= low:
        return True
    return False


def pipe_location(pipe, elevation):
    """Returns the intersetion point of the pipe with the elevation."""
    curve = pipe.Location.Curve
    pipe_point = curve.GetEndPoint(0)
    point = db.XYZ(pipe_point.X, pipe_point.Y, elevation)
    print("pipe location = {}".format(point))
    return point


if __name__ == "__main__":
    main()
    # revit python shell console management
    # __window__.Hide()
    # __window__.Close()
