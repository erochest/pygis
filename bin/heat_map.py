#!/usr/bin/env python


"""\
usage: heat_map.py WORKSPACE DATA_FILE
"""


import arcpy


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


def set_colors():
    """This sets the colors for the ranges of values in the table."""


def main():
    arcpy.env.workspace = arcpy.GetParameterAsText(0)
    data_file = arcpy.GetParameterAsText(1)

    z_field = 'dtemp'
    add_xy_data(data_file, z_field)
    set_colors(z_field)


if __name__ == '__main__':
    main()
