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
    select_form.ShowDialog()

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
        """Initializer."""
        cmb_selection = swf.ComboBox()
        btn_select = swf.Button()
        btn_cancel = swf.Button()
        lbl_instruction = swf.Label()
        self.SuspendLayout()
        # Instruction label
        lbl_instruction.AutoSize = True
        lbl_instruction.Enabled = False
        lbl_instruction.Location = sd.Point(12, 10)
        lbl_instruction.Name = "LblInstruction"
        lbl_instruction.Size = sd.Size(229, 13)
        lbl_instruction.TabIndex = 3
        lbl_instruction.Text = "Select a linked model to use for copying rooms."
        # Selection combo box
        cmb_selection.FormattingEnabled = True
        cmb_selection.Location = sd.Point(12, 40)
        cmb_selection.Name = "CmbSelection"
        cmb_selection.Size = sd.Size(260, 21)
        cmb_selection.TabIndex = 0
        # Select button
        btn_select.Location = sd.Point(110, 80)
        btn_select.Name = "BtnSelect"
        btn_select.Size = sd.Size(75, 23)
        btn_select.TabIndex = 1
        btn_select.Text = "Select"
        btn_select.UseVisualStyleBackColor = True
        # Cancel button
        btn_cancel.DialogResult = swf.DialogResult.Cancel
        btn_cancel.Location = sd.Point(200, 80)
        btn_cancel.Name = "BtnCancel"
        btn_cancel.Size = sd.Size(75, 23)
        btn_cancel.TabIndex = 2
        btn_cancel.Text = "Cancel"
        btn_cancel.UseVisualStyleBackColor = True
        # Form
        self.AcceptButton = btn_select
        self.AutoScaleDimensions = sd.SizeF(6, 13)
        self.AutoScaleMode = swf.AutoScaleMode.Font
        self.CancelButton = btn_cancel
        self.ClientSize = sd.Size(284, 111)
        self.Controls.Add(lbl_instruction)
        self.Controls.Add(btn_cancel)
        self.Controls.Add(btn_select)
        self.Controls.Add(cmb_selection)
        self.Name = "Form1"
        self.Text = "Select Link"
        self.ResumeLayout(False)
        self.PerformLayout()


if __name__ == "__main__":
    #__window__.Hide()
    main()
    #__window__.Close()
