import arcpy
from arcpy.sa import *
import numpy as np
input_cities_file = arcpy.GetParameterAsText(0)
input_raster_file =arcpy.GetParameterAsText(1)
input_boundaries_file =arcpy.GetParameterAsText(2)
workspace = arcpy.GetParameterAsText(4)
field =arcpy.GetParameterAsText(3)

arcpy.CreateFeatureclass_management(str(workspace),'us_cities_level_3',"POINT", spatial_reference = input_cities_file)

output_raster_file = str(workspace) +"\\"+"Raster_NAD.tif"
arcpy.AddMessage(str(output_raster_file))
arcpy.MakeFeatureLayer_management(input_cities_file, 'input_cities_file')
big_cities = arcpy.SelectLayerByAttribute_management('input_cities_file', "NEW_SELECTION",'"POPCLASS"'+">="+ '3' )
cursor = arcpy.da.SearchCursor(big_cities, "SHAPE@")
arrayVal = []
for i in cursor:
	arrayVal.append(i)
del cursor
incursor = arcpy.da.InsertCursor(str(workspace)+'\\'+'us_cities_level_3.shp.', "SHAPE")
for i in arrayVal:
	incursor.insertRow(i)
del incursor

arcpy.AddField_management(str(workspace)+'\\'+'us_cities_level_3.shp', "TEMPER", "TEXT")
arcpy.AddField_management(str(workspace)+'\\'+'us_cities_level_3.shp', "EXCESS", "TEXT")
arcpy.ProjectRaster_management(input_raster_file, output_raster_file, input_cities_file, geographic_transform = "WGS_1984_(ITRF00)_To_NAD_1983")
#clipped_raster = ExtractByMask(output_raster_file, input_boundaries_file)
#clip_path = str(workspace)+'\\'+str(arcpy.Describe(output_raster_file).baseName)+"_extract_by_mask"+".tif"
 
cursor = arcpy.da.SearchCursor(big_cities, "SHAPE@XY")
list_of_temperature  = []
for i in cursor:
	res = arcpy.GetCellValue_management(input_raster_file,str(i[0][0])+" "+str(i[0][1]))
	val=float(str(res.getOutput(0)).replace(",", "."))
	list_of_temperature.append(float(val))
del cursor
excess = map(lambda i: (i - np.mean(list_of_temperature)), list_of_temperature)
with arcpy.da.UpdateCursor(str(workspace)+'\\'+'us_cities_level_3.shp',("TEMPER", "EXCESS")) as incursor:
	arcpy.AddMessage(str(list_of_temperature))
	i=0
	for row in incursor:
		val = (str(list_of_temperature[i]), str(excess[i]))
		incursor.updateRow(val)
		i+=1
	
	
del incursor



                                  
