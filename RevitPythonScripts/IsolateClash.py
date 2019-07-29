"""Isolate Clash in View Script.

This script isolates a clash in the current 3D view.
"""
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui

__name = "IsolateClash.py"
__version = "0.1a"

ID_A = 1624025
ID_B = 9302445
THRESHOLD = 10  # ft


def main():
    """Main Function."""
    print("Running {fname} version {ver}...".format(fname=__name, ver=__version))

    # STEP 0: Setup
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # STEP 1: Get the clashing elements (ids)
    elem_id_a = db.ElementId(ID_A)
    elem_a = doc.GetElement(elem_id_a)
    print(elem_a)
    elem_id_b = db.ElementId(ID_B)
    elem_b = doc.GetElement(elem_id_b)
    print(elem_b)

    ogs = db.OverrideGraphicSettings()
    ogs.SetProjectionLineColor(db.Color(255, 0, 0))
    ogs.SetProjectionLineWeight(7)
    ogs.SetProjectionFillColor(db.Color(255, 0, 0))
    ogs.SetProjectionFillPatternId(db.ElementId(19))

    # STEP 2: Create an outline around the clash
    bbox_a = elem_a.get_BoundingBox(view)
    print(bbox_a)
    min_a = bbox_a.Min
    max_a = bbox_a.Max
    bbox_b = elem_b.get_BoundingBox(view)
    print(bbox_b)
    min_b = bbox_b.Min
    max_b = bbox_b.Max

    outline_offset = db.XYZ(THRESHOLD, THRESHOLD, THRESHOLD)
    min_o = min(min_a, min_b) - outline_offset
    max_o = max(max_a, max_b) + outline_offset

    outline = db.Outline(min_o, max_o)

    # STEP 3: Select all Elements interseting the outline
    filter = db.BoundingBoxIntersectsFilter(outline)
    selection = db.FilteredElementCollector(doc).WherePasses(filter).ToElementIds()

    ogs_half = db.OverrideGraphicSettings()
    ogs_half.SetProjectionLineColor(db.Color(192, 192, 192))
    ogs_half.SetProjectionFillColor(db.Color(192, 192, 192))
    ogs_half.SetProjectionFillPatternId(db.ElementId(19))
    ogs_half.SetSurfaceTransparency(50)


    # STEP 4: Isolate elements in current view
    transaction = db.Transaction(doc)
    transaction.Start("IsolateClash.py")
    try:
        view.IsolateElementsTemporary(selection)
        for elem_id in selection:
            view.SetElementOverrides(elem_id, ogs_half)
        view.SetElementOverrides(elem_id_a, ogs)
        view.SetElementOverrides(elem_id_b, ogs)
    except Exception as ex:
        print("Exception: {0}".format(ex))
        transaction.RollBack()
    else:
        transaction.Commit()
        print("Done.")
    


if __name__ == "__main__":
    # __window__.Hide()
    main()
    # __window__.Close()
