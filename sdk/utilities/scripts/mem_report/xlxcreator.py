#########################################################################################
# Copyright (C) 2016. Dialog Semiconductor, unpublished work. This computer
# program includes Confidential, Proprietary Information and is a Trade Secret of
# Dialog Semiconductor.  All use, disclosure, and/or reproduction is prohibited
# unless authorized in writing. All Rights Reserved.
#########################################################################################

from abc import ABCMeta, abstractmethod
import xlsxwriter


class AbsExcelWriter:
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, name):
        """
        The init will open a workbook with the name provided and define the formats.

        :param name: Name of the Excel file
        """
        self._name = name
        self._formats = {"main row title": None,
                         "main column title": None,
                         "main data": None,
                         "main data total": None,
                         "row title": None,
                         "column title": None,
                         "data": None,
                         "data string" : None,
                         "data total": None
                         }

    @abstractmethod
    def close_workbook(self):
        """
        Close the workbook. This will create the Excel file.


        :rtype : None
        """
        pass

    @abstractmethod
    def create_sheet(self, name=None):
        """
        Create a worksheet on your workbook

        :rtype : None
        :param name: The name of the worksheet
        """
        pass

    @abstractmethod
    def set_column(self, sheet_name, col, width):
        """
        Set column width within a specific worksheet



        :rtype : None
        :param sheet_name: THe name of the worksheet
        :param col: THe zero indexed column (int)
        :param width: THe required width for the column (int)
        """
        pass

    @abstractmethod
    def set_row(self, sheet_name, row, height):
        """
        Set row height within a specific worksheet



        :rtype : None
        :param sheet_name: THe name of the worksheet
        :param row: THe zero indexed column (int)
        :param height: THe required height for the column (int)
        """
        pass

    @abstractmethod
    def write_worksheet(self, sheet_name, row, col, data, format_as=None):
        """
        A method to write data to a worksheet

        :rtype : None
        :param sheet_name: The name of the sheet to write
        :param row: The zero indexed row to start writing the data (int)
        :param col: The zero indexed column to start writing data (int)
        :param data: The data (list of of list, each internal list is a line)
        :param format_as: Describe type of format for the cells where data will be written
        """
        pass

    @abstractmethod
    def create_chart(self, chart_name, configuration):
        pass

    @abstractmethod
    def add_chart_data_series(self, chart_name, series_configuration):
        pass

    @abstractmethod
    def add_chart_to_sheet(self, sheet_name, chart_name, position):
        pass

    @abstractmethod
    def set_chart_size(self, chart_name, x_grad, y_grad):
        pass

    @abstractmethod
    def add_drop_down_selector(self, sheet_name, start_row, start_col, end_row, end_col):
        pass

    @abstractmethod
    def add_comment(self, sheet_name, row, col, comment_text):
        pass

    @abstractmethod
    def freeze_pane(self, sheet_name, row, col):
        pass


class XLwithXlswriter(AbsExcelWriter):
    def __init__(self, name):
        super(XLwithXlswriter, self).__init__(name)
        self._wb = xlsxwriter.Workbook(name)
        self._ws = {}
        self._charts = {}
        self._formats["main row title"] = self._wb.add_format({'bold': 1, 'italic': 1, 'align': 'center'})
        self._formats["main column title"] = self._wb.add_format({'bold': 1, 'align': 'right'})
        self._formats["main data"] = self._wb.add_format({'bold': 1, 'font_color': '#FA7D00', 'bg_color': '#F2F2F2',
                                                          'border': 7})
        self._formats["main data total"] = self._wb.add_format({'bold': 1, 'bg_color': '#B2B2B2', 'border': 7})
        self._formats["row title"] = self._wb.add_format({'italic': 1, 'align': 'center', 'font_color': '#7F7F7F'})
        self._formats["column title"] = self._wb.add_format({'align': 'left', 'bg_color': '#FFDEBD',
                                                             'font_color': '#3F3F76', 'border': 7,
                                                             'border_color': '#7F7F7F'})
        self._formats["data"] = self._wb.add_format({'align': 'right', 'bg_color': '#FFCC99', 'font_color': '#3F3F76',
                                                     'border': 7, 'border_color': '#7F7F7F'})
        self._formats["data string"] = self._wb.add_format({'align': 'left', 'bg_color': '#FFDEBD',
                                                            'font_color': '#3F3F76', 'border': 7,
                                                            'border_color': '#7F7F7F'})
        self._formats["data total"] = self._wb.add_format({'align': 'right', 'bg_color': '#FFA347',
                                                           'font_color': '#3F3F76', 'border': 7,
                                                           'border_color': '#7F7F7F'})

    def close_workbook(self):
        self._wb.close()

    def create_sheet(self, name=None):
        if name not in self._ws:
            self._ws[name] = self._wb.add_worksheet(name)

    def set_column(self, sheet_name, col, width):
        self._ws[sheet_name].set_column(col, col, width)

    def set_row(self, sheet_name, row, height):
        self._ws[sheet_name].set_row(row, height)

    def write_worksheet(self, sheet_name, row, col, data, format_as=None):
        active_row, active_col = row, col
        for l in data:
            for c in l:
                self._ws[sheet_name].write(active_row, active_col, c, self._formats[format_as])
                active_col += 1
            active_row += 1
            active_col = col

    def create_chart(self, chart_name, configuration):
        if chart_name in self._charts:
            raise AssertionError
        self._charts[chart_name] = self._wb.add_chart(configuration)

    def add_chart_data_series(self, chart_name, series_configuration):
        self._charts[chart_name].add_series(series_configuration)

    def add_chart_to_sheet(self, sheet_name, chart_name, position):
        self._ws[sheet_name].insert_chart(position, self._charts[chart_name])

    def set_chart_size(self, chart_name, x_scale, y_scale):
        self._charts[chart_name].set_size({'x_scale': x_scale, 'y_scale': y_scale})

    def add_drop_down_selector(self, sheet_name, start_row, start_col, end_row, end_col):
        self._ws[sheet_name].autofilter(start_row, start_col, end_row, end_col)

    def add_comment(self, sheet_name, row, col, comment_text):
        self._ws[sheet_name].write_comment(row, col, comment_text)

    def freeze_pane(self, sheet_name, row, col):
        self._ws[sheet_name].freeze_panes(row, col)


def cell_id(row, col):
    if col < 26:
        return chr(ord('A') + col) + str(row + 1)
    elif col < 52:
        return 'A' + chr(ord('A') + col - 26) + str(row + 1)
    else:
        return 'B' + chr(ord('A') + col - 52) + str(row + 1)
