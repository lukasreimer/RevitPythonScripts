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

    # important revit python shell variables
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # main script
    #TODO: get all vertical pipes in the view
    pipes = db.FilteredElementCollector(doc, view.Id)\
              .OfCategory(db.BuiltInCategory.OST_PipeCurves)\
              .ToElements()
    print(len(pipes), pipes)
    vertical_pipes = [pipe for pipe in pipes if is_vertical(pipe)]
    print(len(vertical_pipes), vertical_pipes)

    #TODO: filter all pipe crossing upper and lower view range boundary
    top, bottom = top_and_bottom_elevation(doc, view)
    print(top, bottom)

    upper_pipes = []
    lower_pipes = []
    both_pipes =[]

    #TODO: place tags at the pipes
    # doc.NewTag(
    #     View view,
    #     Element elem,
    #     Bool leader?,
    #     TagMode mode,
    #     TagOrientation orientation,
    #     XYZpoint
    # )


# Helpers:
def is_vertical(pipe, tolerance=1.0e-6):
    """Check if a pipe is vertical."""
    curve = pipe.Location.Curve
    start, end = curve.GetEndPoint(0), curve.GetEndPoint(1)
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
    return top_elevation, bottom_elevation


def cuts_top_only(pipe, top, bottom):
    """."""
    pass


def cuts_bottom_only(pipe, top, bottom):
    """."""
    pass


def cuts_top_and_bottom(pipe, top, bottom):
    """."""
    pass


if __name__ == "__main__":
    main()
    # revit python shell console management
    # __window__.Hide()
    # __window__.Close()
