"""About Page for Insulation Cleanup Script."""

import clr
clr.AddReference("RevitAPIUI")
import Autodesk.Revit.UI as ui


__name = "InsulationCleanup.py"
__version = "1.0b"

TITLE = "About Insulation Cleanup"
MAIN_INSTRUCTION = "About Insulation Cleanup"
MAIN_CONTENT = [
    "{name} Script Version {ver}\n".format(name=__name, ver=__version),
    "Check out on <a href=\"https://github.com/lukasreimer/RevitPythonScripts\">github.com/lukasreimer/RevitPythonScripts</a>\n",
    "Icons by <a href=\"https://www.icons8.com/\">icons8.com</a>\n",
    "\n",
    "</> with ❤️ in Berlin"
]
EXPANDED_CONTENT = [
    "This Script cleans up unhosted or rogue pipe and duct insulation.",
    "A rogue piece of insulation is an element that is located on a different workset than its hosting element (e.g. pipe, pipe fitting, duct, duct fitting, etc.).",
    "The cleanup is done without deleting and/or recreating any elements.",
    "In order to reling the insulation worksets an internal mechanism of Revit is used.",
    "Changing the hosts workset to the insulation workset and then back to the original workset carries the insulation element over to the host workset.",
    "Completely unhosted insulation elements (elements without a host) are deleted.",
    "The script can also be used for inspection and reporting only.",
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
