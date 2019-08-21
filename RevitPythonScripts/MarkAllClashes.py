"""Mark all clashes from an interference report in current view."""

from HTMLParser import HTMLParser
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui
clr.AddReference("System.Windows.Forms")
import System.Windows.Forms as swf

__name = "MarkAllClashes.py"
__version = "0.1a"

CLASH_COLOR = db.Color(255, 0, 0)  # red
CLASH_PATTERN_ID = db.ElementId(19)
FADED_COLOR = db.Color(192, 192, 192)  # light gray
FADED_PATTERN_ID = CLASH_PATTERN_ID
FADED_TRANSPARENCY = 50

clashing_overrides = db.OverrideGraphicSettings()
clashing_overrides.SetProjectionLineColor(CLASH_COLOR)
clashing_overrides.SetProjectionFillColor(CLASH_COLOR)
clashing_overrides.SetProjectionFillPatternId(CLASH_PATTERN_ID)
faded_overrides = db.OverrideGraphicSettings()
faded_overrides.SetProjectionLineColor(FADED_COLOR)
faded_overrides.SetProjectionFillColor(FADED_COLOR)
faded_overrides.SetProjectionFillPatternId(FADED_PATTERN_ID)
faded_overrides.SetSurfaceTransparency(FADED_TRANSPARENCY)


def main():
    """Main Function."""
    
    print("Running {fname} version {ver}...".format(fname=__name, ver=__version))

    # STEP 0: Setup
    #app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    #uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # STEP 1: Ask user for clash report html file adn parse it
    print("Opening interference check report file...")
    open_dialog = swf.OpenFileDialog()
    open_dialog.Title = "Open Interference Check Report"
    open_dialog.Filter = "HMTL files (*.html)|*.html"
    if open_dialog.ShowDialog() == swf.DialogResult.OK:  # file selected
        file_path = open_dialog.FileName
        # STEP 2: Parse clash report file and summarize findings
        print("Reading {fname}...".format(fname=file_path))
        with open(file_path, mode="rb") as html_file:
            html = html_file.read()  # just read the plain bytes
            uhtml = unicode(html, "utf-16")  # Revit exports html in UTF-16(-LE) encoding
        print("Parsing file contents...")
        parser = InterferenceReportParser()
        parser.feed(uhtml)
        parser.close()
        clashes = parser.clashes
        #print("Found {num} clashes in the report.".format(num=len(clashes)))
        clashing_ids = []
        for pair in parser.clashes.values():
            for elem_id in pair:
                clashing_ids.append(elem_id)
        clashing_ids = set(clashing_ids)
        #print("Found {num} clashing elements in the report.".format(num=len(clashing_ids)))
        # Get all element ids of the elements in the view
        all_ids = db.FilteredElementCollector(doc, view.Id)\
                    .WhereElementIsNotElementType()\
                    .ToElementIds()
        all_ids = set([elem_id.IntegerValue for elem_id in all_ids])
        #print("Found {num} total elements in the currently active view.".format(num=len(all_ids)))
        # Get all element ids of non-clashing elements in the view
        non_clashing_ids = all_ids - clashing_ids
        #print("Found {num} non-clashing elements in the currently active view.".format(num=len(non_clashing_ids)))
        # Create summary text for user input dialog       
        summary_text = "Checked report {path}\n".format(path=file_path)
        summary_text += "Found {num} clashes in the report.\n".format(num=len(clashes))
        summary_text += "Found {num} clashing elements involved in those clashes.\n".format(num=len(clashing_ids))
        summary_text += "The total number of elements in the current view is {num}\n".format(num=len(all_ids))
        summary_text += "Found {num} non-clashing elements in the current view.".format(num=len(non_clashing_ids))
        print(summary_text)

        # STEP 3: Ask user for display option
        dialog = ui.TaskDialog(title="Mark All Clashes")
        dialog.MainInstruction = "Interference Report Summary"
        dialog.MainContent = summary_text
        dialog.AddCommandLink(ui.TaskDialogCommandLinkId.CommandLink1, "Mark clashing elements and fade the rest")
        dialog.AddCommandLink(ui.TaskDialogCommandLinkId.CommandLink2, "Hide all non-clashing elements temporarily")
        dialog.CommonButtons = ui.TaskDialogCommonButtons.Close
        dialog.DefaultButton = ui.TaskDialogResult.Close
        result = dialog.Show()

        # Step 4: Emphasize the clashes based on the user selection
        transaction = db.Transaction(doc)
        transaction.Start("{name} - v{ver}".format(name=__name, ver=__version))
        try:
            if result == ui.TaskDialogResult.CommandLink1:  # Mark clashes and fade the rest
                print("Marking all clashing elements and fading the rest...")
                for elem_id in all_ids:  # fade all visible elements in the view
                    view.SetElementOverrides(db.ElementId(elem_id), faded_overrides)
                for elem_id in clashing_ids:  # emphasize the clashing elements
                    view.SetElementOverrides(db.ElementId(elem_id), clashing_overrides)
            elif result == ui.TaskDialogResult.CommandLink2:  # Hide all non-clashing elements
                print("Hiding all non-clashing elements in the view temporarily...")
                for elem_id in non_clashing_ids:  # hide alll non-clashing elements
                    view.HideElementTemporary(db.ElementId(elem_id))
            else:
                print("Nothing to do.")
        except Exception as ex:
            print("Exception: {ex}".format(ex=ex))
            transaction.RollBack()
        else:
            transaction.Commit()
            print("Done.")
    else:  # no file to parse
        print("Nothing to do.")


class InterferenceReportParser(HTMLParser):
    """HTML parser for parsing Revit Interference CHeck reports."""

    def __init__(self):
        """Initializer."""
        HTMLParser.__init__(self)
        self.clashes = {}  # clash#: [itemA#, itemB#]
        self.in_column = False
        self.line_counter = -1  # 0 = header, 1...n = data
        self.column_counter = 0  # 1 = id, 2 = item A, 3 = item B
        self.current_data = []

    def handle_starttag(self, tag, attrs):
        """Start tag handler."""
        if tag == "tr":  # enter line (row)
            self.in_row = True
            self.line_counter += 1
        elif tag == "td":  # enter data column
            self.in_column = True
            self.column_counter += 1

    def handle_endtag(self, tag):
        """End tag handler."""
        if tag == "tr":  # exit line (row)
            self.in_row = False
            self.column_counter = 0  # reset for next line
            if self.line_counter > 0:
                self.clashes[self.line_counter] = self.current_data  # save
                self.current_data = []  # reset
        elif tag == "td":  # exit data column
            self.in_column = False

    def handle_data(self, data):
        """Data handler."""
        if self.in_column and self.line_counter > 0 and self.column_counter > 1:
            elem_id = int(data.split(":")[-1].strip().split(" ")[-1].strip())
            self.current_data.append(elem_id)


if __name__ == "__main__":
    # __window__.Hide()
    main()
    # __window__.Close()
