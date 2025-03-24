import arcpy
arcpy.env.workspace = r"C:\Users\paint\Downloads\Admin\Admin\AdminData.gdb"
# yes, it's listed as my downloads folder, I just have it connected to everything in my ArcPro via folder connections. Everything is functional. I accidentally skipped moving some things around when I initially started and just never fixed it.
arcpy.env.overwriteOutput = True
arcpy.SelectLayerByAttribute_management("cities", "CLEAR_SELECTION")

flayer = arcpy.MakeFeatureLayer_management("cities", "Cities_Layer")

qry = "POP1990 > 20000"
arcpy.management.SelectLayerByAttribute(flayer, "NEW_SELECTION", qry)

my_cnt = arcpy.management.GetCount(flayer)
print(f"Selected cities is: {my_cnt}")

arcpy.management.SelectLayerByLocation(flayer, "WITHIN_A_DISTANCE", "us_rivers", "10 miles", "SUBSET_SELECTION")

my_cnt = arcpy.management.GetCount(flayer)
print(f"Selected cities is: {my_cnt}")

field = 'POP1990'
total = 0
i = 1
with arcpy.da.SearchCursor(flayer, field) as cursor:
    for row in cursor:
        print(i, str(row[0]))
        total = total + row[0]
        i = i + 1

print(f"Total population is: {total:,}")
