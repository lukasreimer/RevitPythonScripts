"""Module Docstring.

This is a concise description of the script.
"""
# standard library imports
import time
import clr
# third party imports
clr.AddReference('RevitAPI') 
clr.AddReference('RevitAPIUI') 
import Autodesk.Revit.DB as db
# local imports
# ...

# Main Script
def main():
    """Function Docstring.

    This is a description of the main function containing the business logic.

    Args:
        app (Application): Running application.
        doc (Document): Open document.
        uidoc (ActiveUIDocument): Active UI document.
        view (ActiveView): Currently active view.

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
    start = time.clock()
    main()
    runtime = time.clock() - start
    print("Runtime = {0} seconds".format(runtime))

    # revit python shell console management
    # __window__.Hide()
    # __window__.Close()
