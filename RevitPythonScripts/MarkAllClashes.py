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

CLASH_COLOR = db.Color(255, 0, 0)
CLASH_LINEWEIGHT = 7
CLASH_PATTERN_ID = db.ElementId(19)

FADED_COLOR = db.Color(192, 192, 192)
FADED_PATTERN_ID = CLASH_PATTERN_ID
FADED_TRANSPARENCY = 50


def main():
    """Main Function."""
    
    print("Running {fname} version {ver}...".format(fname=__name, ver=__version))

    # STEP 0: Setup
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # STEP 1: Ask user for clash report html file adn parse it
    print("Opening interference check report file...")
    open_dialog = swf.OpenFileDialog()
    open_dialog.Title = "Open Interference Check Report"
    open_dialog.Filter = "HMTL files (*.html)|*.html"
    if open_dialog.ShowDialog() == swf.DialogResult.OK:
        file_path = open_dialog.FileName

        # STEP 2: Parse clash report file
        print("Parsing {fname} ...".format(fname=file_path))
        with open(file_path, mode="rb") as html_file:
            html = html_file.read()
            html = unicode(html, "utf-8")
        parser = InterferenceReportParser()
        parser.feed(html)
        parser.close()
        clashes = parser.clashes
        print("Found {num} clashes in the report.".format(num=len(clashes)))
        #print(clashes)

        clashing_ids = []
        for pair in parser.clashes.values():
            for elem_id in pair:
                clashing_ids.append(elem_id)
        clashing_ids = set(clashing_ids)
        print("Found {num} clashing elements.".format(num=len(clashing_ids)))
        # print(clashing_ids)

        # Get all elements in the view
        all_ids = db.FilteredElementCollector(doc, view.Id)\
                    .WhereElementIsNotElementType()\
                    .ToElementIds()

        # STEP 2: Setup override styles for marking the clashing elements
        clashing_overrides = db.OverrideGraphicSettings()
        clashing_overrides.SetProjectionLineColor(CLASH_COLOR)
        clashing_overrides.SetProjectionLineWeight(CLASH_LINEWEIGHT)
        clashing_overrides.SetProjectionFillColor(CLASH_COLOR)
        clashing_overrides.SetProjectionFillPatternId(CLASH_PATTERN_ID)

        faded_overrides = db.OverrideGraphicSettings()
        faded_overrides.SetProjectionLineColor(FADED_COLOR)
        faded_overrides.SetProjectionFillColor(FADED_COLOR)
        faded_overrides.SetProjectionFillPatternId(FADED_PATTERN_ID)
        faded_overrides.SetSurfaceTransparency(FADED_TRANSPARENCY)
        
        # STEP 3: Mark all clashing elements by overriding their graphics in the current view
        transaction = db.Transaction(doc)
        transaction.Start("{name} - v{ver}".format(name=__name, ver=__version))
        try:
            for elem_id in all_ids:  # fade all visible elements
                view.SetElementOverrides(elem_id, faded_overrides)
            for elem_id in clashing_ids:  # emphasize the clashing elements
                view.SetElementOverrides(db.ElementId(elem_id), clashing_overrides)
        except Exception as ex:
            print("Exception: {ex}".format(ex=ex))
            transaction.RollBack()
        else:
            transaction.Commit()
            print("Done.")
    else:
        print("no file to parse.")


class InterferenceReportParser(HTMLParser):
    """HTML parser for parsing Revit Interference CHeck reports."""

    def __init__(self):
        """Initializer."""
        HTMLParser.__init__(self)
        self.clashes = {}  # clash#: (itemA#, itemB#)
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
                self.clashes[self.line_counter] = self.current_data
                self.current_data = []
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
