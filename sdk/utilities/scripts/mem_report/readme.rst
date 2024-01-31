======================
Memory Reporting Tools
======================

These are Python scripts that generate Excel files containing memory utilization
reports for projects created with the SDK.

Prerequisites
-------------

The scripts have been developped using Python 2.7. Other than that the only 
thing needed is XlsxWriter_

.. _XlsxWriter: http://xlsxwriter.readthedocs.io/

XlsWriter Windows installation::

> c:\Python27\python.exe –m pip install XlsxWriter

XlsWriter Linux installation::

> python pip install XlsxWriter

Usage
-----

Memory Reporter
~~~~~~~~~~~~~~~

Memory Reporter takes as input a linker map file from a project and generates an
Excel file containing the memory utilization report for it::

> python mem_reporter.py <path to map file>

Note that the output Excel name will consist of the directory name containing 
the map file and the name of the map file (so it ends up something like 
DA14681-01-Release_QSPI_ble_adv.xlsx), based on the assumption that map files are
inside Eclipe's build configuration folders. Have that in mind to understand the
implications of moving the map file elsewhere before running the script.

Create Sunmmary
~~~~~~~~~~~~~~~
It is also possible to create an Excel file containing a brief summary of the
sizes of several projects. For that you will need to run this script::

> python create_summary.py <path that contains projects' map files> <name of output Excel file>

Known Issues
------------

Retained RAM reporting for RAM builds
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Memory reporter gives an incorrect report of retained RAM requirements in case of a RAM projects. It adds to the
retained RAM only the sections with names like 'RETAINED_XXX' like in the case of QSPI projects. In reality RAM projects
have larger retained RAM requirements (.text section needs also to be retained, etc.).

Use of link-time optimization option (LTO)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The memory reporter uses the path of the object files in order to classify them into specific SDK modules ("ble",
"cpm", "peripherals", "adapters", etc.). When LTO is used, the compiler creates intermediate object files for the linker
to be able to perform the optimizations. These object files do not keep their original names and as a result the module
classification is not possible. These object files are classified as "unknown".

Zero formulas in LibreOffice
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This concerns mostly Linux users. You may see that some cells containing formulas have ‘0’s 
instead of the expected number. Press Ctrl+Shft+F9 to fix this or try Tools->Options-> under 
LibreOfficeCalc->Formula and in “Recalculation on file load” select “Always recalculate” for 
a permanent solution.

`Here you can find details for this issue`_ (it applies also for some other spreadsheet 
applications)

.. _Here you can find details for this issue: http://stackoverflow.com/questions/32205927/xlsxwriter-and-libreoffice-not-showing-formulas-result

No new lines in cells (Windows)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The tools insert new lines in some cells. However in Excel these are not enabled by default. In order
to fix the display of cells with new lines, you need to select the cells and press the "Wrap Text" button.

