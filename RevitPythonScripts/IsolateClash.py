"""Isolate clash in current view."""

from HTMLParser import HTMLParser
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
import System.Windows.Forms as swf
import System.Drawing as sd

__name = "IsolateClash.py"
__version = "0.1a"

THRESHOLD = 10  # ft


def main():
    """Main Function."""
    print("Running {fname} version {ver}...".format(fname=__name, ver=__version))

    # STEP 0: Setup
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # Ask user for clash report html file
    open_dialog = swf.OpenFileDialog()
    open_dialog.Title = "Open Interference Check Report"
    open_dialog.Filter = "HMTL files (*.html)|*.html"
    if open_dialog.ShowDialog() == swf.DialogResult.OK:
        file_path = open_dialog.FileName
        print("file path = {fp}".format(fp=file_path))

    # Parse clash report html file
    with open(file_path, mode="rb") as html_file:
        html = html_file.read()
        html = unicode(html, "utf-8")
    # print(html)
    parser = InterferenceReportParser()
    parser.feed(html)
    print(parser.clashes)

    clashing_ids = []
    for pair in parser.clashes.values():
        for elem_id in pair:
            clashing_ids.append(elem_id)
    clashing_ids = set(clashing_ids)
    print(clashing_ids)
    print(len(clashing_ids))

    # TODO: Ask user which clash to isolate
    first_clash = parser.clashes[1]
    # STEP 1: Get the clashing elements (ids)
    elem_id_a = db.ElementId(first_clash[0])
    elem_a = doc.GetElement(elem_id_a)
    print(elem_a)
    elem_id_b = db.ElementId(first_clash[1])
    elem_b = doc.GetElement(elem_id_b)
    print(elem_b)

    ogs = db.OverrideGraphicSettings()
    ogs.SetProjectionLineColor(db.Color(255, 0, 0))
    ogs.SetProjectionLineWeight(7)
    ogs.SetProjectionFillColor(db.Color(255, 0, 0))
    ogs.SetProjectionFillPatternId(db.ElementId(19))

    # STEP 2: Create an outline around the clash
    bbox_a = elem_a.get_BoundingBox(view)
    print(bbox_a)
    min_a = bbox_a.Min
    max_a = bbox_a.Max
    bbox_b = elem_b.get_BoundingBox(view)
    print(bbox_b)
    min_b = bbox_b.Min
    max_b = bbox_b.Max

    outline_offset = db.XYZ(THRESHOLD, THRESHOLD, THRESHOLD)
    min_o = min(min_a, min_b) - outline_offset
    max_o = max(max_a, max_b) + outline_offset

    outline = db.Outline(min_o, max_o)

    # STEP 3: Select all Elements interseting the outline
    filter = db.BoundingBoxIntersectsFilter(outline)
    selection = db.FilteredElementCollector(doc).WherePasses(filter).ToElementIds()

    ogs_half = db.OverrideGraphicSettings()
    ogs_half.SetProjectionLineColor(db.Color(192, 192, 192))
    ogs_half.SetProjectionFillColor(db.Color(192, 192, 192))
    ogs_half.SetProjectionFillPatternId(db.ElementId(19))
    ogs_half.SetSurfaceTransparency(50)

    # STEP 4: Isolate elements in current view
    transaction = db.Transaction(doc)
    transaction.Start("{name} - v{ver}".format(name=__name, ver=__version))
    try:
        view.IsolateElementsTemporary(selection)
        for elem_id in selection:
            view.SetElementOverrides(elem_id, ogs_half)
        view.SetElementOverrides(elem_id_a, ogs)
        view.SetElementOverrides(elem_id_b, ogs)
    except Exception as ex:
        print("Exception: {0}".format(ex))
        transaction.RollBack()
    else:
        transaction.Commit()
        print("Done.")


class InterferenceReportParser(HTMLParser):
    """HTML parser for parsing Revit Interference CHeck reports."""

    def __init__(self):
        HTMLParser.__init__(self)
        self.clashes = {}  # clash#: (itemA#, itemB#)
        self.in_column = False
        self.line_counter = -1  # 0 = header, 1...n = data
        self.column_counter = 0  # 1 = id, 2 = item A, 3 = item B
        self.current_data = []

    def handle_starttag(self, tag, attrs):
        if tag == "tr":  # enter line (row)
            self.in_row = True
            self.line_counter += 1
        elif tag == "td":  # enter data column
            self.in_column = True
            self.column_counter += 1

    def handle_endtag(self, tag):
        if tag == "tr":  # exit line (row)
            self.in_row = False
            self.column_counter = 0  # reset for next line
            if self.line_counter > 0:
                self.clashes[self.line_counter] = self.current_data
                self.current_data = []
        elif tag == "td":  # exit data column
            self.in_column = False

    def handle_data(self, data):
        if self.in_column and self.line_counter > 0 and self.column_counter > 1:
            elem_id = int(data.split(":")[-1].strip().split(" ")[-1].strip())
            self.current_data.append(elem_id)


if __name__ == "__main__":
    # __window__.Hide()
    main()
    # __window__.Close()
