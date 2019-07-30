"""Transfer parameter data from linked rooms to spaces."""

import clr
clr.AddReference('RevitAPI') 
clr.AddReference('RevitAPIUI') 
import Autodesk.Revit.DB as db

__name = "RoomSpaceTransfer.py"
__version = "0.1a"

def main():
    """Main Script."""

    print("Running {fname} version {ver}...".format(fname=__name, ver=__version))

    # important revit python shell variables
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # TODO: select all spaces in the model

    # TODO: select linked rooms for the spaces

    # TODO: transfer parameter data from rooms to spaces
    


if __name__ == "__main__":
    # __window__.Hide()
    main()
    # __window__.Close()
