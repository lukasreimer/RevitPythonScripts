"""Export all Schedules with a certain prefix at once."""

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui
clr.AddReference("System.Windows.Forms")
import System.Windows.Forms as swf

__name = "ExportSchedules.py"
__version = "0.1a"

PREFIX = "Qty_"


def main():
    """Main script docstring."""
    
    print("Running {name} version {ver}".format(name=__name, ver=__version))

    # STEP 0: Setup
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # STEP 1: Find all appropriate schedules
    all_schedules = db.FilteredElementCollector(doc)\
                  .OfCategory(db.BuiltInCategory.OST_Schedules)\
                  .WhereElementIsNotElementType()\
                  .ToElements()
    print("Found {num} schedules in the project.".format(num=len(all_schedules)))
    #print(all_schedules)

    quantity_schedules = [s for s in all_schedules if s.Name.startswith(PREFIX)]
    print("Found {num} schedules with prefix '{prefix}'.".format(
        num=len(quantity_schedules), prefix=PREFIX))
    #print(quantity_schedules)

    # STEP 2: Ask for export folder location
    folder_browser = swf.FolderBrowserDialog()
    folder_browser.Description = "Please select an output folder for saving the schedules."
    if folder_browser.ShowDialog() != swf.DialogResult.OK:  # no folder selected
        print("No folder selected. Nothing to do.")
        return ui.Result.Cancelled
    print("Selected output folder: {folder}".format(
        folder=folder_browser.SelectedPath))        

    # STEP 3: Export all selected schedules
    # https://www.revitapidocs.com/2018/8ba18e73-6daf-81b6-d15b-e4aa90bc8c22.htm
    export_options = db.ViewScheduleExportOptions()
    export_options.FieldDelimiter = ","
    for schedule in quantity_schedules:
        file_name = "{name}.csv".format(name=schedule.Name)
        schedule.Export(folder_browser.SelectedPath, file_name, export_options)
    print("Done.")
    return ui.Result.Succeeded


if __name__ == "__main__":
    # __window__.Hide()
    main()
    # __window__.Close()
