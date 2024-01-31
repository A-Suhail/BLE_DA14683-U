####################################################################################################
#
# @name filter.py
# @brief
#
# Copyright (C) 2016 Dialog Semiconductor.
# This computer program includes Confidential, Proprietary Information
# of Dialog Semiconductor. All Rights Reserved.
#
####################################################################################################


class Null:
    """ Null filter always returns None - serves as base class for every filter.
    The real purpose of filter is precess the raw data just after it is read from the input device
    (input filter list) or just before it's written to the output device (output filter list). """

    def __call__(self, input_data_generator, **kwargs):
        """ The main filter applying call.
        :param input_data_generator: A data string or a data generator
        :param kwargs: An additional arguments that the filter can be called with
        :return: Processed data
        """
        return None


class Echo(Null):
    """ Echo filter just dumps the raw data into the console. """

    def __init__(self, msg='echo:'):
        """ Initialise the echo filter with a message string.
        :param msg: First part of the message that will be printed along with the raw data
        """
        self.msg = msg

    def __call__(self, data, **kwargs):
        """ This filter just prints the raw data into the console. """
        print('%s %s' % (self.msg, ' '.join(['%.2x' % ord(d) for d in data])))
        return data


def apply_filters(data, *filters):
    """ This helper function stacks up filters in a linear fashion.

    :param data: Input data or data generator
    :param filters: Filters to be combined
    :return: Stacked filters result
    """
    result = data
    for f in filters:
        result = f(result)

    return result
