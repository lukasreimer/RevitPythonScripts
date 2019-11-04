"""Correct ventilation pipe riser tags.

This script checks through all pipe riser tags in the current view
and corrects them to ventilation style tags if the tagged pipes system
is a ventilation system.
"""

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui

__name = "CorrectVentTags.py"
__version = "0.1a"

mapping = {
    "NachOben": "LüftungNachOben",
    "VonUnten": "LüftungVonUnten",
    "Steigleitung": "LüftungSteigleitung",
}


def main():
    """Main script docstring."""
    
    print("Running {name} version {ver}".format(name=__name, ver=__version))

    # STEP 0: Setup
    doc = __revit__.ActiveUIDocument.Document
    view = doc.ActiveView

    # STEP 1: Get all the tags in the view
    tags = db.FilteredElementCollector(doc, view.Id)\
             .OfCategory(db.BuiltInCategory.OST_PipeTags)\
             .WhereElementIsNotElementType()\
             .ToElements()
    #print(tags)

    # STEP 2: 
    transaction = db.Transaction(doc)
    transaction.Start("{name} - v{ver}".format(name=__name, ver=__version))
    try:
        for tag in tags:
            host = tag.GetTaggedLocalElement()
            system = host.MEPSystem
            if system:
                system_type = doc.GetElement(system.GetTypeId())
                #print(type(system_type), system_type)
                system_classification = system_type.SystemClassification
                print(type(system_classification), system_classification)
                # TODO: find vent classified pipe tags and change tag type
                
    except Exception as ex:
        print(ex)
        transaction.RollBack()
        return ui.Result.Failed
    else:
        transaction.Commit()
        print("Done.")
        return ui.Result.Succeeded



if __name__ == "__main__":
    # __window__.Hide()
    main()
    # __window__.Close()
