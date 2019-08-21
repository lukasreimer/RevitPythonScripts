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

__name = "InsulationCleanup.py"
__version = "1.0b"

CHECK = "✔"
ERROR = "✘"

def main():
    """Main Script."""

    print("Running {name} version {ver}...".format(name=__name, ver=__version))

    # STEP 0: Setup
    doc = __revit__.ActiveUIDocument.Document

    # STEP 1: Inspect Model and summarize findings
    pipe_insulations = query_all_elements_of_category(doc=doc, cat=db.BuiltInCategory.OST_PipeInsulations)
    duct_insulations = query_all_elements_of_category(doc=doc, cat=db.BuiltInCategory.OST_DuctInsulations)
    rogue_pipe, unhosted_pipe = find_rogue_and_unhosted_elements(doc=doc, elems=pipe_insulations)
    rogue_duct, unhosted_duct = find_rogue_and_unhosted_elements(doc=doc, elems=duct_insulations)
    summary_list = write_summary(
        tpipe=pipe_insulations, tduct=duct_insulations,  # totals
        upipe= unhosted_pipe, uduct=unhosted_duct,       # unhosted
        rpipe=rogue_pipe, rduct=rogue_duct)              # rogue
    summary_text = string.join(summary_list, "\n")
    print(summary_text)

    # STEP 2: Receive User Input
    dialog = ui.TaskDialog(title="Insulation Cleanup")
    dialog.MainInstruction = "Insulation Cleanup Summary"
    dialog.MainContent = summary_text
    dialog.AddCommandLink(ui.TaskDialogCommandLinkId.CommandLink1, "Write Report")
    dialog.AddCommandLink(ui.TaskDialogCommandLinkId.CommandLink2, "Clean Insulation")
    dialog.CommonButtons = ui.TaskDialogCommonButtons.Close
    dialog.DefaultButton = ui.TaskDialogResult.Close
    result = dialog.Show()

    # STEP 3: Write report or clean up insulation
    if result == ui.TaskDialogResult.CommandLink1:  # Write report
        save_dialog = swf.SaveFileDialog()
        save_dialog.Title = "Save Insulation Cleanup Report"
        save_dialog.Filter = "Text files|*.txt"
        save_dialog.FileName = "report.txt"
        if save_dialog.ShowDialog() == swf.DialogResult.OK:  # Save report
            file_path = save_dialog.FileName
            print("Writing report to {0}".format(file_path))
            with open(file_path, mode="wb") as fh:
                report = write_report(
                    doc, unhosted_pipe, rogue_pipe, unhosted_duct, rogue_duct)
                for line in report:
                    fh.write("{line}\r\n".format(line=line))
                print("Done.")
        else:  # Don't save report
            print("File save dialog canceled.")
    elif result == ui.TaskDialogResult.CommandLink2:  # Clean Insulation
        transaction = db.Transaction(doc)
        transaction.Start("{name} - v{ver}".format(name=__name, ver=__version))
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


ElementHostPair = collections.namedtuple("ElementHostPair", ["element", "host"])


def query_all_elements_of_category(doc, cat):
    """Return all elements of a category from a document."""
    collector = db.FilteredElementCollector(doc)
    elements = collector.OfCategory(cat)\
                        .WhereElementIsNotElementType()\
                        .ToElements()
    return elements


def find_rogue_and_unhosted_elements(doc, elems):
    """Find all rogue and unhosted insulation elements."""
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


def cleanup_insulation(pair):
    """Cleanup rogue and unhosted insulation elements."""
    element_workset_id = pair.element.WorksetId.IntegerValue
    host_workset_id = pair.host.WorksetId.IntegerValue
    host_workset_parameter = pair.host.get_Parameter(
        db.BuiltInParameter.ELEM_PARTITION_PARAM)
    host_workset_parameter.Set(element_workset_id)
    host_workset_parameter.Set(host_workset_id)


def write_summary(tpipe, tduct, upipe, rpipe, uduct, rduct):
    """Write a summary of rogue and unhosted insulation elements."""
    summary = []
    summary.append("Pipe Insulation:")
    summary.append("{res} Found {num} rogue pipe insulation elements.".format(num=len(rpipe), res=ERROR if len(rpipe) else CHECK))
    summary.append("{res} Found {num} unhosted pipe insulation elements.".format(num=len(upipe), res=ERROR if len(upipe) else CHECK))
    summary.append("There is a total of {tot} pipe insulation elements in the model.".format(tot=len(tpipe)))
    summary.append("Duct Insulation:")
    summary.append("{res} Found {num} rogue duct insulation elements.".format(num=len(rduct), res=ERROR if len(rduct) else CHECK))
    summary.append("{res} Found {num} unhosted duct insulation elements.".format(num=len(uduct), res=ERROR if len(uduct) else CHECK))
    summary.append("There is a total of {tot} duct insulation elements in the model.".format(tot=len(tduct)))
    return summary


def write_report(doc, upipe, rpipe, uduct, rduct):
    """Write report of rogue and unhosted insulation elements."""
    workset_table = doc.GetWorksetTable()
    rogue = len(upipe) + len(uduct)
    unhosted = len(rpipe) + len(rduct)
    report = []
    # write header with general information
    report.append("reporting time, {now}".format(now=datetime.datetime.now()))
    report.append("rogue elements, {num}".format(num=rogue))
    report.append("unhosted elements, {num}".format(num=unhosted))
    report.append("---")
    # define csv structure template and header line
    line_template = "{idx},{eid},'{en}','{ews}',{hid},'{hn}','{hws}'"
    report.append(
        "index,element id,element name,element workset,host id,host name,host workset")
    # write rogue and unhosted element data:
    for idx, pair in enumerate(itertools.chain(upipe, rpipe, uduct, rduct)):
        elem, host = pair
        elem_workset = workset_table.GetWorkset(elem.WorksetId)
        host_workset = workset_table.GetWorkset(host.WorksetId)
        line = line_template.format(
            idx=idx,
            eid=elem.Id.IntegerValue, en=elem.Name, ews=elem_workset.Name,
            hid=host.Id.IntegerValue, hn=host.Name, hws=host_workset.Name)
        report.append(line)
    return report


if __name__ == "__main__":
    # __window__.Hide()
    main()
    # __window__.Close()
