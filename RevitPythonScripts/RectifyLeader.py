"""Rectify the leaders of the curently selected tags."""

import clr
clr.AddReference("RevitAPI")
clr.AddReference("RevitAPIUI")
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui

__name = "RectifyLeader.py"
__version = "0.1a"


def main():
	"""Main function."""
	print("Running {fname} version {ver}...".format(fname=__name, ver=__version))

	doc = __revit__.ActiveUIDocument.Document
	uidoc = __revit__.ActiveUIDocument

	sel = uidoc.Selection
	ids = sel.GetElementIds()
	ids = [id for id in ids]
	elems = [doc.GetElement(id) for id in ids]
	print(elems)

	tag = elems[0] if elems else None
	print(tag)
	loc = tag.Location

	trans = db.Transaction(doc)
	trans.Start("{name} - v{ver}".format(name=__name, ver=__version))
	try:
		tag.LeaderEndCondition = db.LeaderEndCondition.Free
		end_loc = tag.LeaderEnd
		tag.LeaderEndCondition = db.LeaderEndCondition.Attached

		elbow_loc = tag.LeaderElbow
		head_loc = tag.TagHeadPosition

		print("loc       =", loc)
		print("end_loc   =", end_loc)
		print("elbow_loc =", elbow_loc)
		print("head_loc  =", head_loc)

		pos1 = db.XYZ(end_loc.X, head_loc.Y, elbow_loc.Z)
		pos2 = db.XYZ(head_loc.X, end_loc.Y, elbow_loc.Z)

		dist1 = elbow_loc.DistanceTo(pos1)
		dist2 = elbow_loc.DistanceTo(pos2)

		print("pos1 =", pos1, " dist1 =", dist1)
		print("pos2 =", pos2, " dist2 =", dist2)

		if dist1 <= dist2:
			tag.LeaderElbow = pos1
		else:
			tag.LeaedrElbow = pos2
	except:
		trans.RollBack()
	else:
		trans.Commit()


if __name__ == "__main__":
	# __window__.Hide()
    main()
    # __window__.Close()
