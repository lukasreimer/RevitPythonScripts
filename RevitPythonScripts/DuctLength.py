import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui

FEET_2_METER = 0.3048

def main():
    """Main Function."""
    # STEP 0: Setup
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # STEP 1: Get Selection
    selection = uidoc.Selection
    print(selection)
    element_ids = selection.GetElementIds()
    print(element_ids)
    
    # STEP 2: Filter Selection
    ducts = []
    for element_id in element_ids:
    	element = doc.GetElement(element_id)
    	if isinstance(element, db.Mechanical.Duct):
    		ducts.append(element)
    print(ducts)
    
    # STEP 3: Aggregate data
    total_length_m = 0
    for duct in ducts:
    	print(duct)
    	parameter = duct.get_Parameter(db.BuiltInParameter.CURVE_ELEM_LENGTH)
    	print(parameter)
    	length_m = parameter.AsDouble() * FEET_2_METER
    	print(length_m)
    	total_length_m += length_m
	print(total_length_m)
    
    # STEP 4: Ouput Result
    summary_text = "Selected Elements = {se}\nSelected Ducts = {sd}\nTotal Length = {tl} m\n".format(
    	se=len(element_ids),
    	sd=len(ducts),
    	tl=total_length_m
    )
    dialog = ui.TaskDialog(title="Duct Length")
    dialog.MainInstruction = "Duct Length Summary"
    dialog.MainContent = summary_text
    dialog.FooterText = "<a href=\"http://www.google.de\">Ask Google</a>"
    #dialog.AddCommandLink(ui.TaskDialogCommandLinkId.CommandLink1, "Write Report")
    #dialog.AddCommandLink(ui.TaskDialogCommandLinkId.CommandLink2, "Clean Insulation")
    dialog.CommonButtons = ui.TaskDialogCommonButtons.Close;
    dialog.DefaultButton = ui.TaskDialogResult.Close;
    result = dialog.Show()


if __name__ == "__main__":
    main()
    # __window__.Hide()
    # __window__.Close()