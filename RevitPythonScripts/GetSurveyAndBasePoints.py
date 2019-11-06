"""Query the Survey Point and the Project Base Point and get the translation
and rotation.
"""

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui

__name = "GetSurveyAndBasePoints.py"
__version = "0.1a"


def main():
    """Main script docstring."""
    
    print("🐍 Running {name} version {ver}:".format(name=__name, ver=__version))

    # Setup
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # Main script
    print("Hello World! ✔✘🛈➜😊")


if __name__ == "__main__":
    # __window__.Hide()
    main()
    # __window__.Close()
