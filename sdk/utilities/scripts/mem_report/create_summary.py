#########################################################################################
# Copyright (C) 2016. Dialog Semiconductor, unpublished work. This computer
# program includes Confidential, Proprietary Information and is a Trade Secret of
# Dialog Semiconductor.  All use, disclosure, and/or reproduction is prohibited
# unless authorized in writing. All Rights Reserved.
#########################################################################################

import sys
import os
import map_reader
import xlxcreator


def get_prj_names(full_path):
    c = os.path.basename(os.path.dirname(full_path))
    p = os.path.splitext(os.path.basename(full_path))[0]
    return p, c


def adjust_maximum_name_size(current_maximum_name_size, name):
    return max(current_maximum_name_size, len(name))


def get_summary_sizes(map_file):
    section_data = map_reader.generate_report(map_file)
    otp_size = sum([int(section_data[sec]["size"], 16) for sec in section_data
                    if 0x7fc0000 > int(section_data[sec]["address"], 16) >= 0x7f80000])
    qspi_size = sum([int(section_data[sec]["size"], 16) for sec in section_data
                     if 0xBF00000 > int(section_data[sec]["address"], 16) >= 0x8000000])
    ram_size = sum([int(section_data[sec]["size"], 16) for sec in section_data
                    if 0x7fe0000 > int(section_data[sec]["address"], 16) >= 0x7fc0000])
    cache_ram_size = sum([int(section_data[sec]["size"], 16) for sec in section_data
                          if 0x8000000 > int(section_data[sec]["address"], 16) >= 0x7fe0000])
    retained_size = sum([int(section_data[sec]["size"], 16) for sec in section_data if "RETENTION" in sec])

    if os.path.isfile(map_file[:-4] + '.bin'):
        bin_size = os.stat(map_file[:-4] + '.bin').st_size
    else:
        print "WARNING: " + map_file[:-4] + '.bin' + " does not exist"
        bin_size = 0
    return otp_size, qspi_size, ram_size, cache_ram_size, retained_size, bin_size


search_path = os.path.abspath(sys.argv[1])
report_name = sys.argv[2]

# Start Excel file creation
E = xlxcreator.XLwithXlswriter(report_name)

# Create Main worksheet
E.create_sheet("Projects Summary")

# Write main title
title_data = [["Project", "Configuration", "OTP size", "QSPI size", "RAM size",
               "Cache RAM size", "Retained RAM size", "Bin file size"]]
E.write_worksheet("Projects Summary", 0, 0, title_data, "main row title")

maximum_prj_name_size = len(title_data[0][0])
maximum_cfg_name_size = len(title_data[0][1])

# Write data
active_row = 1
for root, dirs, files in os.walk(search_path):
    for f in files:
        if f.endswith(".map"):
            project, configuration = get_prj_names(os.path.join(root, f))
            maximum_prj_name_size = adjust_maximum_name_size(maximum_prj_name_size, project)
            maximum_cfg_name_size = adjust_maximum_name_size(maximum_cfg_name_size, configuration)
            E.write_worksheet("Projects Summary", active_row, 0, [[project]], "main column title")
            E.write_worksheet("Projects Summary", active_row, 1, [[configuration]], "main column title")
            otp, qspi, ram, cram, ret, bins = get_summary_sizes(os.path.join(root, f))
            E.write_worksheet("Projects Summary", active_row, 2, [[otp, qspi, ram, cram, ret, bins]], "data")
            active_row += 1

# Set column widths
E.set_column("Projects Summary", 0, maximum_prj_name_size + 2)
E.set_column("Projects Summary", 1, maximum_cfg_name_size + 2)
E.set_column("Projects Summary", 2, len(title_data[0][2]) + 2)
E.set_column("Projects Summary", 3, len(title_data[0][3]) + 2)
E.set_column("Projects Summary", 4, len(title_data[0][4]) + 2)
E.set_column("Projects Summary", 5, len(title_data[0][5]) + 2)
E.set_column("Projects Summary", 6, len(title_data[0][6]) + 2)
E.set_column("Projects Summary", 7, len(title_data[0][7]) + 2)

# Add an auto-filter in project name column to allow filtering out some
E.add_drop_down_selector("Projects Summary", 0, 0, active_row - 1, 0)

# Add comments
E.add_comment("Projects Summary", 0, 2, "The sum of sizes of sections within the OTP memory region.")
E.add_comment("Projects Summary", 0, 3, "The sum of sizes of sections within the QSPI memory region.")
E.add_comment("Projects Summary", 0, 4, "The sum of sizes of sections within the RAM memory region.")
E.add_comment("Projects Summary", 0, 5, "The sum of sizes of sections within the Cache RAM memory region.")
E.add_comment("Projects Summary", 0, 6, "The sum of sizes of sections  that end up in retained RAM.\n\n"
                                        "For the SDK projects this is the sum of the sections that have"
                                        " \"RETENTION\" in their name.")
E.add_comment("Projects Summary", 0, 7, "The size of the .bin file. If the .bin is not found then the size is 0.")

# Close Excel file
E.close_workbook()

