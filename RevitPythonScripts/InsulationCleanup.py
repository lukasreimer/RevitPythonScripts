"""Cleanup unhosted and rogue pipe and duct insulation."""

import time
import clr

clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui
import collections


# TODO: Cleanup and console/dialog data output
def main():
    # important revit python shell variables
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # Setup:
    pipe_insulation_category = db.BuiltInCategory.OST_PipeInsulations
    duct_insulation_category = db.BuiltInCategory.OST_DuctInsulations

    # Main Script
    print("Running InsulationCleanup.py script...")
    # Inspect
    # select all pipe/duct insulation elements
    pipe_insulation_elements = query_all_elements(
        document=doc, category=pipe_insulation_category
    )
    duct_insulation_elements = query_all_elements(
        document=doc, category=duct_insulation_category
    )

    print_summary(pipe_insulation_elements, "Pipe Insulation Summary:")
    print_summary(duct_insulation_elements, "Duct Insulation Summary:")
    # print_all(pipe_insulation_elements, "Pipe Insulation Elements:")
    # print_all(duct_insulation_elements, "Duct Insulation Elements:")

    # Find all unhosted and rogue insulation elements
    rogue_pipe, unhosted_pipe = find_rogue_elements(
        document=doc, insulation_elements=pipe_insulation_elements
    )
    rogue_duct, unhosted_duct = find_rogue_elements(
        document=doc, insulation_elements=duct_insulation_elements
    )

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
    print("Cleaning Up Insulation...")
    transaction = db.Transaction(doc)
    transaction.Start("InsulationCleanup.py")
    try:
        # Delete all unhosted elements
        for element in unhosted_pipe:
            doc.Delete(element.Id)
        # Move all rogue elements to correct workset
        for pair in rogue_pipe:
            cleanup_insulation(pair)
        # raise RuntimeError("Just testing rolling back the transaction.")
    except Exception as ex:
        ui.TaskDialog.Show("Failed", "Exception:\n{}".format(ex))
        transaction.RollBack()
    else:
        text = """\
Deleted {num_unhosted_pipe} unhosted pipe insulation elements.
Moved {num_rogue_pipe} rogue pipe insulation elements.
---
Deleted {num_unhosted_duct} unhosted pipe insulation elements.
Moved {num_rogue_duct} rogue pipe insulation elements."""
        ui.TaskDialog.Show(
            "Done", text.format(
                num_unhosted_pipe=len(unhosted_pipe),
                num_rogue_pipe=len(rogue_pipe),
                num_unhosted_duct=len(unhosted_duct),
                num_rogue_duct=len(rogue_duct),
            ),
        )
        transaction.Commit()


# Functions:
ElementHostPair = collections.namedtuple("ElementHostPair", ["element", "host"])


def cleanup_insulation(pair):
    """Cleanup rogue insulation elements."""
    # https://thebuildingcoder.typepad.com/blog/2013/01/change-element-workset.html
    element_workset_id = pair.element.WorksetId.IntegerValue
    host_workset_id = pair.host.WorksetId.IntegerValue
    # print("{elem_id}, {host_id}".format(elem_id=element_workset_id, host_id=host_workset_id))
    # get the host workset parameter for setting its value
    host_workset_parameter = pair.host.get_Parameter(
        db.BuiltInParameter.ELEM_PARTITION_PARAM
    )
    # move host to insulation WorksetId
    host_workset_parameter.Set(element_workset_id)
    # move host to previous host workset (and carry over the insulation)
    host_workset_parameter.Set(host_workset_id)


def find_rogue_elements(document, insulation_elements):
    """Find all unhosted or rogue insulation elements."""
    unhosted_elements = []
    rogue_elements = []
    for element in insulation_elements:
        host_id = element.HostElementId
        host_element = document.GetElement(host_id)
        if host_element is None:
            unhosted_elements.append(element)
        else:
            if element.WorksetId != host_element.WorksetId:
                rogue_elements.append(ElementHostPair(element, host_element))
        # print("{id}: {element}".format(id=host_id, element=host_element))
    return rogue_elements, unhosted_elements


def query_all_elements(document, category):
    """Return all elements of a category from a document."""
    filter = db.ElementCategoryFilter(category)
    collector = db.FilteredElementCollector(document)
    elements = collector.WherePasses(filter).WhereElementIsNotElementType().ToElements()
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


if __name__ == "__main__":
    start = time.clock()
    main()
    runtime = time.clock() - start
    print("Runtime = {0} seconds".format(runtime))

    # revit python shell console management
    # __window__.Hide()
    # __window__.Close()
