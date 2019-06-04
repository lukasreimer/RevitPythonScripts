"""Transfer Parameter Data from linked Rooms to Spaces."""

import time
import clr
clr.AddReference('RevitAPI') 
clr.AddReference('RevitAPIUI') 
import Autodesk.Revit.DB as db


def main():
    """Main Script."""

    # important revit python shell variables
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    print("Transferring Parameter Data from Rooms to Spaces...")

    # TODO: select all spaces in the model

    # TODO: select linked rooms for the spaces

    # TODO: transfer parameter data from rooms to spaces
    


if __name__ == "__main__":
    start = time.clock()
    main()
    runtime = time.clock() - start
    print("Runtime = {0} seconds".format(runtime))

    # revit python shell console management
    # __window__.Hide()
    # __window__.Close()
