import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui

FEET_2_METER = 0.3048

def main():
    """Main Function."""
    # STEP 0: Setup
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument

    # STEP 1: Get Selection
    selection = uidoc.Selection
    element_ids = selection.GetElementIds()
    
    # STEP 2: Filter Selection
    ducts = []
    for element_id in element_ids:
    	element = doc.GetElement(element_id)
    	if isinstance(element, db.Mechanical.Duct):
    		ducts.append(element)
    
    # STEP 3: Aggregate data
    total_length_m = 0
    for duct in ducts:
    	parameter = duct.get_Parameter(db.BuiltInParameter.CURVE_ELEM_LENGTH)
    	length_m = parameter.AsDouble() * FEET_2_METER
    	total_length_m += length_m
    
    # STEP 4: Ouput Result
    dialog = ui.TaskDialog(title="Duct Length")
    dialog.MainInstruction = "Total Selected Duct Length = {0} m".format(total_length_m)
    dialog.CommonButtons = ui.TaskDialogCommonButtons.Close
    dialog.DefaultButton = ui.TaskDialogResult.Close
    dialog.Show()


if __name__ == "__main__":
    main()
    __window__.Hide()
    __window__.Close()