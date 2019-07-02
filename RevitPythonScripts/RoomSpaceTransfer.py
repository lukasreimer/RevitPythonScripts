"""Transfer Parameter Data from linked Rooms to Spaces."""

import clr
clr.AddReference('RevitAPI') 
clr.AddReference('RevitAPIUI') 
import Autodesk.Revit.DB as db


def main():
    """Main Script."""

    print("Transferring Parameter Data from Rooms to Spaces...")

    # important revit python shell variables
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # TODO: select all spaces in the model

    # TODO: select linked rooms for the spaces

    # TODO: transfer parameter data from rooms to spaces
    


if __name__ == "__main__":
    main()
    # revit python shell console management
    # __window__.Hide()
    # __window__.Close()
