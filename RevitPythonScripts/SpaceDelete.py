import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db

#important vars, revit python shell version
app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
view = doc.ActiveView

print("Running Space Delete script for deleting Spaces...")
print("")

# Get all Spaces from the model
spaces = db.FilteredElementCollector(doc)\
           .OfCategory(db.BuiltInCategory.OST_MEPSpaces)\
           .ToElements()

print("Spaces:")
for space in spaces:
    print(space)
print("Total = {0} spaces".format(len(spaces)))
print("")

# Delete all Spaces from the model
transaction = db.Transaction(doc)
transaction.Start("SpaceDelete.py")
try:
    for space in spaces:
        print("deleting {0}...".format(space.Id))
        doc.Delete(space.Id)
except Exception as ex:
    print("Exception:\n {0}".format(ex))
    transaction.RollBack()
else:
    transaction.Commit()
    print("Done.")

#revit python shell has a console, access it like so
#__window__.Hide()
#__window__.Close()
