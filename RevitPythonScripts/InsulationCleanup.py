"""Cleanup unhosted and rogue pipe and duct insulation."""

import collections
import datetime
import itertools
import os
import string
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

    rogue_pipe, unhosted_pipe = find_rogue_elements(doc=doc, elems=pipe_ins_elems)
    rogue_duct, unhosted_duct = find_rogue_elements(doc=doc, elems=duct_ins_elems)

    summary_list = write_summary(
        tpipe=pipe_ins_elems, tduct=duct_ins_elems,  # totals
        upipe= unhosted_pipe, uduct=unhosted_duct,  # unhosted
        rpipe=rogue_pipe, rduct=rogue_duct)  # rogue
    summary_text = string.join(summary_list, "\n")
    print(summary_text)

    # STEP 2: Receive User Input
    dialog = ui.TaskDialog(title="Insulation Cleanup")
    dialog.MainInstruction = "Insulation Cleanup Summary"
    dialog.MainContent = summary_text
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
            with open(file_path, mode="wb") as fh:
                report = write_report(doc, unhosted_pipe, rogue_pipe, unhosted_duct, rogue_duct)
                for line in report:
                    fh.write("{ln}\n".format(ln=line))
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

def write_summary(tpipe, tduct, upipe, rpipe, uduct, rduct):
    """Write a summary of unhosted and rogue insulation elements."""
    summary = []
    summary.append("Pipe: unhosted={uh:4d}, rogue={ro:4d} (total={tot:6d})".format(uh=len(upipe), ro=len(rpipe), tot=len(tpipe)))
    summary.append("Duct: unhosted={uh:4d}, rogue={ro:4d} (total={tot:6d})".format(uh=len(uduct), ro=len(rduct), tot=len(tduct)))
    return summary


def write_report(doc, upipe, rpipe, uduct, rduct):
    """Write report of unhosted and rogue insulation elements."""
    workset_table = doc.GetWorksetTable()
    report = []
    report.append("time: {now}".format(now=datetime.datetime.now()))
    report.append("[index/total] element, host")
    total_unhosted = len(upipe) + len(uduct)
    total_rogue = len(rpipe) + len(rduct)
    report.append("--- Unhosted: {num_unhosted} elements ---".format(num_unhosted=total_unhosted))
    for idx, pair in enumerate(itertools.chain(upipe, uduct)):
        elem, host = pair
        line = "[{idx}/{tot}] #{e_id}, {e_name} @'{e_workset}' --> #{h_id}, {h_name} @'{h_workset}'".format(
            idx=idx, tot=total_unhosted,
            e_id=elem.Id, e_name=elem.Name, e_workset=workset_table.GetWorkset(elem.WorksetId).Name,
            h_id=host.Id, h_name=host.Name, h_workset=workset_table.GetWorkset(host.WorksetId).Name)
        report.append(line)
    report.append("--- Rogue: {num_rogue} elements ---".format(num_rogue=total_rogue))
    for idx, pair in enumerate(itertools.chain(upipe, rpipe, uduct, rduct)):
        elem, host = pair
        line = "[{idx}/{tot}] #{e_id}, {e_name} @'{e_workset}' --> #{h_id}, {h_name} @'{h_workset}'".format(
            idx=idx, tot=total_rogue,
            e_id=elem.Id, e_name=elem.Name, e_workset=workset_table.GetWorkset(elem.WorksetId).Name,
            h_id=host.Id, h_name=host.Name, h_workset=workset_table.GetWorkset(host.WorksetId).Name)
        report.append(line)
    return report


if __name__ == "__main__":
    main()
    # revit python shell console management
    # _window__.Hide()
    # __window__.Close()
