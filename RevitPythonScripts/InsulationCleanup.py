"""Cleanup unhosted and rogue pipe and duct insulation."""

import clr

clr.AddReference("RevitAPI")
import Autodesk.Revit.DB as db
import collections
import os


def main():
    """Main Script."""

    # Setup
    doc = __revit__.ActiveUIDocument.Document
    pipe_insulation_category = db.BuiltInCategory.OST_PipeInsulations
    duct_insulation_category = db.BuiltInCategory.OST_DuctInsulations
    clean_pipes = False
    clean_ducts = False
    report_file_name = "InsulationCleanup.txt"

    # Main Script
    print("HELLO!")
    print("Running InsulationCleanup.py script...")

    # STEP 1: Inspect Model
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

    # STEP 2: Receive User Input
    print("[0] Report, [1] Clean Pipe, [2] Clean Duct, [3] Clean Both")
    answer = raw_input("?> ").strip()
    if answer == "0":
        full_path = os.path.join(os.getcwd(), report_file_name)
        write_report(file_path=full_path,
                     unhosted_pipe=unhosted_pipe,
                     rogue_pipe=rogue_pipe,
                     unhosted_duct=unhosted_duct,
                     rogue_duct=rogue_duct)
    elif answer == "1":
        clean_pipes = True
    elif answer == "2":
        clean_ducts = True
    elif answer == "3":
        clean_pipes = True
        clean_ducts = True
    else:
        print("Nothing to do...")

    # STEP 3: Clean Up Insulation
    transaction = db.Transaction(doc)
    transaction.Start("InsulationCleanup.py")
    try:
        if clean_pipes:
            print("Cleaning Pipe Insulation...")
            for pipe_element in unhosted_pipe:
                doc.Delete(pipe_element.Id)
            for pipe_pair in rogue_pipe:
                cleanup_insulation(pipe_pair)
            print("Deleted {num} unhosted pipe insulation elements".format(
                num=len(unhosted_pipe)))
            print("Moved {num} rogue pipe insulation elements.".format(
                num=len(rogue_pipe)))
        if clean_ducts:
            print("Cleaning Duct Insulation...")
            for duct_element in unhosted_duct:
                doc.Delete(duct_element.Id)
            for duct_pair in rogue_duct:
                cleanup_insulation(duct_pair)
            print("Deleted {num} unhosted duct insulation elements.".format(
                num=len(unhosted_duct)))
            print("Moved {num} rogue duct insulation elements.".format(
                num=len(rogue_duct)))
    except Exception as exception:
        print("Failed.\nException:\n{ex}".format(ex=exception))
        transaction.RollBack()
    else:
        print("Done.")
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

def write_report(file_path, unhosted_pipe, rogue_pipe, unhosted_duct, rogue_duct):
    """Write report of unhosted and rogue insulation elements to a file."""
    print("writing report at {}".format(file_path))
    with open(file_path, mode="w") as file:
        file.write("Hello World!\n")
        # TODO: implement output time stamp
        # TODO: implement report creation


if __name__ == "__main__":
    main()
    # revit python shell console management
    raw_input("Hit any key to close.")
    __window__.Hide()
    __window__.Close()
