"""Tag all vertical risers in current view."""
# TODO: investigate Transformation stuff messing up elevation / point comparisons

import itertools
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
import System.Windows.Forms as swf
import System.Drawing as sd

__name = "TagRisersInView.py"
__version = "0.1a"


def main():
    """Main Script. """
    
    print("Running {fname} version {ver}...".format(fname=__name, ver=__version))

    # STEP 0: Setup
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    print("Current view is: '{vname}' of type {vtype}".format(vname=view.Name, vtype=type(view)))
    if type(view) is db.ViewPlan:
        
        # STEP 1: Get all vertical pipes in the view
        print("Getting all pipes from the currently active view...")
        pipes = db.FilteredElementCollector(doc, view.Id)\
                  .OfCategory(db.BuiltInCategory.OST_PipeCurves)\
                  .WhereElementIsNotElementType()\
                  .ToElements()
        print("Found {num} pipes in the currently active view.".format(num=len(pipes)))
        vertical_pipes = [pipe for pipe in pipes if is_vertical(pipe)]
        print("Found {num} vertical pipes in the view.".format(num=len(vertical_pipes)))

        # STEP 2: Filter all pipes crossing upper and lower view range boundary
        top, bottom = top_and_bottom_elevation(doc, view)  
        print("Top boundary elevation is {hf} ft = {hm} m".format(hf=top, hm=top*0.3048))
        print("Bottom boundary elevation is {hf} ft = {hm} m".format(hf=bottom, hm=bottom*0.3048))
        
        upper_pipes = [pipe for pipe in vertical_pipes if cuts_top_only(pipe, top, bottom)]
        lower_pipes = [pipe for pipe in vertical_pipes if cuts_bottom_only(pipe, top, bottom)]
        both_pipes =[pipe for pipe in vertical_pipes if cuts_top_and_bottom(pipe, top, bottom)]
        print("Found {num} pipes crossing upper boundary only.".format(num=len(upper_pipes)))
        print("Found {num} pipes crossing lower boundary only.".format(num=len(lower_pipes)))
        print("Found {num} pipes crossing both boundaries.".format(num=len(both_pipes)))

        # STEP 3: Get all available pipe tags in the project
        tag_types = db.FilteredElementCollector(doc)\
                    .OfCategory(db.BuiltInCategory.OST_PipeTags)\
                    .WhereElementIsElementType()\
                    .ToElements()
        tags = {}  # {tag_title: tag_type}
        for tag_type in tag_types:
            tag_family_name = tag_type.get_Parameter(db.BuiltInParameter.SYMBOL_FAMILY_NAME_PARAM).AsString()
            tag_type_name = tag_type.get_Parameter(db.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
            full_tag_name = "{f_name} - {t_name}".format(f_name=tag_family_name, t_name=tag_type_name)
            tags[full_tag_name] = tag_type

        # STEP 4: Get user selection for pipe riser tags to be applied
        print("Please select the tags to be placed...")
        tag_select_form = TagSelectionForm(tags=tags)
        result = tag_select_form.ShowDialog()
        if result == swf.DialogResult.OK:
            selected_tag_title = tag_select_form.get_selection()
            selected_tag = tags[selected_tag_title]

            # STEP 5: Place tags at the pipes
            print("Creating tags...")
            transaction = db.Transaction(doc)
            transaction.Start("{name} - v{ver}".format(name=__name, ver=__version))
            try:
                for pipe in itertools.chain(upper_pipes, lower_pipes, both_pipes):
                    point = pipe_location(pipe, top)
                    new_tag = db.IndependentTag.Create(doc, view.Id, db.Reference(pipe), False, db.TagMode.TM_ADDBY_CATEGORY, db.TagOrientation.Horizontal, point)
                    new_tag.ChangeTypeId(selected_tag.Id)
            except Exception as ex:
                print("Exception:\n {0}".format(ex))
                transaction.RollBack()
            else:
                transaction.Commit()
                print("Done.")
        else:  # result != swf.DialogResult.OK
            print("No tag selected, nothing to do.")
    else:  # type(view) != dbViewPlan
        print("Currently active view is not a plan view!")
        dialog = ui.TaskDialog(title="Tag Risers in View")
        dialog.MainInstruction = "No plan view selected!"
        dialog.MainContent = "Please make sure to have a plan view active before running this command."
        result = dialog.Show()

# Helpers:
def is_vertical(pipe, tolerance=1.0e-6):
    """Check if a pipe is vertical."""
    assert pipe.ConnectorManager.Connectors.Size == 2
    point1 = pipe.ConnectorManager.Lookup(0).Origin
    point2 = pipe.ConnectorManager.Lookup(1).Origin
    dz = abs(point1.Z - point2.Z)
    if dz > 0:
        dx = abs(point1.X - point2.X)
        dy = abs(point1.X - point2.X)
        if dx < tolerance and dy < tolerance:
            return True
    return False

def top_and_bottom_elevation(doc, view):
    """Extract top and bottom elevation of a plan view."""
    view_range = view.GetViewRange()
    top_plane = view_range.GetLevelId(db.PlanViewPlane.TopClipPlane)
    bottom_plane = view_range.GetLevelId(db.PlanViewPlane.BottomClipPlane)
    top_level = doc.GetElement(top_plane)
    bottom_level = doc.GetElement(bottom_plane)
    top_offset = view_range.GetOffset(db.PlanViewPlane.TopClipPlane)
    bottom_offset = view_range.GetOffset(db.PlanViewPlane.BottomClipPlane)
    top_elevation = top_level.Elevation + top_offset
    bottom_elevation = bottom_level.Elevation + bottom_offset
    assert top_elevation >= bottom_elevation
    return top_elevation, bottom_elevation


def cuts_top_only(pipe, top, bottom):
    """Checks if the pipe only intersects the top elevation."""
    assert pipe.ConnectorManager.Connectors.Size == 2
    point1 = pipe.ConnectorManager.Lookup(0).Origin
    point2 = pipe.ConnectorManager.Lookup(1).Origin
    high = max(point1.Z, point2.Z)
    low = min(point1.Z, point2.Z)
    if high >= top and top >= low >= bottom:
        print("cutting top: high = {hf} ft = {hm} m, low = {lf} ft = {lm} m".format(hf=high, hm=high*0.3048, lf=low, lm=low*0.3048))
        return True
    return False


def cuts_bottom_only(pipe, top, bottom):
    """Checks if the pipe only intersects the botom elevation."""
    assert pipe.ConnectorManager.Connectors.Size == 2
    point1 = pipe.ConnectorManager.Lookup(0).Origin
    point2 = pipe.ConnectorManager.Lookup(1).Origin
    high = max(point1.Z, point2.Z)
    low = min(point1.Z, point2.Z)
    if low <= bottom and bottom <= high <= top:
        print("cutting top: high = {hf} ft = {hm} m, low = {lf} ft = {lm} m".format(hf=high, hm=high*0.3048, lf=low, lm=low*0.3048))
        return True
    return False


def cuts_top_and_bottom(pipe, top, bottom):
    """Checks if the pipe intersects both elevations."""
    assert pipe.ConnectorManager.Connectors.Size == 2
    point1 = pipe.ConnectorManager.Lookup(0).Origin
    point2 = pipe.ConnectorManager.Lookup(1).Origin
    high = max(point1.Z, point2.Z)
    low = min(point1.Z, point2.Z)
    if high >= top and bottom >= low:
        print("cutting top: high = {hf} ft = {hm} m, low = {lf} ft = {lm} m".format(hf=high, hm=high*0.3048, lf=low, lm=low*0.3048))
        return True
    return False


def pipe_location(pipe, elevation):
    """Returns the intersetion point of the pipe with the elevation."""
    curve = pipe.Location.Curve
    pipe_point = curve.GetEndPoint(0)
    point = db.XYZ(pipe_point.X, pipe_point.Y, elevation)
    # print("pipe location = {}".format(point))
    return point


class TagSelectionForm(swf.Form):
    """Link selection form."""

    def __init__(self, tags):
        """Initializer."""
        # Instatiate widgets
        self.gridLayout = swf.TableLayoutPanel()
        self.buttonLayout = swf.FlowLayoutPanel()
        self.labelTag = swf.Label()
        self.comboTag = swf.ComboBox()
        self.buttonCancel = swf.Button()
        self.buttonSelect = swf.Button()
        self.gridLayout.SuspendLayout()
        self.buttonLayout.SuspendLayout()
        self.SuspendLayout()
        # Place widgets and populate them
        self.layout_widgets()
        self.populate_combo_boxes(tags)

    def layout_widgets(self):
        """Layout the widgets."""
        # labelTag
        self.labelTag.Text = "Select Riser Tag:"
        self.labelTag.Anchor = swf.AnchorStyles.Right
        self.labelTag.AutoSize = True
        self.labelTag.Location = sd.Point(54, 13)
        self.labelTag.Size = sd.Size(48, 13)
        # comboBoxTag
        self.comboTag.Anchor = swf.AnchorStyles.Left | swf.AnchorStyles.Right
        self.comboTag.FormattingEnabled = False
        self.comboTag.Location = sd.Point(108, 9)
        self.comboTag.Size = sd.Size(268, 21)
        # buttonCancel
        self.buttonCancel.Text = "Cancel"
        self.buttonCancel.DialogResult = swf.DialogResult.Cancel
        self.buttonCancel.Location = sd.Point(290, 8)
        self.buttonCancel.Size = sd.Size(75, 23)
        self.buttonCancel.UseVisualStyleBackColor = True
        # buttonSelect
        self.buttonSelect.Text = "Select"
        self.buttonSelect.DialogResult = swf.DialogResult.OK
        self.buttonSelect.Location = sd.Point(209, 8)
        self.buttonSelect.Size = sd.Size(75, 23)
        self.buttonSelect.UseVisualStyleBackColor = True
        # buttonLayout
        self.buttonLayout.Dock = swf.DockStyle.Fill
        self.buttonLayout.FlowDirection = swf.FlowDirection.RightToLeft
        self.buttonLayout.Location = sd.Point(8, 98)
        self.buttonLayout.Size = sd.Size(368, 45)
        self.buttonLayout.Padding = swf.Padding(0, 5, 0, 0)
        self.buttonLayout.Controls.Add(self.buttonCancel)
        self.buttonLayout.Controls.Add(self.buttonSelect)
        # gridLayout
        self.gridLayout.Dock = swf.DockStyle.Fill
        self.gridLayout.Location = sd.Point(0, 0)
        self.gridLayout.Size = sd.Size(384, 81)
        self.gridLayout.Padding = swf.Padding(5)
        self.gridLayout.SetColumnSpan(self.buttonLayout, 2)
        self.gridLayout.RowCount = 2
        self.gridLayout.RowStyles.Add(swf.RowStyle(swf.SizeType.Absolute, 30))
        self.gridLayout.RowStyles.Add(swf.RowStyle())
        self.gridLayout.ColumnCount = 2
        self.gridLayout.ColumnStyles.Add(swf.ColumnStyle(swf.SizeType.Absolute, 100))
        self.gridLayout.ColumnStyles.Add(swf.ColumnStyle())
        self.gridLayout.Controls.Add(self.labelTag, 0, 0)
        self.gridLayout.Controls.Add(self.comboTag, 1, 0)
        self.gridLayout.Controls.Add(self.buttonLayout, 1, 1)
        # TagSelectionForm
        self.Text = "TagRisersInView.py - Tag Selection"
        self.AcceptButton = self.buttonSelect
        self.CancelButton = self.buttonCancel
        self.AutoScaleDimensions = sd.SizeF(6, 13)
        self.AutoScaleMode = swf.AutoScaleMode.Font
        self.ClientSize = sd.Size(384, 81)
        self.Controls.Add(self.gridLayout)
        self.KeyPreview = True
        self.MinimumSize = sd.Size(400, 120)
        self.gridLayout.ResumeLayout(False)
        self.gridLayout.PerformLayout()
        self.buttonLayout.ResumeLayout(False)
        self.ResumeLayout(False)
    
    def populate_combo_boxes(self, tags):
        """Populate the combo boxes with tag names."""
        for tag_title in sorted(tags.keys()):  # fill combo box
            self.comboTag.Items.Add(tag_title)
        self.comboTag.SelectedIndex = 0  # preselect first element
    
    def get_selection(self):
        """Return the currently selected item."""
        return self.comboTag.SelectedItem


if __name__ == "__main__":
    # __window__.Hide()
    main()
    # __window__.Close()
