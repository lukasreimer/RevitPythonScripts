"""Cleanup unhosted and rogue pipe and duct insulation."""

import time
import clr

clr.AddReference("RevitAPI")
# clr.AddReference("RevitAPIUI")
import Autodesk.Revit.DB as db
# import Autodesk.Revit.UI as ui
import collections


def main():
    """Main Script."""

    # Setup
    doc = __revit__.ActiveUIDocument.Document

    pipe_insulation_category = db.BuiltInCategory.OST_PipeInsulations
    duct_insulation_category = db.BuiltInCategory.OST_DuctInsulations

    # Main Script
    print("Running InsulationCleanup.py script...")
    # Inspect
    pipe_insulation_elements = query_all_elements(
        document=doc, category=pipe_insulation_category)
    duct_insulation_elements = query_all_elements(
        document=doc, category=duct_insulation_category)

    print_summary(pipe_insulation_elements, "Pipe Insulation Elements:")
    # print_all(pipe_insulation_elements, indent=2)
    print_summary(duct_insulation_elements, "Duct Insulation Elements:")
    # print_all(duct_insulation_elements, indent=2)

    rogue_pipe, unhosted_pipe = find_rogue_elements(
        document=doc, insulation_elements=pipe_insulation_elements)
    rogue_duct, unhosted_duct = find_rogue_elements(
        document=doc, insulation_elements=duct_insulation_elements)

    print_summary(unhosted_pipe, "Unhosted Pipe Insulation Summary:")
    # print_all(unhosted_pipe, indent=2)
    print_summary(rogue_pipe, "Rogue Pipe Insulation Summary:")
    # print_all(rogue_pipe, indent=2)
    print_summary(unhosted_duct, "Unhosted Duct Insulation Summary:")
    # print_all(unhosted_duct, indent=2)
    print_summary(rogue_duct, "Rogue Duct Insulation Summary:")
    #print_all(rogue_duct, indent=2)

    print("[1] - Cleanup Pipe Insulation")
    print("[2] - Cleanup Duct Insulation")
    print("[3] - Cleanup Both Pipe and Duct Insulation")
    print("[4] - Write Report")
    answer = input("Continue?")
    print("You said: '{}'".format(answer))

    # Change
    print("Cleaning Up Insulation...")
    transaction = db.Transaction(doc)
    transaction.Start("InsulationCleanup.py")
    try:
        # PIPE
        # Delete all unhosted pipe insulation elements
        for pipe_element in unhosted_pipe:
            doc.Delete(pipe_element.Id)
        # Move all rogue pipe insulation elements to correct workset
        for pipe_pair in rogue_pipe:
            cleanup_insulation(pipe_pair)
        # DUCT
        # Delete all unhosted pipe insulation elements
        for duct_element in unhosted_duct:
            doc.Delete(duct_element.Id)
        # Move all rogue pipe insulation elements to correct workset
        for duct_pair in rogue_duct:
            cleanup_insulation(duct_pair)
    except Exception as exception:
        # ui.TaskDialog.Show("Failed", "Exception:\n{}".format(ex))
        print("Failed.\nException:\n{ex}".format(ex=exception))
        transaction.RollBack()
    else:
        print("Done.")
        print("Deleted {num} unhosted pipe insulation elements".format(num=len(unhosted_pipe)))
        print("Moved {num} rogue pipe insulation elements.".format(num=len(rogue_pipe)))
        print("Deleted {num} unhosted duct insulation elements.".format(num=len(unhosted_duct)))
        print("Moved {num} rogue duct insulation elements.".format(num=len(rogue_duct)))
        transaction.Commit()


# Helpers:
ElementHostPair = collections.namedtuple("ElementHostPair", ["element", "host"])


def cleanup_insulation(pair):
    """Cleanup rogue insulation elements."""
    element_workset_id = pair.element.WorksetId.IntegerValue
    host_workset_id = pair.host.WorksetId.IntegerValue
    # get the host workset parameter for setting its value back and forth
    host_workset_parameter = pair.host.get_Parameter(
        db.BuiltInParameter.ELEM_PARTITION_PARAM)
    host_workset_parameter.Set(element_workset_id)
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
    return rogue_elements, unhosted_elements


def query_all_elements(document, category):
    """Return all elements of a category from a document."""
    filter = db.ElementCategoryFilter(category)
    collector = db.FilteredElementCollector(document)
    elements = collector.WherePasses(filter)\
                        .WhereElementIsNotElementType()\
                        .ToElements()
    # pythonic_elements = [element for element in elements]
    return elements


def print_summary(element_list, caption=""):
    """Print a summary of the given list."""
    length = element_list.Count
    print("{caption} {length}".format(caption=caption, length=length))


def print_all(element_list, caption=None, indent=0):
    """Print all elements from the given list."""
    total = element_list.Count
    if caption:
        print(caption)
    for index, element in enumerate(element_list):
        print("{indent}[{index}/{total}]: {element}".format(
            indent=indent*" ",
            index=index,
            total=total,
            element=element))


if __name__ == "__main__":
    start = time.clock()
    main()
    runtime = time.clock() - start
    print("Runtime = {0} seconds".format(runtime))
    # revit python shell console management
    # __window__.Hide()
    # __window__.Close()
