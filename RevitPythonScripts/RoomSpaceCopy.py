"""Create Spaces from linked Rooms."""

import sys
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")
import System.Windows.Forms as swf
import System.Drawing as sd

__name = "RoomSpaceCopy.py"
__version = "0.1a"


def main():
    """Main Script."""

    print("Running {fname} version {ver}...".format(fname=__name, ver=__version))

    #important vars, revit python shell version
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # Get all links in the revit model
    linked_docs = []
    for document in app.Documents:
        if document.IsLinked:
            linked_docs.append(document)

    # print("Linked Documents:")
    # print(linked_docs)
    # for item in linked_docs:
    #     print(item)
    #     print("{0}: {1}".format(item.Title, item.PathName))

    # TODO: implement user selection of the document
    select_form = LinkSelectionForm(links=linked_docs)
    result = select_form.ShowDialog()
    print(result)
    if result == swf.DialogResult.OK:
        # TODO: get selected  link and carry on
        pass
    else:
        print("No link selected, nothing to do.")

    # Select the link to copy rooms from
    link = linked_docs[0]
    print("Selected Link: {}".format(link.Title))

    # Get all Rooms from the selected link
    rooms = db.FilteredElementCollector(link)\
            .OfCategory(db.BuiltInCategory.OST_Rooms)\
            .ToElements()

    # print("Linked Rooms:")
    # for room in rooms:
    #     print(room)
    print("Found {0} rooms in the linked document".format(len(rooms)))

    # # Get linked Levels:
    # linked_levels = db.FilteredElementCollector(link)\
    #                 .OfCategory(db.BuiltInCategory.OST_Levels)\
    #                 .WhereElementIsNotElementType()\
    #                 .ToElements()

    # print("Linked Levels:")
    # for level in linked_levels:
    #     print(level, level.Name, level.Elevation)
    # print("Total = {0} linked levels".format(len(linked_levels)))

    # Get Levels:
    levels = db.FilteredElementCollector(doc)\
            .OfCategory(db.BuiltInCategory.OST_Levels)\
            .WhereElementIsNotElementType()\
            .ToElements()

    # print("Levels:")
    # for level in levels:
    #     print(level, level.Name, level.Elevation)
    print("Found {0} levels in the model.".format(len(levels)))

    # Create Spaces for all placed Rooms in the selected link
    print("Creating spaces for placed rooms in the selected link..")
    transaction = db.Transaction(doc)
    transaction.Start("{name} - v{ver}".format(name=__name, ver=__version))
    try:
        created_spaces = []
        for room in rooms:
            space_level = find_closest_level(levels, room.Level.Elevation)
            if room.Location:  # room is actually placed
                location_point = room.Location.Point
                insert_point = db.UV(location_point.X, location_point.Y)
                created_space = doc.Create.NewSpace(space_level, insert_point)
                created_spaces.append(created_space)
                # Save unique ID of source room in space parameter "Comments"
                comment_param = created_space.get_Parameter(
                    db.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
                comment_param.Set(room.UniqueId)
        print("Created {0} spaces.".format(len(created_spaces)))

    except Exception as ex:
        print("Exception: {0}".format(ex))
        transaction.RollBack()
    else:
        transaction.Commit()
        print("Done.")

def find_closest_level(levels, elevation):
    """Find the level closest to the given elevation. """
    closest = None
    difference = float("inf")
    for level in levels:
        level_difference = abs(level.Elevation - elevation)
        if level_difference < difference:
            closest = level
            difference = level_difference
    return closest


# TODO: implement functionality
class LinkSelectionForm(swf.Form):
    """Link selection form."""

    def __init__(self, links):
        self.tableLayoutOverall = swf.TableLayoutPanel()
        self.labelLink = swf.Label()
        self.comboBoxLink = swf.ComboBox()
        self.flowLayoutPanelButtons = swf.FlowLayoutPanel()
        self.buttonSelect = swf.Button()
        self.buttonCancel = swf.Button()
        self.tableLayoutOverall.SuspendLayout()
        self.flowLayoutPanelButtons.SuspendLayout()
        self.SuspendLayout()
        # labelLink
        self.labelLink.Anchor = swf.AnchorStyles.Right
        self.labelLink.AutoSize = True
        self.labelLink.Location = sd.Point(25, 18)
        self.labelLink.Name = "labelLink"
        self.labelLink.Size = sd.Size(27, 13)
        self.labelLink.TabIndex = 0
        self.labelLink.Text = "Link"
        # comboBoxLink
        self.comboBoxLink.Anchor = swf.AnchorStyles.Left | swf.AnchorStyles.Right
        self.comboBoxLink.FormattingEnabled = True
        self.comboBoxLink.Location = sd.Point(58, 14)
        self.comboBoxLink.Name = "comboBoxLink"
        self.comboBoxLink.Size = sd.Size(258, 21)
        self.comboBoxLink.TabIndex = 1
        # buttonSelect
        self.buttonSelect.Location = sd.Point(149, 3)
        self.buttonSelect.Name = "buttonSelect"
        self.buttonSelect.Size = sd.Size(75, 23)
        self.buttonSelect.TabIndex = 0
        self.buttonSelect.Text = "Select"
        self.buttonSelect.UseVisualStyleBackColor = True
        self.buttonSelect.Click += self.buttonSelect_Click
        # buttonCancel
        self.buttonCancel.Anchor = swf.AnchorStyles.None
        self.buttonCancel.DialogResult = swf.DialogResult.Cancel
        self.buttonCancel.Location = sd.Point(230, 3)
        self.buttonCancel.Name = "buttonCancel"
        self.buttonCancel.Size = sd.Size(75, 23)
        self.buttonCancel.TabIndex = 1
        self.buttonCancel.Text = "Cancel"
        self.buttonCancel.UseVisualStyleBackColor = True
        # flowLayoutPanelButtons
        self.flowLayoutPanelButtons.BackColor = sd.SystemColors.Control
        self.tableLayoutOverall.SetColumnSpan(self.flowLayoutPanelButtons, 2)
        self.flowLayoutPanelButtons.Controls.Add(self.buttonCancel)
        self.flowLayoutPanelButtons.Controls.Add(self.buttonSelect)
        self.flowLayoutPanelButtons.Dock = swf.DockStyle.Fill
        self.flowLayoutPanelButtons.FlowDirection = swf.FlowDirection.RightToLeft
        self.flowLayoutPanelButtons.Location = sd.Point(8, 48)
        self.flowLayoutPanelButtons.Name = "flowLayoutPanelButtons"
        self.flowLayoutPanelButtons.Size = sd.Size(308, 35)
        self.flowLayoutPanelButtons.TabIndex = 2
        # tableLayoutOverall
        self.tableLayoutOverall.ColumnCount = 2
        self.tableLayoutOverall.ColumnStyles.Add(swf.ColumnStyle(swf.SizeType.Absolute, 50))
        self.tableLayoutOverall.ColumnStyles.Add(swf.ColumnStyle())
        self.tableLayoutOverall.Controls.Add(self.labelLink, 0, 0)
        self.tableLayoutOverall.Controls.Add(self.comboBoxLink, 1, 0)
        self.tableLayoutOverall.Controls.Add(self.flowLayoutPanelButtons, 0, 1)
        self.tableLayoutOverall.Dock = swf.DockStyle.Fill
        self.tableLayoutOverall.Location = sd.Point(0, 0)
        self.tableLayoutOverall.Name = "tableLayoutOverall"
        self.tableLayoutOverall.Padding = swf.Padding(5)
        self.tableLayoutOverall.RowCount = 2
        self.tableLayoutOverall.RowStyles.Add(swf.RowStyle(swf.SizeType.Percent, 50))
        self.tableLayoutOverall.RowStyles.Add(swf.RowStyle(swf.SizeType.Percent, 50))
        self.tableLayoutOverall.Size = sd.Size(324, 91)
        self.tableLayoutOverall.TabIndex = 0
        # RoomSpaceCopyForm
        self.AcceptButton = self.buttonSelect
        self.AutoScaleDimensions = sd.SizeF(6, 13)
        self.AutoScaleMode = swf.AutoScaleMode.Font
        self.CancelButton = self.buttonCancel
        self.ClientSize = sd.Size(324, 91)
        self.Controls.Add(self.tableLayoutOverall)
        self.MaximizeBox = False
        self.MinimizeBox = False
        self.MinimumSize = sd.Size(340, 130)
        self.Name = "RoomSpaceCopyForm"
        self.Text = "RoomSpaceCopyForm"
        self.tableLayoutOverall.ResumeLayout(False)
        self.tableLayoutOverall.PerformLayout()
        self.flowLayoutPanelButtons.ResumeLayout(False)
        self.ResumeLayout(False)
        # TODO: populate comboBox
    
    def buttonSelect_Click(self, sender, args):
        print("Select clicked!")
        self.DialogResult = swf.DialogResult.OK
        self.Close()
    
    def buttonCancel_Click(self, sender, args):
        print("Cancel clicked!")
        self.DialogResult = swf.DialogResult.Cancel
        self.Close()


if __name__ == "__main__":
    #__window__.Hide()
    main()
    #__window__.Close()
