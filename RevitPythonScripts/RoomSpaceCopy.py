"""Create Spaces from linked Rooms."""

import time
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db


def main():
    """Main Script."""

    #important vars, revit python shell version
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    print("Running RoomSpaceCopy script for copying linked Rooms to Spaces...")

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

    # Select the link to copy rooms from
    link = linked_docs[0]
    print("Selected Link: {}".format(link.Title))

    # Get all Rooms from the selected link
    rooms = db.FilteredElementCollector(link)\
            .OfCategory(db.BuiltInCategory.OST_Rooms)\
            .ToElements()

    print("Linked Rooms:")
    for room in rooms:
        print(room)
    print("Total = {0} rooms".format(len(rooms)))

    # Get linked Levels:
    linked_levels = db.FilteredElementCollector(link)\
                    .OfCategory(db.BuiltInCategory.OST_Levels)\
                    .WhereElementIsNotElementType()\
                    .ToElements()

    print("Linked Levels:")
    for level in linked_levels:
        print(level, level.Name, level.Elevation)
    print("Total = {0} linked levels".format(len(linked_levels)))

    # Get Levels:
    levels = db.FilteredElementCollector(doc)\
            .OfCategory(db.BuiltInCategory.OST_Levels)\
            .WhereElementIsNotElementType()\
            .ToElements()

    print("Levels:")
    for level in levels:
        print(level, level.Name, level.Elevation, level.IsMonitoringLinkElement())
    print("Total = {0} levels".format(len(levels)))

    # TODO: Create Mapping of Levels and Linked Levels by minimal distance
    transaction = db.Transaction(doc)
    transaction.Start("RoomSpaceCopy.py")
    try:
        pass
        # Create Spaces for all rooms in the selected link
        for room in rooms:
            room_level = room.Level
            space_level = room_level  # TODO: find correct level from mapping
            location_point = room.Location.Point
            insert_point = db.UV(location_point.X, location_point.Y)
            # print(level, location, point)
            # print("creating space: ")
            # created_space = doc.Create.NewSpace(space_level, insert_point)
            # print("created space: {0}".format(created_space))
        # Transfer data from the linked rooms to the Spaces

    except Exception as ex:
        print(ex)
        transaction.RollBack()
    else:
        transaction.Commit()
        print("Done.")


if __name__ == "__main__":
     start = time.clock()
    main()
    runtime = time.clock() - start
    print("Runtime = {0} seconds".format(runtime))

    #revit python shell has a console, access it like so
    #__window__.Hide()
    #__window__.Close()
