"""Color all pipe tags based on the color of the host's pipe system type."""
# TODO: add reset overrides to all tags to make color changes possible

import clr
clr.AddReference("RevitAPI")
import Autodesk.Revit.DB as db

__name = "ColorRiserTags.py"
__version = "0.1a"


def main():
	"""Main script."""

	print("Running {fname} version {ver}...".format(fname=__name, ver=__version))

	# STEP 0: Setup
	doc = __revit__.ActiveUIDocument.Document
	view = doc.ActiveView

	# STEP 1: Get all the tags in the view
	tags = db.FilteredElementCollector(doc, view.Id)\
				.OfCategory(db.BuiltInCategory.OST_PipeTags)\
				.WhereElementIsNotElementType()\
				.ToElements()
	#print(tags)

	# STEP 2: Override tag color based on host system type color
	transaction = db.Transaction(doc)
	transaction.Start("{name} - v{ver}".format(name=__name, ver=__version))
	try:
		for tag in tags:
			host = tag.GetTaggedLocalElement()
			system = host.MEPSystem
			system_type = doc.GetElement(system.GetTypeId())
			color = system_type.LineColor
			override = db.OverrideGraphicSettings()
			override.SetProjectionLineColor(color)
			view.SetElementOverrides(tag.Id, override)
	except Exception as ex:
		print(ex)
		transaction.RollBack()
	else:
		transaction.Commit()
		print("Done.")


if __name__ == "__main__":
	__window__.Hide()
	main()
	__window__.Close()
