"""Tag vertical risers in current view."""

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
    """Main Script

    This script is tagging all vertical pipe risers in the current view.
    """
    
    print("Running {fname} version {ver}...".format(fname=__name, ver=__version))

    # STEP 0: Setup
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    print("Current view is: '{v}' {t}".format(v=view.Name, t=type(view)))
    if type(view) is db.ViewPlan:
        
        # STEP 1: Get all vertical pipes in the view
        print("Getting all pipes from the currently active view...")
        pipes = db.FilteredElementCollector(doc, view.Id)\
                  .OfCategory(db.BuiltInCategory.OST_PipeCurves)\
                  .ToElements()
        print("Found {num} pipes in the currently active view.".format(num=len(pipes)))
        vertical_pipes = [pipe for pipe in pipes if is_vertical(pipe)]
        print("Found {num} vertical pipes in the view.".format(num=len(vertical_pipes)))

        # STEP 2: Filter all pipes crossing upper and lower view range boundary
        top, bottom = top_and_bottom_elevation(doc, view)  
        print("Top boundary elevation is {0} ft".format(top))
        print("Bottom boundary elevation is {0} ft".format(bottom))
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
        tags = {}  # tag_title: tag_type
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
            selected_top_tag_title = tag_select_form.comboBoxTopTag.SelectedItem
            selected_top_tag = tags[selected_top_tag_title]
            selected_bottom_tag_title = tag_select_form.comboBoxBottomTag.SelectedItem
            selected_bottom_tag = tags[selected_bottom_tag_title]
            selected_both_tag_title = tag_select_form.comboBoxBothTag.SelectedItem
            selected_both_tag = tags[selected_both_tag_title]

            # STEP 5: Place tags at the pipes
            print("Creating tags...")
            transaction = db.Transaction(doc)
            transaction.Start("{name} - v{ver}".format(name=__name, ver=__version))
            try:
                for pipe in upper_pipes:
                    point = pipe_location(pipe, top)
                    new_tag = db.IndependentTag.Create(doc, view.Id, db.Reference(pipe), False, db.TagMode.TM_ADDBY_CATEGORY, db.TagOrientation.Horizontal, point)
                    new_tag.ChangeTypeId(selected_top_tag.Id)
                for pipe in lower_pipes:
                    point = pipe_location(pipe, bottom)
                    new_tag = db.IndependentTag.Create(doc, view.Id, db.Reference(pipe), False, db.TagMode.TM_ADDBY_CATEGORY, db.TagOrientation.Horizontal, point)
                    new_tag.ChangeTypeId(selected_bottom_tag.Id)
                for pipe in both_pipes:
                    point = pipe_location(pipe, top)
                    new_tag = db.IndependentTag.Create(doc, view.Id, db.Reference(pipe), False, db.TagMode.TM_ADDBY_CATEGORY, db.TagOrientation.Horizontal, point)
                    new_tag.ChangeTypeId(selected_both_tag.Id)
            except Exception as ex:
                print("Exception:\n {0}".format(ex))
                transaction.RollBack()
            else:
                transaction.Commit()
                print("Done.")
        else:  # result != swf.DialogResult.OK
            print("No link selected, nothing to do.")
    else:  # type(view) != dbViewPlan
        print("Currently active view is not a plan view!")

# Helpers:
def is_vertical(pipe, tolerance=1.0e-6):
    """Check if a pipe is vertical."""
    curve = pipe.Location.Curve
    start = curve.GetEndPoint(0)
    end = curve.GetEndPoint(1)
    dz = abs(start.Z - end.Z)
    if dz > tolerance:
        dx = abs(start.X - end.X)
        dy = abs(start.X - end.X)
        if dx < tolerance and dy < tolerance:
            return True
    return False


def top_and_bottom_elevation(doc, view):
    """Extract top and bottom elevation of a plan view."""
    view_range = view.GetViewRange()
    # get clip plane ids
    top_plane = view_range.GetLevelId(db.PlanViewPlane.TopClipPlane)
    bottom_plane = view_range.GetLevelId(db.PlanViewPlane.BottomClipPlane)
    # get clip plane levels
    top_level = doc.GetElement(top_plane)
    bottom_level = doc.GetElement(bottom_plane)
    # get clip plane offsets
    top_offset = view_range.GetOffset(db.PlanViewPlane.TopClipPlane)
    bottom_offset = view_range.GetOffset(db.PlanViewPlane.BottomClipPlane)
    # calculate clip plane elevations
    top_elevation = top_level.Elevation + top_offset
    bottom_elevation = bottom_level.Elevation + bottom_offset
    assert top_elevation >= bottom_elevation
    return top_elevation, bottom_elevation


def cuts_top_only(pipe, top, bottom):
    """Checks if the pipe only intersects the top elevation."""
    curve = pipe.Location.Curve
    start = curve.GetEndPoint(0)
    end = curve.GetEndPoint(1)
    high = max(start.Z, end.Z)
    low = min(start.Z, end.Z)
    if high >= top and top >= low >= bottom:
        return True
    return False


def cuts_bottom_only(pipe, top, bottom):
    """Checks if the pipe only intersects the botom elevation."""
    curve = pipe.Location.Curve
    start = curve.GetEndPoint(0)
    end = curve.GetEndPoint(1)
    high = max(start.Z, end.Z)
    low = min(start.Z, end.Z)
    if low <= bottom and bottom <= high <= top:
        return True
    return False


def cuts_top_and_bottom(pipe, top, bottom):
    """Checks if the pipe intersects both elevations."""
    curve = pipe.Location.Curve
    start = curve.GetEndPoint(0)
    end = curve.GetEndPoint(1)
    high = max(start.Z, end.Z)
    low = min(start.Z, end.Z)
    if high >= top and bottom >= low:
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
        self.tableLayoutPanelOverall = swf.TableLayoutPanel()
        self.flowLayoutPanelButtons = swf.FlowLayoutPanel()
        self.labelTopTag = swf.Label()
        self.labelBottomTag = swf.Label()
        self.labelBothTag = swf.Label()
        self.comboBoxTopTag = swf.ComboBox()
        self.comboBoxBottomTag = swf.ComboBox()
        self.comboBoxBothTag = swf.ComboBox()
        self.buttonCancel = swf.Button()
        self.buttonSelect = swf.Button()
        self.tableLayoutPanelOverall.SuspendLayout()
        self.flowLayoutPanelButtons.SuspendLayout()
        self.SuspendLayout()
        # Call layout functions
        self.layout_widgets()
        self.populate_combo_boxes(tags)

    def layout_widgets(self):
        """Layout the widgets."""
        # labelTopTag
        self.labelTopTag.Text = "Top Tag"
        self.labelTopTag.Anchor = swf.AnchorStyles.Right
        self.labelTopTag.AutoSize = True
        self.labelTopTag.Location = sd.Point(54, 13)
        self.labelTopTag.Size = sd.Size(48, 13)
        self.labelTopTag.TabIndex = 0
        # labelBottomTag
        self.labelBottomTag.Text = "Bottom Tag"
        self.labelBottomTag.Anchor = swf.AnchorStyles.Right
        self.labelBottomTag.AutoSize = True
        self.labelBottomTag.Location = sd.Point(40, 43)
        self.labelBottomTag.Size = sd.Size(62, 13)
        self.labelBottomTag.TabIndex = 1
        # labelBothTag
        self.labelBothTag.Text = "Both Tag"
        self.labelBothTag.Anchor = swf.AnchorStyles.Right
        self.labelBothTag.AutoSize = True
        self.labelBothTag.Location = sd.Point(51, 73)
        self.labelBothTag.Size = sd.Size(51, 13)
        self.labelBothTag.TabIndex = 2
        # comboBoxTopTag
        self.comboBoxTopTag.Anchor = swf.AnchorStyles.Left | swf.AnchorStyles.Right
        self.comboBoxTopTag.FormattingEnabled = True
        self.comboBoxTopTag.Location = sd.Point(108, 9)
        self.comboBoxTopTag.Size = sd.Size(268, 21)
        self.comboBoxTopTag.TabIndex = 3
        # comboBoxBottomTag
        self.comboBoxBottomTag.Anchor = swf.AnchorStyles.Left | swf.AnchorStyles.Right
        self.comboBoxBottomTag.FormattingEnabled = True
        self.comboBoxBottomTag.Location = sd.Point(108, 39)
        self.comboBoxBottomTag.Size = sd.Size(268, 21)
        self.comboBoxBottomTag.TabIndex = 4
        # comboBoxBothTag
        self.comboBoxBothTag.Anchor = swf.AnchorStyles.Left | swf.AnchorStyles.Right
        self.comboBoxBothTag.FormattingEnabled = True
        self.comboBoxBothTag.Location = sd.Point(108, 69)
        self.comboBoxBothTag.Size = sd.Size(268, 21)
        self.comboBoxBothTag.TabIndex = 5
        # buttonCancel
        self.buttonCancel.Text = "Cancel"
        self.buttonCancel.DialogResult = swf.DialogResult.Cancel
        self.buttonCancel.Location = sd.Point(290, 8)
        self.buttonCancel.Size = sd.Size(75, 23)
        self.buttonCancel.TabIndex = 0
        self.buttonCancel.UseVisualStyleBackColor = True
        # buttonSelect
        self.buttonSelect.Text = "Select"
        self.buttonSelect.DialogResult = swf.DialogResult.OK
        self.buttonSelect.Location = sd.Point(209, 8)
        self.buttonSelect.Size = sd.Size(75, 23)
        self.buttonSelect.TabIndex = 1
        self.buttonSelect.UseVisualStyleBackColor = True
        # self.buttonSelect.Click += self.buttonSelect_Click
        # flowLayoutPanelButtons
        self.tableLayoutPanelOverall.SetColumnSpan(self.flowLayoutPanelButtons, 2)
        self.flowLayoutPanelButtons.Controls.Add(self.buttonCancel)
        self.flowLayoutPanelButtons.Controls.Add(self.buttonSelect)
        self.flowLayoutPanelButtons.Dock = swf.DockStyle.Fill
        self.flowLayoutPanelButtons.FlowDirection = swf.FlowDirection.RightToLeft
        self.flowLayoutPanelButtons.Location = sd.Point(8, 98)
        self.flowLayoutPanelButtons.Padding = swf.Padding(0, 5, 0, 0)
        self.flowLayoutPanelButtons.Size = sd.Size(368, 45)
        self.flowLayoutPanelButtons.TabIndex = 6
        # tableLayoutPanelOverall
        self.tableLayoutPanelOverall.ColumnCount = 2
        self.tableLayoutPanelOverall.ColumnStyles.Add(swf.ColumnStyle(swf.SizeType.Absolute, 100))
        self.tableLayoutPanelOverall.ColumnStyles.Add(swf.ColumnStyle())
        self.tableLayoutPanelOverall.Controls.Add(self.labelTopTag, 0, 0)
        self.tableLayoutPanelOverall.Controls.Add(self.labelBottomTag, 0, 1)
        self.tableLayoutPanelOverall.Controls.Add(self.labelBothTag, 0, 2)
        self.tableLayoutPanelOverall.Controls.Add(self.comboBoxTopTag, 1, 0)
        self.tableLayoutPanelOverall.Controls.Add(self.comboBoxBottomTag, 1, 1)
        self.tableLayoutPanelOverall.Controls.Add(self.comboBoxBothTag, 1, 2)
        self.tableLayoutPanelOverall.Controls.Add(self.flowLayoutPanelButtons, 1, 3)
        self.tableLayoutPanelOverall.Dock = swf.DockStyle.Fill
        self.tableLayoutPanelOverall.Location = sd.Point(0, 0)
        self.tableLayoutPanelOverall.Padding = swf.Padding(5)
        self.tableLayoutPanelOverall.RowCount = 4
        self.tableLayoutPanelOverall.RowStyles.Add(swf.RowStyle(swf.SizeType.Absolute, 30))
        self.tableLayoutPanelOverall.RowStyles.Add(swf.RowStyle(swf.SizeType.Absolute, 30))
        self.tableLayoutPanelOverall.RowStyles.Add(swf.RowStyle(swf.SizeType.Absolute, 30))
        self.tableLayoutPanelOverall.RowStyles.Add(swf.RowStyle())
        self.tableLayoutPanelOverall.Size = sd.Size(384, 151)
        self.tableLayoutPanelOverall.TabIndex = 0
        # TagSelectionForm
        self.Text = "TagRisersInView.py Tag Selection"
        self.AcceptButton = self.buttonSelect
        self.CancelButton = self.buttonCancel
        self.AutoScaleDimensions = sd.SizeF(6, 13)
        self.AutoScaleMode = swf.AutoScaleMode.Font
        self.ClientSize = sd.Size(384, 151)
        self.Controls.Add(self.tableLayoutPanelOverall)
        self.KeyPreview = True
        self.MinimumSize = sd.Size(400, 190)
        self.tableLayoutPanelOverall.ResumeLayout(False)
        self.tableLayoutPanelOverall.PerformLayout()
        self.flowLayoutPanelButtons.ResumeLayout(False)
        self.ResumeLayout(False)
    
    def populate_combo_boxes(self, tags):
        """Populate the combo boxes with tag names."""
        # Fill combo boxes with tag titles
        for tag_title in sorted(tags.keys()):
            self.comboBoxTopTag.Items.Add(tag_title)
            self.comboBoxBottomTag.Items.Add(tag_title)
            self.comboBoxBothTag.Items.Add(tag_title)
        # Preselect first item in the list
        self.comboBoxTopTag.SelectedIndex = 0
        self.comboBoxBottomTag.SelectedIndex = 0
        self.comboBoxBothTag.SelectedIndex = 0


if __name__ == "__main__":
    # __window__.Hide()
    main()
    # __window__.Close()
