"""Color all pipe tags based on the color of the host's pipe system type.

This script colors pipe riser tags based on the system override color of the
tagged pipe.
"""

from __future__ import print_function
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui

__name = "ColorRiserTags.py"
__version = "0.2b"

# Constants
TAG_FAMILY_NAME = "BHE_DE_PipeTag_FlowArrow"


def main():
    """Main script."""

    print("🐍 Running {fname} version {ver}...".format(fname=__name, ver=__version))

    # STEP 0: Setup
    doc = __revit__.ActiveUIDocument.Document
    view = doc.ActiveView

    # STEP 1: Get all the tags in the view
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

    # STEP 3: Override tag color based on host system type color
    print("Recoloring all tags in the view based on host system color... ", end="")
    transaction = db.Transaction(doc)
    transaction.Start("{name} - v{ver}".format(name=__name, ver=__version))
    try:
        for riser_tag in riser_tags:
            host = riser_tag.GetTaggedLocalElement()
            system = host.MEPSystem
            if system:
                system_type = doc.GetElement(system.GetTypeId())
                color = system_type.LineColor
                override = db.OverrideGraphicSettings()
                view.SetElementOverrides(riser_tag.Id, override)  # reset to default
                override.SetProjectionLineColor(color)
                view.SetElementOverrides(riser_tag.Id, override)
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
    __result__ = main()
    if __result__ == ui.Result.Succeeded:
        __window__.Close()
