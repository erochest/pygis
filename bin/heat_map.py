#!/usr/bin/env python


"""\
usage: heat_map.py WORKSPACE DATA_FILE SYMBOLOGY_LAYER
"""


import arcpy
import os


def add_xy_data(data_file, z_field='dtemp'):
    """Adds the XY data to the current file."""
    arcpy.MakeXYEventLayer_management(
        data_file,      # table
        'lon',          # x
        'lat',          # y
        z_field,        # output layer
        "WGS 1984",     # spatial reference
        z_field,        # z
        )


def set_colors(input_layer, symbology_layer):
    """This sets the colors for the ranges of values in the table."""
    arcpy.ApplySymbologyFromLayer_management(input_layer, symbology_layer)

def idw(input_layer, z_field):
    """Performs the IDW analysis. Returns the output layer."""
    output = z_field + '_idw'
    arcpy.IDW_ga(input_layer, z_field, output)
    return output


def main():
    arcpy.CheckOutExtension("GeoStats")

    arcpy.env.workspace = arcpy.GetParameterAsText(0)
    data_file = arcpy.GetParameterAsText(1)
    symbology_layer = arcpy.GetParameterAsText(2)

    z_field = 'dtemp'

    add_xy_data(data_file, z_field)
    set_colors(z_field, symbology_layer)
    idw_output = idw(z_field, z_field)

    output_file = idw_output + '.lyr'
    if os.path.exists(output_file):
        os.remove(output_file)

    print('Saving output to {}'.format(output_file))
    arcpy.SaveToLayerFile_management(idw_output, output_file)


if __name__ == '__main__':
    main()
