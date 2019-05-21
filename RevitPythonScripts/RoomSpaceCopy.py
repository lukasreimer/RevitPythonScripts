import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.DB import *

#important vars, revit python shell version
app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
view = doc.ActiveView

# Get all links in the revit model
# Select the link to copy rooms from
# Create Spaces for all rooms in the selected link
# Transfer data from the linked rooms to the Spaces


#revit python shell has a console, access it like so
#---------------------------------------------------
__window__.Hide()
__window__.Close()
