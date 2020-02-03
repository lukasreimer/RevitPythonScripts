"""Module docstring."""

# standard library imports
from __future__ import print_function
import clr
# third party imports
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui
# local imports
# ...

__name = "ScriptName.py"
__version = "0.1"

def main():
    """Main script docstring."""
    
    print("🐍 Running {name} version {ver}".format(name=__name, ver=__version))

    # Setup
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # Main script
    print("Hello World! ✔✘🛈➜😊")
    return ui.Result.Succeeded


if __name__ == "__main__":
    #__window__.Hide()
    result = main()
    if result == ui.Result.Succeeded:
        __window__.Close()
