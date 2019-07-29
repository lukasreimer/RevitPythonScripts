"""Module Docstring.

This is a concise description of the script.
"""
# standard library imports
import clr
# third party imports
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui
# local imports
# ...

# Main Script
def main():
    """Function Docstring.

    This is a description of the main function containing the business logic.

    Args:
        ...

    Returns:
        None: implicityly.
    """
    # important revit python shell variables
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # main script
    print("Hello World!")


if __name__ == "__main__":
    # __window__.Hide()
    main()
    # __window__.Close()
