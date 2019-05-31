import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui
import collections
import sys

__version__ = "0.1"

# TODO: Cleanup and console/dialog data output

# important variables, revit python shell version
app = __revit__.Application
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
view = doc.ActiveView

# Setup:
pipe_insulation_category = db.BuiltInCategory.OST_PipeInsulations
duct_insulation_category = db.BuiltInCategory.OST_DuctInsulations


# Functions:
def query_all_elements(document, category):
    """Return all elements of a category from a document."""
    filter = db.ElementCategoryFilter(category)
    collector = db.FilteredElementCollector(document)
    elements = collector.WherePasses(filter)\
                        .WhereElementIsNotElementType()\
                        .ToElements()
    # pythonic_elements = [element for element in elements]
    return elements

def print_summary(element_list, caption=None):
    """Print a summary of the given list."""
    length = element_list.Count
    if caption:
        print(caption)
    print("Found {0} elements.".format(length))


def print_all(element_list, caption=None):
    """Print all elements from the given list."""
    # print(type(element_list))
    # print(element_list)
    length = element_list.Count
    if caption:
        print(caption)
    for index, element in enumerate(element_list):
        print("{0}/{1}: {2}".format(index, length, element))


# Main Script
print("Running InsulationCleanup python script v{0} ...".format(__version__))
# Inspect
# select all pipe/duct insulation elements
pipe_insulation_elements = query_all_elements(document=doc, category=pipe_insulation_category)
duct_insulation_elements = query_all_elements(document=doc, category=duct_insulation_category)

print_summary(pipe_insulation_elements, "Pipe Insulation Summary:")
print_summary(duct_insulation_elements, "Duct Insulation Summary:")
# print_all(pipe_insulation_elements, "Pipe Insulation Elements:")
# print_all(duct_insulation_elements, "Duct Insulation Elements:")

sys.exit()

# compute all unhosted/rogue insulation elements
ElementHostPair = collections.namedtuple("ElementHostPair", ["element", "host"])
unhosted_elements = []
rogue_elements = []
for element in insulation_elements:
    host_id = element.HostElementId
    host_element = doc.GetElement(host_id)
    if host_element is None:
        unhosted_elements.append(element)
    else:
        if element.WorksetId != host_element.WorksetId:
            rogue_elements.append(ElementHostPair(element, host_element))
    # print("{id}: {element}".format(id=host_id, element=host_element))

# show a report of all unhosted/rogue elements
# print("{} Unhosted Elements:".format(len(unhosted_elements)))
# for element in unhosted_elements:
#     print(element)

# print("{} Rogue Elements:".format(len(rogue_elements)))
# for pair in rogue_elements:
#     print("{element}: {host}".format(element=pair.element, host=pair.host))

# worksets = FilteredWorksetCollector(doc).OfKind(WorksetKind.UserWorkset)\
#                                         .ToWorksets()
# print("Worksets:")
# for workset in worksets:
#     print("{id}: {name}".format(id=workset.Id.IntegerValue, name=workset.Name))

# Change
transaction = db.Transaction(doc)
transaction.Start("InsulationCleanup.py")
try:
    # Delete all unhosted elements
    for element in unhosted_elements:
        doc.Delete(element.Id)
    # Move all rogue elements to correct workset
    for pair in rogue_elements:
        # https://thebuildingcoder.typepad.com/blog/2013/01/change-element-workset.html
        element_workset_id = pair.element.WorksetId.IntegerValue
        host_workset_id = pair.host.WorksetId.IntegerValue
        print("{elem_id}, {host_id}".format(elem_id=element_workset_id, host_id=host_workset_id))

        # get the host workset parameter for setting its value
        host_workset_parameter = pair.host.get_Parameter(db.BuiltInParameter.ELEM_PARTITION_PARAM)
        # move host to insulation WorksetId
        host_workset_parameter.Set(element_workset_id)
        # move host to previous host workset (and carry over the insulation)
        host_workset_parameter.Set(host_workset_id)

    # raise RuntimeError("Just testing rolling back the transaction.")
except Exception as ex:
    ui.TaskDialog.Show("Failed", "Exception:\n{}".format(ex))
    transaction.RollBack()
else:
    ui.TaskDialog.Show("Done", "Deleted {num_unhosted} unhosted insulation elements.\nMoved {num_rogue} rogue insulation elements".format(num_unhosted=len(unhosted_elements), num_rogue=len(rogue_elements)))
    transaction.Commit()

#__window__.Hide()
__window__.Close()
