"""Calculate and display the total length of the currently selected pipes and
ducts.
"""

from __future__ import print_function
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui

__name = "SelectionLength.py"
__version = "0.1b"

FEET_2_METER = 0.3048  # meters per feet

def main():
    """Main Function."""
    
    print("🐍 Running {fname} version {ver}...".format(fname=__name, ver=__version))

    # STEP 0: Setup
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument

    # STEP 1: Get Selection
    selection = uidoc.Selection
    element_ids = selection.GetElementIds()
    
    # STEP 2: Filter Selection
    ducts, flex_ducts = [], []
    pipes, flex_pipes = [], []
    for element_id in element_ids:
        element = doc.GetElement(element_id)
        if isinstance(element, db.Mechanical.Duct):
            ducts.append(element)
        if isinstance(element, db.Mechanical.FlexDuct):
            flex_ducts.append(element)
        if isinstance(element, db.Plumbing.Pipe):
            pipes.append(element)
        if isinstance(element, db.Plumbing.FlexPipe):
            flex_pipes.append(element)
    
    # STEP 3: Aggregate data
    duct_length = total_length(ducts)
    flex_duct_length = total_length(flex_ducts)
    pipe_length = total_length(pipes)
    flex_pipe_length = total_length(flex_pipes)

    # STEP 4: Ouput Result
    summary = "Duct = {0} m / Flex Duct = {1}m\n".format(duct_length, flex_duct_length)
    summary += "Ducting = {0} m\n\n".format(duct_length + flex_duct_length)
    summary += "Pipe = {0} m / Flex Pipe = {1}m\n".format(pipe_length, flex_pipe_length)
    summary += "Piping = {0} m".format(pipe_length + flex_pipe_length)

    dialog = ui.TaskDialog(title="Duct Length")
    dialog.MainInstruction = "Selection Lengths Summary"
    dialog.MainContent = summary
    dialog.CommonButtons = ui.TaskDialogCommonButtons.Close
    dialog.DefaultButton = ui.TaskDialogResult.Close
    dialog.Show()

    print("✔\nDone. 😊")
    return ui.Result.Succeeded


def total_length(elements):
    """Sum up the lengths of elements (ducts/pipes) to get the total length in meters."""
    total_length = 0
    for element in elements:
        parameter = element.get_Parameter(db.BuiltInParameter.CURVE_ELEM_LENGTH)
        length_in_meters = parameter.AsDouble() * FEET_2_METER
        total_length += length_in_meters
    return total_length


if __name__ == "__main__":
    #__window__.Hide()
    result = main()
    if result == ui.Result.Succeeded:
        __window__.Close()
