import clr
clr.AddReference("RevitAPI")
import Autodesk.Revit.DB as db
import math
import collections


def main():
	"""Main script."""
	print("Running SmokeExtractAirflows.py script...")

	# Step 0: Setup
	normal_airflow_m3hm2 = 25.0  # m³/(h*m²)
	raised_airflow_m3hm2 = 36.0  # m³/(h*m²)
	doc = __revit__.ActiveUIDocument.Document

	# Step 1: Collect all spaces from the model
	print("Collecting all spaces from the model...")
	collector = db.FilteredElementCollector(doc)
	spaces = collector.OfCategory(db.BuiltInCategory.OST_MEPSpaces)\
					.WhereElementIsNotElementType()\
					.ToElements()
	print("Found {0} spaces".format(spaces.Count))

	# Step 2: Calculate smoke extract airflows according to smoke extract strategy
	print("Calculating smoke extract airflow according to strategy...")
	space_airflows = []
	for space in spaces:
		strategy = space.GetParameters("BH Entrauchungsstrategie")[0].AsString()
		print("Space #{0}: {1} - {2} -> {3}".format(
			space.Id.IntegerValue,
			space.GetParameters("Raumnummer")[0].AsString(),
			space.GetParameters("Raumbezeichnung")[0].AsString(),
			strategy))
		airflow_m3h = 0.0
		airflow_ft3s = 0.0
		if strategy:
			if "MRA" in strategy:
				area_ft2 = space.get_Parameter(db.BuiltInParameter.ROOM_AREA)\
								.AsDouble()
				area_m2 = to_square_meters(area_ft2)
				print("    Area = {0} ft² = {1} m²".format(area_ft2, area_m2))
				if "25 m³/h/m²" in strategy:
					airflow_m3h = round_up(normal_airflow_m3hm2 * area_m2)
					airflow_ft3s = to_cubic_feet_per_second(airflow_m3h)
				elif "36 m³/h/m²" in strategy:
					airflow_m3h = round_up(raised_airflow_m3hm2 * area_m2)
					airflow_ft3s = to_cubic_feet_per_second(airflow_m3h)
				print("    Airflow = {0} ft³/s ) {1} m³/h".format(
					airflow_ft3s, airflow_m3h))
		pair = SpaceAirflowPair(space, airflow_ft3s)
		space_airflows.append(pair)

	# Step 3: Set Smoke Extract Airflows
	print("Setting Smoke Extract Ariflows on Spaces...")
	transaction = db.Transaction(doc)
	transaction.Start("SmokeExtractAirflows.py")
	try:
		for space, airflow in space_airflows:
			airflow_param = space.get_Parameter(
				db.BuiltInParameter.ROOM_DESIGN_EXHAUST_AIRFLOW_PARAM)
			airflow_param.Set(airflow)
	except Exception as ex:
		print("An exception occurred:")
		print(ex)
		transaction.RollBack()
	else:
		print("Done.")
		transaction.Commit()


# Helpers:

SpaceAirflowPair = collections.namedtuple(
	"SpaceAirflowPair", ["space", "airflow"])

def round_up(number, precision=10.0):
	"""Round a number up to the given precision.

	Precision =   1.0 means 12345.6 gets rounded to 12346,
	precision =  10.0 means 12345.6 gets rounded to 12350,
	precision = 100.0 means 12345.6 gets rounded to 12400,
	and so on.
	"""
	return math.ceil(number / precision) * precision

# Constants for unit conversions
FOOT_TO_METER_FACTOR = 0.3048
METER_TO_FOOT_FACTOR = 1.0 / FOOT_TO_METER_FACTOR
HOUR_TO_SECOND_FACTOR = 3600.0
SECOND_TO_HOUR_FACTOR = 1.0 / HOUR_TO_SECOND_FACTOR

def to_meters(feet):
	"""Convert a value in feet to meters."""
	return feet * FOOT_TO_METER_FACTOR

def to_feet(meters):
	"""Convert a value in meters to feet."""
	return meters / FOOT_TO_METER_FACTOR

def to_square_meters(square_feet):
	"""Convert a value in square feet to square meters."""
	return square_feet * FOOT_TO_METER_FACTOR**2

def to_square_feet(square_meters):
	"""Convert a value in square meters to square feet."""
	return square_meters / FOOT_TO_METER_FACTOR**2

def to_cubic_meters_per_hour(cubic_feet_per_second):
	"""Convert a value in cubic feet per second to cubic meters per hour."""
	return cubic_feet_per_second * FOOT_TO_METER_FACTOR**3 / SECOND_TO_HOUR_FACTOR

def to_cubic_feet_per_second(cubic_meters_per_hour):
	"""Convert a value in cubic meters per hour to cubic feet per second."""
	return cubic_meters_per_hour / FOOT_TO_METER_FACTOR**3 * SECOND_TO_HOUR_FACTOR


if __name__ == "__main__":
	main()
