"""Query the Survey Point and the Project Base Point and get the translation
and rotation.
"""

from __future__ import print_function
import math
import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
import Autodesk.Revit.DB as db
import Autodesk.Revit.UI as ui

__name = "GetSurveyAndBasePoints.py"
__version = "0.1a"

# Constants
FEET_TO_METER = 0.3048  # feet/meter
RADIANS_TO_DEGREE = 180 / math.pi  # rad/°


def main():
    """Main script."""
    
    print("🐍 Running {name} version {ver}:".format(name=__name, ver=__version))

    # STEP 0: Setup
    app = __revit__.Application
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    view = doc.ActiveView

    # STEP 1: Get the Survey Point
    survey = db.FilteredElementCollector(doc)\
                     .OfCategory(db.BuiltInCategory.OST_SharedBasePoint)\
                     .ToElements()[0]  # assume there is only one!

    s_lat = survey.get_Parameter(db.BuiltInParameter.BASEPOINT_LATITUDE_PARAM).AsDouble()
    s_lon = survey.get_Parameter(db.BuiltInParameter.BASEPOINT_LONGITUDE_PARAM).AsDouble()
    s_ns = survey.get_Parameter(db.BuiltInParameter.BASEPOINT_NORTHSOUTH_PARAM).AsDouble()
    s_ew = survey.get_Parameter(db.BuiltInParameter.BASEPOINT_EASTWEST_PARAM).AsDouble()
    s_elev = survey.get_Parameter(db.BuiltInParameter.BASEPOINT_ELEVATION_PARAM).AsDouble()

    print("Survey Point:")
    print("Latitude  =", s_lat)
    print("Longitude =", s_lon)
    print("N/S       =", s_ns, "ft (=", s_ns*FEET_TO_METER, "m)")
    print("E/W       =", s_ew, "ft (=", s_ew*FEET_TO_METER, "m)")
    print("Elevation =", s_elev, "ft (=", s_elev*FEET_TO_METER, "m)")
    print()

    # STEP 2: Get the Project Base Point
    project_base = db.FilteredElementCollector(doc)\
                     .OfCategory(db.BuiltInCategory.OST_ProjectBasePoint)\
                     .ToElements()[0]  # assume there is only one!

    ns = project_base.get_Parameter(db.BuiltInParameter.BASEPOINT_NORTHSOUTH_PARAM).AsDouble()
    ew = project_base.get_Parameter(db.BuiltInParameter.BASEPOINT_EASTWEST_PARAM).AsDouble()
    elev = project_base.get_Parameter(db.BuiltInParameter.BASEPOINT_ELEVATION_PARAM).AsDouble()
    angle = project_base.get_Parameter(db.BuiltInParameter.BASEPOINT_ANGLETON_PARAM).AsDouble()

    print("Project Base Point:")
    print("N/S       =", ns, "ft (=", ns*FEET_TO_METER, "m)")
    print("E/W       =", ew, "ft (=", ew*FEET_TO_METER, "m)")
    print("Elevation =", elev, "ft (=", elev*FEET_TO_METER, "m)")
    print("Angle     =", angle, "rad (=", angle*RADIANS_TO_DEGREE, "°)")
    print()

    transform = doc.ActiveProjectLocation.GetTransform()
    total_transform = doc.ActiveProjectLocation.GetTotalTransform()
    print("Transformation:")
    print("Transform =", transform)
    print("Total Transform =", total_transform)

    print("✔\nDone. 😊")


if __name__ == "__main__":
    # __window__.Hide()
    main()
    # __window__.Close()
