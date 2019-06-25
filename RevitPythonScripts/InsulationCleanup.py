"""Cleanup unhosted and rogue pipe and duct insulation."""

import collections
import itertools
import os
import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui

clr.AddReference("System.Windows.Forms")
import System.Windows.Forms as swf


def main():
    """Main Script."""

    print("Running InsulationCleanup.py script...")

    # STEP 0: Setup
    doc = __revit__.ActiveUIDocument.Document

    # STEP 1: Inspect Model
    pipe_ins_elems = query_all_elements(doc=doc, cat=db.BuiltInCategory.OST_PipeInsulations)
    duct_ins_elems = query_all_elements(doc=doc, cat=db.BuiltInCategory.OST_DuctInsulations)

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
    dialog.FooterText = "<a href=\"http://www.google.de\">Ask Google</a>"
    dialog.AddCommandLink(ui.TaskDialogCommandLinkId.CommandLink1, "Write Report")
    dialog.AddCommandLink(ui.TaskDialogCommandLinkId.CommandLink2, "Clean Insulation")
    result = dialog.Show()

    # STEP 3: Write report or clean up insulation
    if result == ui.TaskDialogResult.CommandLink1:  # Write report
        save_dialog = swf.SaveFileDialog()
        save_dialog.Title = "Save Insulation Cleanup Report"
        save_dialog.Filter = "Text files|*.txt"
        save_dialog.FileName = "report.txt"
        if save_dialog.ShowDialog() == swf.DialogResult.OK:
            file_path = save_dialog.FileName
            print("Writing report to {0}".format(file_path))
            # TODO: actually save report file
            with open(file_path, mode="w") as fh:
                report = write_report(unhosted_pipe, rogue_pipe, unhosted_duct, rogue_duct)
                fh.writelines(report)
                print("Done.")
        else:
            print("File save dialog canceled.")

    elif result == ui.TaskDialogResult.CommandLink2:  # Clean Insulation
        transaction = db.Transaction(doc)
        transaction.Start("InsulationCleanup.py")
        try:
            print("Cleaning Insulation...")
            for pipe_element in unhosted_pipe:
                doc.Delete(pipe_element.Id)
            print("Deleted {num} unhosted pipe insulation elements".format(num=len(unhosted_pipe)))
            for pipe_pair in rogue_pipe:
                cleanup_insulation(pipe_pair)
            print("Moved {num} rogue pipe insulation elements.".format(num=len(rogue_pipe)))
            for duct_element in unhosted_duct:
                doc.Delete(duct_element.Id)
            print("Deleted {num} unhosted duct insulation elements.".format(num=len(unhosted_duct)))
            for duct_pair in rogue_duct:
                cleanup_insulation(duct_pair)
            print("Moved {num} rogue duct insulation elements.".format(num=len(rogue_duct)))
        except Exception as exception:
            print("Failed.\nException:\n{ex}".format(ex=exception))
            transaction.RollBack()
        else:
            print("Done.")
            transaction.Commit()
    else:
        print("Nothing to do.")


# Helpers:
ElementHostPair = collections.namedtuple("ElementHostPair", ["element", "host"])


def cleanup_insulation(pair):
    """Cleanup rogue insulation elements."""
    element_workset_id = pair.element.WorksetId.IntegerValue
    host_workset_id = pair.host.WorksetId.IntegerValue
    # get the host workset parameter for setting its value back and forth
    host_workset_parameter = pair.host.get_Parameter(db.BuiltInParameter.ELEM_PARTITION_PARAM)
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

def write_summary(upipe, rpipe, uduct, rduct):
    """Write a summary of unhosted and rogue insulation elements."""
    pass

def write_report(upipe, rpipe, uduct, rduct):
    """Write report of unhosted and rogue insulation elements."""
    report = []
    status = "time: ...".format()
    report.append(status)
    header = "type, id".format()
    report.append(header)
    total = len(upipe) + len(rpipe) + len(uduct) + len(rduct)
    for idx, elem in enumerate(itertools.chain(upipe, rpipe, uduct, rduct)):
        line = "[{idx}/{tot}] {elem}\n".format(idx=idx, tot=total, elem=elem)
        report.append(line)
        print(report)
    return report


if __name__ == "__main__":
    main()
    # revit python shell console management
    # _window__.Hide()
    # __window__.Close()
