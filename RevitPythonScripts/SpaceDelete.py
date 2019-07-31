"""Delete all spaces in the model."""

import clr
clr.AddReference('RevitAPI')
import Autodesk.Revit.DB as db

__name = "SpaceDelete.py"
__version = "0.1a"

def main():
    """Main Program."""

    print("Running {fname} version {ver}...".format(fname=__name, ver=__version))
    
    # Important Revit variables
    doc = __revit__.ActiveUIDocument.Document

    # Get all Spaces from the model
    spaces = db.FilteredElementCollector(doc)\
            .OfCategory(db.BuiltInCategory.OST_MEPSpaces)\
            .ToElements()
    print("Found {0} spaces in the model.".format(len(spaces)))

    # Delete all Spaces from the model
    print("Deleting spaces...")
    transaction = db.Transaction(doc)
    transaction.Start("{name} - v{ver}".format(name=__name, ver=__version))
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
    #__window__.Hide()
    main()
    #__window__.Close()
