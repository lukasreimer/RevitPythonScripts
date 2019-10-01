"""Simple script just saying hello from Python.

Installation:
1) Create Hello.py (Python script) and Hello.xml (RPS addin manifest)
2) Deploy RPS Addin from RPS ribbon button "Deploy RpsAddin", select Hello.xml
    --> generates "Output_Hello/" folder with Hello.dll and other DLLs
3) Move outputs to desired storage location
    --> e.g. C:\Users\<USERNAME>\AppData\Roaming\Autodesk\Revit\Addins\2018\Hello
4) Create Hello.addin (Revit addin manifest) pointing to storage location
    --> store at C:\Users\<USERNAME>\AppData\Roaming\Autodesk\Revit\Addins\2018
"""

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
