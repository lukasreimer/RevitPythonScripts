import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db

#important vars, revit python shell version
app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
view = doc.ActiveView

print("Running RoomSpaceCopy script for copying linked Rooms to Spaces...")
print("")

# Get all links in the revit model
linked_docs = []
for document in app.Documents:
    if document.IsLinked:
        linked_docs.append(document)

print("Linked Documents:")
print(linked_docs)
for item in linked_docs:
    print(item)
    print("{0}: {1}".format(item.Title, item.PathName))
print("")

# Select the link to copy rooms from
link = linked_docs[0]
print("Selected Link: {}".format(link.Title))
print("")

# Get all Rooms from the selected link
rooms = db.FilteredElementCollector(link)\
          .OfCategory(db.BuiltInCategory.OST_Rooms)\
          .ToElements()

print("Linked Rooms:")
for room in rooms:
    print(room)
print("Total = {0} rooms".format(len(rooms)))
print("")

# Create Spaces for all rooms in the selected link
# Transfer data from the linked rooms to the Spaces

print("Done.")

#revit python shell has a console, access it like so
#__window__.Hide()
#__window__.Close()
