"""About Page for Riser Tagging Script."""

import clr
clr.AddReference("RevitAPIUI")
import Autodesk.Revit.UI as ui


__version = "0.2b"

TITLE = "About Riser Tagging"
MAIN_INSTRUCTION = "About Riser Tagging"
MAIN_CONTENT = [
    "Riser Tagging Scripts Version {ver}\n".format(ver=__version),
    "Check out on <a href=\"https://github.com/lukasreimer/RevitPythonScripts\">github.com/lukasreimer/RevitPythonScripts</a>\n",
    "Icons by <a href=\"https://www.icons8.com/\">icons8.com</a>\n",
    "\n",
    "</> with ❤️ in Berlin"
]
EXPANDED_CONTENT = [
    "This set of scripts implements an automation workflow for placing riser arrow tags.",
    "It consists of 3 individual scripts which together represent the tagging workflow.",
    "\n• Script 1 (\"Tag Risers\") places riser arrow tags on all vertical pipe segments that intersect the top and bottom planes of the view range of the currently active view.",
    "The script tries to examine the flow through the pipe and select the proper symbol.",
    "If no flow information is available on the pipe, the default of downward flow (gravity) is assumed."
    "\n• Script 2 (\"Correct Ventilation\") corrects the riser tag arrow symbol of ventilation pipes based on the systemclassification of the tagged pipe element.",
    "If that element is of type 'Vent', the appropriate symbol is set for the tag type.",
    "\n• Script 3 (\"Color Riser Tags\") overrides the color of all pipe riser tags in the currently active view to match the system color of the tagged pipe.",
    "\n• Script 4 (\"Clear Riser Tags\") deletes all pipe riser tags in the current view based on the family name of the used pipe riser tag.",
    "Use carefully!",
    "Manually placed tags of the same family will also be deleted by this script."
]


def main():
    """Main Script."""

    dialog = ui.TaskDialog(title=TITLE)
    dialog.MainIcon = ui.TaskDialogIcon.TaskDialogIconInformation
    dialog.MainInstruction = MAIN_INSTRUCTION
    dialog.MainContent = "".join(MAIN_CONTENT)
    dialog.ExpandedContent = " ".join(EXPANDED_CONTENT)
    dialog.CommonButtons = ui.TaskDialogCommonButtons.Close
    dialog.DefaultButton = ui.TaskDialogResult.Close
    dialog.Show()


if __name__ == "__main__":
    __window__.Hide()
    main()
    __window__.Close()
