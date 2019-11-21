"""Export all Schedules with a certain prefix at once."""

from __future__ import print_function
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui
clr.AddReference("System.Windows.Forms")
import System.Windows.Forms as swf

__name = "ExportSchedules.py"
__version = "0.1b"

PREFIX = "Qty_"


def main():
    """Main script docstring."""
    
    print("🐍 Running {fname} version {ver}...".format(fname=__name, ver=__version))

    # STEP 0: Setup
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # STEP 1: Find all appropriate schedules
    print("Getting all available schedules from the model...", end="")
    all_schedules = db.FilteredElementCollector(doc)\
                  .OfCategory(db.BuiltInCategory.OST_Schedules)\
                  .WhereElementIsNotElementType()\
                  .ToElements()
    print("✔")
    print("  ➜ Found {num} schedules in the project.".format(num=len(all_schedules)))
    #print(all_schedules)

    # STEP 2: Filtering for quantification schedules (with given prefix)
    print("Filtering quantification schedules from the found schedules...", end="")
    quantity_schedules = [s for s in all_schedules if s.Name.startswith(PREFIX)]
    print("✔")
    print("  ➜ Found {num} schedules with prefix '{prefix}'.".format(
        num=len(quantity_schedules), prefix=PREFIX))
    #print(quantity_schedules)

    # STEP 3: Ask for export folder location
    print("Please select an output folder for saving the schedules...", end="")
    folder_browser = swf.FolderBrowserDialog()
    folder_browser.Description = "Please select an output folder for saving the schedules."
    if folder_browser.ShowDialog() != swf.DialogResult.OK:  # no folder selected
        print("\n✘ No folder selected. Nothing to do.")
        return ui.Result.Cancelled
    print("✔")
    print("🛈 Selected output folder: {folder}".format(
        folder=folder_browser.SelectedPath))        

    # STEP 3: Export all selected schedules
    # https://www.revitapidocs.com/2018/8ba18e73-6daf-81b6-d15b-e4aa90bc8c22.htm
    print("Exporting schedules as CSV to selected output folder...", end="")
    try:
        export_options = db.ViewScheduleExportOptions()
        export_options.FieldDelimiter = ","
        for schedule in quantity_schedules:
            file_name = "{name}.csv".format(name=schedule.Name)
            schedule.Export(folder_browser.SelectedPath, file_name, export_options)
    except Exception as ex:
        print("\n✘ Exception:\n {ex}".format(ex=ex))
        return ui.Result.Failed
    else:
        print("✔\nDone. 😊")
        return ui.Result.Succeeded


if __name__ == "__main__":
    #__window__.Hide()
    result = main()
    # if result == ui.Result.Succeeded:
    #     __window__.Close()
