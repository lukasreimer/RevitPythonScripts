"""Delete all spaces in the model."""

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db


def main():
    """Main Program."""

    print("Running Space Delete script for deleting Spaces...")
    
    # Important Revit variables
    doc = __revit__.ActiveUIDocument.Document

    # Get all Spaces from the model
    spaces = db.FilteredElementCollector(doc)\
            .OfCategory(db.BuiltInCategory.OST_MEPSpaces)\
            .ToElements()
    print("Found {0} spaces in the model".format(len(spaces)))

    # Delete all Spaces from the model
    print("Deleting spaces...")
    transaction = db.Transaction(doc)
    transaction.Start("SpaceDelete.py")
    try:
        for space in spaces:
            # print("deleting {0}...".format(space.Id))
            doc.Delete(space.Id)
    except Exception as ex:
        print("Exception:\n {0}".format(ex))
        transaction.RollBack()
    else:
        transaction.Commit()
        print("Done.")


if __name__ == "__main__":
    main()
    #revit python shell has a console, access it like so
    #__window__.Hide()
    #__window__.Close()
