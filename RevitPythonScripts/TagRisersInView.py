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
        label1 = swf.Label()
        label2 = swf.Label()
        label3 = swf.Label()
        comboBox1 = swf.ComboBox()
        comboBox2 = swf.ComboBox()
        comboBox3 = swf.ComboBox()
        button1 = swf.Button()
        button2 = swf.Button()
        self.SuspendLayout()
        # label1
        label1.AutoSize = True
        label1.Location = sd.Point(12, 15)
        label1.Name = "label1"
        label1.Size = sd.Size(67, 13)
        label1.TabIndex = 2
        label1.Text = "Top pipe tag"
        # label2
        label2.AutoSize = True
        label2.Location = sd.Point(12, 42)
        label2.Name = "label2"
        label2.Size = sd.Size(81, 13)
        label2.TabIndex = 4
        label2.Text = "Bottom pipe tag"
        # label3
        label3.AutoSize = True
        label3.Location = sd.Point(12, 69)
        label3.Name = "label3"
        label3.Size = sd.Size(70, 13)
        label3.TabIndex = 6
        label3.Text = "Both pipe tag"
        # comboBox1
        comboBox1.FormattingEnabled = True
        comboBox1.Location = sd.Point(105, 12)
        comboBox1.Name = "comboBox1"
        comboBox1.Size = sd.Size(250, 21)
        comboBox1.TabIndex = 3
        # comboBox2
        comboBox2.FormattingEnabled = True
        comboBox2.Location = sd.Point(105, 39)
        comboBox2.Name = "comboBox2"
        comboBox2.Size = sd.Size(250, 21)
        comboBox2.TabIndex = 5
        # comboBox3
        comboBox3.DropDownWidth = 250
        comboBox3.FormattingEnabled = True
        comboBox3.Location = sd.Point(105, 66)
        comboBox3.Name = "comboBox3"
        comboBox3.Size = sd.Size(250, 21)
        comboBox3.TabIndex = 7
        
        # button1
        button1.Location = sd.Point(181, 109)
        button1.Name = "button1"
        button1.Size = sd.Size(84, 26)
        button1.TabIndex = 0
        button1.Text = "OK"
        button1.UseVisualStyleBackColor = True
        # button2
        button2.Location = sd.Point(271, 109)
        button2.Name = "button2"
        button2.Size = sd.Size(84, 26)
        button2.TabIndex = 1
        button2.Text = "Cancel"
        button2.UseVisualStyleBackColor = True
        # Form1
        self.AcceptButton = button1
        self.CancelButton = button2
        self.AutoScaleDimensions = sd.SizeF(6, 13)
        self.AutoScaleMode = swf.AutoScaleMode.Font
        #self.AutoSize = True
        #self.AutoSizeMode = swf.AutoSizeMode.GrowAndShrink
        self.ClientSize = sd.Size(365, 147)
        self.Controls.Add(comboBox3)
        self.Controls.Add(label3)
        self.Controls.Add(comboBox2)
        self.Controls.Add(label2)
        self.Controls.Add(comboBox1)
        self.Controls.Add(label1)
        self.Controls.Add(button2)
        self.Controls.Add(button1)
        self.Name = "Form1"
        self.StartPosition = swf.FormStartPosition.CenterParent
        self.Text = "Form1"
        self.ResumeLayout(False)
        self.PerformLayout()


if __name__ == "__main__":
    # __window__.Hide()
    main() 
    # __window__.Close()
