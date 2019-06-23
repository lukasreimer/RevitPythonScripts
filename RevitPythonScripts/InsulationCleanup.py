"""Cleanup unhosted and rogue pipe and duct insulation."""

import collections
import os
import clr

clr.AddReference("RevitAPI")
import Autodesk.Revit.DB as db

clr.AddRefrence("RevitAPIUI")
import Autodesk.Revit.UI as ui


def main():
    """Main Script."""

    # Setup
    doc = __revit__.ActiveUIDocument.Document
    pipe_ins_cat = db.BuiltInCategory.OST_PipeInsulations
    duct_ins_cat = db.BuiltInCategory.OST_DuctInsulations
    clean_pipe = False
    clean_duct = False
    report_file_name = "InsulationCleanup.txt"

    # Main Script
    print("Running InsulationCleanup.py script...")

    # STEP 1: Inspect Model
    pipe_ins_elems = query_all_elements(doc=doc, cat=pipe_ins_cat)
    duct_ins_elems = query_all_elements(doc=doc, cat=duct_ins_cat)

    print_summary(pipe_ins_elems, "Pipe Insulation Elements:")
    # print_all(pipe_insulation_elements, indent=2)
    print_summary(duct_ins_elems, "Duct Insulation Elements:")
    # print_all(duct_insulation_elements, indent=2)

    rogue_pipe, unhosted_pipe = find_rogue_elements(doc=doc, elems=pipe_ins_elems)
    rogue_duct, unhosted_duct = find_rogue_elements(doc=doc, elems=duct_ins_elems)

    print_summary(unhosted_pipe, "Unhosted Pipe Insulation Summary:")
    # print_all(unhosted_pipe, indent=2)
    print_summary(rogue_pipe, "Rogue Pipe Insulation Summary:")
    # print_all(rogue_pipe, indent=2)
    print_summary(unhosted_duct, "Unhosted Duct Insulation Summary:")
    # print_all(unhosted_duct, indent=2)
    print_summary(rogue_duct, "Rogue Duct Insulation Summary:")
    #print_all(rogue_duct, indent=2)

    # STEP 2: Receive User Input
    dialog = ui.TaskDialog(title="Insulation Cleanup")
    dialog.MainInstruction = "Insulation Cleanup"
    dialog.MainContent = "Insulation Cleanup Report"
    dialog.FooterText = "<a href=\"http://www.google.de\">Click here for more information</a>"
    dialog.AddCommandLink(ui.TaskDialogCommandLinkId.CommandLink1, "Write Report")
    dialog.AddCommandLink(ui.TaskDialogCommandLinkId.CommandLink2, "Clean Pipe Insulation")
    dialog.AddCommandLink(ui.TaskDialogCommandLinkId.CommandLink3, "Clean Duct Insulation")
    dialog.AddCommandLink(ui.TaskDialogCommandLinkId.CommandLink4, "Clean Pipe & Duct Insulation")
    result = dialog.Show()

    if result == ui.TaskDialogResult.CommandLink1:
        print("Write Report")
        save_dialog = ui.FileSaveDialog(filter="All files|*.*")
        save_dialog.Title = "Save Insulation Cleanup Report"
        save_dialog.InitialFileName = "report.txt"
        save_result = save_dialog.Show()
        report_path = save_dialog.GetSelectedModelPath()
        print(save_result, report_path)
        # TODO: actually save repor file
    elif result == ui.TaskDialogResult.CommandLink2:
        print("Clean Pipe Insulation")
        clean_pipe = True
    elif result == ui.TaskDialogResult.CommandLink3:
        print("Clean Duct Insulation")
        clean_duct = True
    elif result == ui.TaskDialogResult.CommandLink4:
        print("Clean Pipe & Duct Insulation")
        clean_pipe = True
        clean_duct = True
    else:
        print("Nothing to do...")
    
    # STEP 3: Clean Up Insulation
    transaction = db.Transaction(doc)
    transaction.Start("InsulationCleanup.py")
    try:
        if clean_pipe:
            print("Cleaning Pipe Insulation...")
            for pipe_element in unhosted_pipe:
                doc.Delete(pipe_element.Id)
            for pipe_pair in rogue_pipe:
                cleanup_insulation(pipe_pair)
            print("Deleted {num} unhosted pipe insulation elements".format(
                num=len(unhosted_pipe)))
            print("Moved {num} rogue pipe insulation elements.".format(
                num=len(rogue_pipe)))
        if clean_duct:
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


def find_rogue_elements(doc, elems):
    """Find all unhosted or rogue insulation elements."""
    unhosted_elements = []
    rogue_elements = []
    for element in elems:
        host_id = element.HostElementId
        host_element = doc.GetElement(host_id)
        if host_element is None:
            unhosted_elements.append(element)
        else:
            if element.WorksetId != host_element.WorksetId:
                rogue_elements.append(ElementHostPair(element, host_element))
    return rogue_elements, unhosted_elements


def query_all_elements(doc, cat):
    """Return all elements of a category from a document."""
    filter = db.ElementCategoryFilter(cat)
    collector = db.FilteredElementCollector(doc)
    elements = collector.WherePasses(filter)\
                        .WhereElementIsNotElementType()\
                        .ToElements()
    # pythonic_elements = [element for element in elements]
    return elements


def print_summary(elems, caption=""):
    """Print a summary of the given list."""
    length = elems.Count
    print("{caption} {length}".format(caption=caption, length=length))


def print_all(elems, caption=None, indent=0):
    """Print all elements from the given list."""
    total = elems.Count
    if caption:
        print(caption)
    for index, element in enumerate(elems):
        print("{indent}[{index}/{total}]: {element}".format(
            indent=indent*" ",
            index=index,
            total=total,
            element=element))

def write_report(path, upipe, rpipe, uduct, rduct):
    """Write report of unhosted and rogue insulation elements to a file."""
    print("writing report at {}".format(path))
    with open(path, mode="w") as file:
        file.write("Hello World!\n")
        # TODO: implement output time stamp
        # TODO: implement report creation


if __name__ == "__main__":
    main()
    # revit python shell console management
    __window__.Hide()
    __window__.Close()
