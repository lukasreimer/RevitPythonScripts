"""Clear all BHE_DE pipe riser tags in the current view."""

from __future__ import print_function
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui

__name = "ClearPipeRiserTagsInView.py"
__version = "0.2b"

# Constants
TAG_FAMILY_NAME = "BHE_DE_PipeTag_FlowArrow"


def main():
    """Main script docstring."""
    
    print("🐍 Running {name} version {ver}".format(name=__name, ver=__version))

    # STEP 0: Setup
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # STEP 1: Get all pipe tags in the view
    print("Getting all pipe tags from the view... ", end="")
    tags = db.FilteredElementCollector(doc, view.Id)\
             .OfCategory(db.BuiltInCategory.OST_PipeTags)\
             .WhereElementIsNotElementType()\
             .ToElements()
    print("✔")
    print("  ➜ Found {num} tags in the current view.".format(num=len(tags)))

    # STEP 2: Filter for BHE_DE pipe riser tags
    print("Filtering for pipe riser tags... ", end="")
    riser_tags = []
    for tag in tags:
        tag_type = doc.GetElement(tag.GetTypeId())
        tag_family_name = tag_type.get_Parameter(db.BuiltInParameter.SYMBOL_FAMILY_NAME_PARAM).AsString()
        if tag_family_name == TAG_FAMILY_NAME:
            riser_tags.append(tag)
    print("✔")
    print("  ➜ Found {num} pipe riser tags in the current view.".format(num=len(riser_tags)))

    # STEP 3: Delete all BHE_DE pipe riser tags
    if len(riser_tags) == 0:
        print("Nothing to do. 😑")
        return ui.Result.Cancelled
    print("Deleting all pipe riser tags from the view...", end="")
    transaction = db.Transaction(doc)
    transaction.Start("{name} - v{ver}".format(name=__name, ver=__version))
    try:
        for riser_tag in riser_tags:
            doc.Delete(riser_tag.Id)
    except Exception as ex:
        print("\n✘ Exception:\n {ex}".format(ex=ex))
        transaction.RollBack()
        return ui.Result.Failed
    else:
        transaction.Commit()
        print("✔\nDone. 😊")
        return ui.Result.Succeeded


if __name__ == "__main__":
    #__window__.Hide()
    result = main()
    if result == ui.Result.Succeeded:
        __window__.Close()
