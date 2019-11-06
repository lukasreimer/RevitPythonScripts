"""Correct ventilation pipe riser tags.

This script checks through all pipe riser tags in the current view
and corrects them to ventilation style tags if the tagged pipes system
is a ventilation system.
"""

from __future__ import print_function
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui

__name = "CorrectVentTags.py"
__version = "0.1b"

# Constants
TAG_FAMILY_NAME = "BHE_DE_PipeTag_FlowArrow"
TAG_TYPE_NAME_MAPPING = {  # hard coded tag names to use
    "Steigleitung": TAG_FAMILY_NAME + " - Steigleitung",
    "Fallleitung": TAG_FAMILY_NAME + " - Fallleitung",
    "VonOben": TAG_FAMILY_NAME + " - VonOben",
    "NachOben": TAG_FAMILY_NAME + " - NachOben",
    "VonUnten": TAG_FAMILY_NAME + " - VonUnten",
    "NachUnten": TAG_FAMILY_NAME + " - NachUnten",
    "LüftungNachOben": TAG_FAMILY_NAME + " - LüftungNachOben",
    "LüftungVonUnten": TAG_FAMILY_NAME + " - LüftungVonUnten",
    "LüftungSteigleitung": TAG_FAMILY_NAME + " - LüftungSteigleitung",
}
REMAPPING = {
    "NachOben": "LüftungNachOben",
    "VonOben": "LüftungNachOben",
    "NachUnten": "LüftungVonUnten",
    "VonUnten": "LüftungVonUnten",
    "Steigleitung": "LüftungSteigleitung",
    "Fallleitung": "LüftungSteigleitung",
}


def main():
    """Main script - Correct the pipe riser tags tagging vent pipes."""
    
    print("🐍 Running {name} version {ver}:".format(name=__name, ver=__version))

    # STEP 0: Setup
    doc = __revit__.ActiveUIDocument.Document
    view = doc.ActiveView

    # STEP 1: Get all available Pipe Tags in the project
    print("Getting all available pipe tags from the model... ", end="")
    tag_types = db.FilteredElementCollector(doc)\
                  .OfCategory(db.BuiltInCategory.OST_PipeTags)\
                  .WhereElementIsElementType()\
                  .ToElements()
    tag_types_mapping = {}  # tag_title: tag_type
    for tag_type in tag_types:
        tag_family_name = tag_type.get_Parameter(db.BuiltInParameter.SYMBOL_FAMILY_NAME_PARAM).AsString()
        tag_type_name = tag_type.get_Parameter(db.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        full_tag_name = "{f_name} - {t_name}".format(f_name=tag_family_name, t_name=tag_type_name)
        tag_types_mapping[full_tag_name] = tag_type
    print("✔")

    # STEP 2: Check if setup tags actually exist in project
    print("Checking if expected tag family (and types) exist(s)... ", end="")
    all_tags_available = True
    for tag_name in TAG_TYPE_NAME_MAPPING.values():
        if not tag_name in tag_types_mapping:
            print("✘ Error: {tag_name} not available!".format(tag_name=tag_name))
            all_tags_available = False
    if not all_tags_available:
        print("✘ Error: Not all required tags are available in the project! See above.")
        return ui.Result.Failed
    print("✔")

    # STEP 3: Get all the tags in the view
    tags_in_view = db.FilteredElementCollector(doc, view.Id)\
                     .OfCategory(db.BuiltInCategory.OST_PipeTags)\
                     .WhereElementIsNotElementType()\
                     .ToElements()

    # STEP 4: Change all tags on vent pipes to vent tags
    # TODO: test running the script on a finished drawing!
    print("Changing all pipe riser tags tagging vent pipes.... ", end="")
    transaction = db.Transaction(doc)
    transaction.Start("{name} - v{ver}".format(name=__name, ver=__version))
    try:
        for tag in tags_in_view:
            host = tag.GetTaggedLocalElement()
            system = host.MEPSystem
            if system:
                system_type = doc.GetElement(system.GetTypeId())
                system_classification = system_type.SystemClassification
                if system_classification == db.MEPSystemClassification.Vent:
                    tag_type = doc.GetElement(tag.GetTypeId())
                    tag_family_name = tag_type.get_Parameter(db.BuiltInParameter.SYMBOL_FAMILY_NAME_PARAM).AsString()
                    tag_type_name = tag_type.get_Parameter(db.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
                    if not tag_family_name == TAG_FAMILY_NAME:  # other kind of tag, dont bother
                        continue
                    if tag_type_name not in REMAPPING:  # tag type already good or not in remapping
                        continue
                    target = REMAPPING[tag_type_name]
                    target_type_id = tag_types_mapping[TAG_TYPE_NAME_MAPPING[target]].Id
                    tag.ChangeTypeId(target_type_id)
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
    #__window__.Close()
