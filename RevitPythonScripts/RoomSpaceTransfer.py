"""Transfer parameter data from associated rooms to spaces."""

from __future__ import print_function
import clr
clr.AddReference('RevitAPI') 
clr.AddReference('RevitAPIUI') 
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui

__name = "RoomSpaceTransfer.py"
__version = "0.1a"

def main():
    """Main Script."""

    print("🐍 Running {name} version {ver}".format(name=__name, ver=__version))

    # important revit python shell variables
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # Select all spaces in the model
    print("Getting all spaces from the model...", end="")
    all_spaces = db.FilteredElementCollector(doc).OfCategory(db.BuiltInCategory.OST_MEPSpaces).ToElements()
    print("✔")
    print("  ➜ Found {num} spaces in the project.".format(num=len(all_spaces)))
    #print(all_schedules)

    # TODO: select linked rooms for the spaces
    print("Getting all space and room numbers and names...", end="")
    output = []
    for space in all_spaces:
        space_number_param = space.get_Parameter(db.BuiltInParameter.ROOM_NUMBER)
        space_name_param = space.get_Parameter(db.BuiltInParameter.ROOM_NAME)
        room_number_param = space.get_Parameter(db.BuiltInParameter.SPACE_ASSOC_ROOM_NUMBER)
        room_name_param = space.get_Parameter(db.BuiltInParameter.SPACE_ASSOC_ROOM_NAME)
        output.append((
            space_number_param.AsString(),
            space_name_param.AsString(),
            room_number_param.AsString(),
            room_name_param.AsString()
        ))
    print("✔")
    for item in output:
        print(item)

    # TODO: transfer parameter data from rooms to spaces
    print("Transfering parameters from room to space...", end="")
    
    print("✔\nDone. 😊")
    return ui.Result.Succeeded


if __name__ == "__main__":
    #__window__.Hide()
    result = main()
    # if result == ui.Result.Succeeded:
    #     __window__.Close()
