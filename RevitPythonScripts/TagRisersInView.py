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

    # STEP 1: Get all vertical pipes in the view
    pipes = db.FilteredElementCollector(doc, view.Id)\
              .OfCategory(db.BuiltInCategory.OST_PipeCurves)\
              .ToElements()
    print("Found {num} pipes in the currently active view.".format(num=len(pipes)))
    # print(pipes)
    vertical_pipes = [pipe for pipe in pipes if is_vertical(pipe)]
    print("Found {num} vertical pipes in the view.".format(num=len(vertical_pipes)))
    # print(vertical_pipes)

    # STEP 2: Filter all pipes crossing upper and lower view range boundary
    top, bottom = top_and_bottom_elevation(doc, view)
    print("Top boundary elevation is {0} ft".format(top))
    print("Bottom boundary elevation is {0} ft".format(bottom))

    upper_pipes = [pipe for pipe in vertical_pipes if cuts_top_only(pipe, top, bottom)]
    lower_pipes = [pipe for pipe in vertical_pipes if cuts_bottom_only(pipe, top, bottom)]
    both_pipes =[pipe for pipe in vertical_pipes if cuts_top_and_bottom(pipe, top, bottom)]
    print("Found {num} pipes crossing upper boundary only.".format(num=len(upper_pipes)))
    # print(upper_pipes)
    print("Found {num} pipes crossing lower boundary only.".format(num=len(lower_pipes)))
    # print(lower_pipes)
    print("Found {num} pipes crossing both boundaries.".format(num=len(both_pipes)))
    # print(both_pipes)

    # STEP 3: Get all available pipe tags in the project
    tag_types = db.FilteredElementCollector(doc)\
                  .OfCategory(db.BuiltInCategory.OST_PipeTags)\
                  .WhereElementIsElementType()\
                  .ToElements()
    print(tag_types)
    for tag_type in tag_types:
        tag_id = tag_type.Id
        tag_family_name = tag_type.get_Parameter(db.BuiltInParameter.SYMBOL_FAMILY_NAME_PARAM).AsString()
        tag_type_name = tag_type.get_Parameter(db.BuiltInParameter.SYMBOL_NAME_PARAM).AsString()
        print("#{tag_id} = {f_name} - {t_name}".format(tag_id=tag_id, f_name=tag_family_name, t_name=tag_type_name))

    #TODO STEP 4: Get user selection for pipe riser tags to be applied
    select_form = TagSelectionForm(tags=tag_types)
    select_form.ShowDialog()


    #TODO: STEP 5: Place tags at the pipes
    print("Crating tags...")
    transaction = db.Transaction(doc)
    transaction.Start("{name} - v{ver}".format(name=__name, ver=__version))
    try:
        for pipe in upper_pipes:
            point = pipe_location(pipe, top)
            new_tag = db.IndependentTag.Create(doc, view.Id, db.Reference(pipe), False, db.TagMode.TM_ADDBY_CATEGORY, db.TagOrientation.Horizontal, point)
            #print(new_tag)
            # new_tag.ChangeTypeId(db.ElementId(1096070))  # TODO: get id from user selection
        for pipe in lower_pipes:
            pass  # TODO implement as above
        for pipe in both_pipes:
            pass  # TODO implement as above
    except Exception as ex:
        print("Exception:\n {0}".format(ex))
        transaction.RollBack()
    else:
        transaction.Commit()
        print("Done.")


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
    print("pipe location = {}".format(point))
    return point


# TODO: implement functionality
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
        self.comboBox1 = swf.ComboBox()
        self.comboBox2 = swf.ComboBox()
        self.comboBox3 = swf.ComboBox()
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
        self.labelTopTag.Name = "labelTopTag"
        self.labelTopTag.Text = "Top Tag"
        self.labelTopTag.Anchor = swf.AnchorStyles.Right
        self.labelTopTag.AutoSize = True
        self.labelTopTag.Location = sd.Point(54, 13)
        self.labelTopTag.Size = sd.Size(48, 13)
        self.labelTopTag.TabIndex = 0
        # labelBottomTag
        self.labelBottomTag.Name = "labelBottomTag"
        self.labelBottomTag.Text = "Bottom Tag"
        self.labelBottomTag.Anchor = swf.AnchorStyles.Right
        self.labelBottomTag.AutoSize = True
        self.labelBottomTag.Location = sd.Point(40, 43)
        self.labelBottomTag.Size = sd.Size(62, 13)
        self.labelBottomTag.TabIndex = 1
        # labelBothTag
        self.labelBothTag.Name = "labelBothTag"
        self.labelBothTag.Text = "Both Tag"
        self.labelBothTag.Anchor = swf.AnchorStyles.Right
        self.labelBothTag.AutoSize = True
        self.labelBothTag.Location = sd.Point(51, 73)
        self.labelBothTag.Size = sd.Size(51, 13)
        self.labelBothTag.TabIndex = 2
        # comboBox1
        self.comboBox1.Name = "comboBox1"
        self.comboBox1.Anchor = swf.AnchorStyles.Left | swf.AnchorStyles.Right
        self.comboBox1.FormattingEnabled = True
        self.comboBox1.Location = sd.Point(108, 9)
        self.comboBox1.Size = sd.Size(268, 21)
        self.comboBox1.TabIndex = 3
        # comboBox2
        self.comboBox2.Name = "comboBox2"
        self.comboBox2.Anchor = swf.AnchorStyles.Left | swf.AnchorStyles.Right
        self.comboBox2.FormattingEnabled = True
        self.comboBox2.Location = sd.Point(108, 39)
        self.comboBox2.Size = sd.Size(268, 21)
        self.comboBox2.TabIndex = 4
        # comboBox3
        self.comboBox3.Name = "comboBox3"
        self.comboBox3.Anchor = swf.AnchorStyles.Left | swf.AnchorStyles.Right
        self.comboBox3.FormattingEnabled = True
        self.comboBox3.Location = sd.Point(108, 69)
        self.comboBox3.Size = sd.Size(268, 21)
        self.comboBox3.TabIndex = 5
        # buttonCancel
        self.buttonCancel.Name = "buttonCancel"
        self.buttonCancel.Text = "Cancel"
        self.buttonCancel.DialogResult = swf.DialogResult.Cancel
        self.buttonCancel.Location = sd.Point(290, 8)
        self.buttonCancel.Size = sd.Size(75, 23)
        self.buttonCancel.TabIndex = 0
        self.buttonCancel.UseVisualStyleBackColor = True
        # buttonSelect
        self.buttonSelect.Name = "buttonSelect"
        self.buttonSelect.Text = "Select"
        self.buttonSelect.DialogResult = swf.DialogResult.OK
        self.buttonSelect.Location = sd.Point(209, 8)
        self.buttonSelect.Size = sd.Size(75, 23)
        self.buttonSelect.TabIndex = 1
        self.buttonSelect.UseVisualStyleBackColor = True
        # self.buttonSelect.Click += self.buttonSelect_Click
        # flowLayoutPanelButtons
        self.flowLayoutPanelButtons.Name = "flowLayoutPanelButtons"
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
        self.tableLayoutPanelOverall.Name = "tableLayoutPanelOverall"
        self.tableLayoutPanelOverall.ColumnCount = 2
        self.tableLayoutPanelOverall.ColumnStyles.Add(swf.ColumnStyle(swf.SizeType.Absolute, 100))
        self.tableLayoutPanelOverall.ColumnStyles.Add(swf.ColumnStyle())
        self.tableLayoutPanelOverall.Controls.Add(self.labelTopTag, 0, 0)
        self.tableLayoutPanelOverall.Controls.Add(self.labelBottomTag, 0, 1)
        self.tableLayoutPanelOverall.Controls.Add(self.labelBothTag, 0, 2)
        self.tableLayoutPanelOverall.Controls.Add(self.comboBox1, 1, 0)
        self.tableLayoutPanelOverall.Controls.Add(self.comboBox2, 1, 1)
        self.tableLayoutPanelOverall.Controls.Add(self.comboBox3, 1, 2)
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
        self.Name = "TagSelectionForm"
        self.Text = "TagRisersInView Form"
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
        pass


if __name__ == "__main__":
    # __window__.Hide()
    main()
    # __window__.Close()
