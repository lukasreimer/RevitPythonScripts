"""Color all elements of a category in the view by the value of a parameter."""

from HTMLParser import HTMLParser
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui
clr.AddReference("System.Windows.Forms")
import System.Windows.Forms as swf

__name = "ColorByParameterValue.py"
__version = "1.0a"


def main():
    """Main Function."""

    print("🐍 Running {name} version {ver}".format(name=__name, ver=__version))

    # TODO: implement
    return ui.Result.Succeeded


if __name__ == "__main__":
    #__window__.Hide()
    result = main()
    if result == ui.Result.Succeeded:
        __window__.Close()
