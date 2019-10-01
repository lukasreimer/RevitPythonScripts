"""Simple script just saying hello from Python."""

import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui

__name = "Hello.py"
__version = "0.1"

def main():
    """Main Script."""
    print("Running {name} version {ver}".format(name=__name, ver=__version))
    print("Hello World!")
    ui.TaskDialog.Show("Hello.py", "Hello from Python!")


if __name__ == "__main__":
    # __window__.Hide()
    main()
    # __window__.Close()
