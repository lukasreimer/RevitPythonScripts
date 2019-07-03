"""Tag vertical risers in current view."""

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui


def main():
    """Main Script

    This script is tagging all vertical pipe risers in the current view.
    """
    print("Running TagRisersInView.py script...")

    # important revit python shell variables
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # main script
    print("Hello World!")


if __name__ == "__main__":
    main()
    # revit python shell console management
    # __window__.Hide()
    # __window__.Close()
