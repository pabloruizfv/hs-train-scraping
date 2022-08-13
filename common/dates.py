from datetime import timedelta, date


def string_date_to_date_object(string_date):
    """
    Converts a date which is provided as a string in "DD/MM/YYYY" format to a
    date object from datetime library.
    :param: string_date: (string "DD/MM/YYYY")
    :return: date_object: (date object)
    """
    date_object = date(year=int(string_date[6:10]),
                       month=int(string_date[3:5]),
                       day=int(string_date[0:2]))
    return date_object


def date_object_to_string_date(date_object):
    """
    Converts a date object from datetime library to a string date in
    "DD/MM/YYYY" format.
    :param: date_object: (date object)
    :return: string_date: (string "DD/MM/YYYY")
    """
    string_date = str(date_object.day).zfill(2) + '/' + \
        str(date_object.month).zfill(2) + '/' + \
        str(date_object.year)

    return string_date


def load_dates_inbetween(first_date, last_date):
    """
    Loads the dates in the interval between the provided first date and
    last date (including both).
    :param first_date: (string "DD/MM/YYYY")
    :param last_date: (string "DD/MM/YYYY")
    :return: inbetween_dates: (list of strings ["DD/MM/YYYY"])
    """
    first_date_object = string_date_to_date_object(first_date)
    last_date_object = string_date_to_date_object(last_date)

    assert first_date_object <= last_date_object

    inbetween_dates = []
    current_date_object = first_date_object
    while current_date_object <= last_date_object:
        current_date = str(current_date_object.day).zfill(2) + '/' + \
            str(current_date_object.month).zfill(2) + '/' + \
            str(current_date_object.year)
        inbetween_dates.append(current_date)
        current_date_object += timedelta(days=1)

    return inbetween_dates


def add_days_to_date(original_date, days_to_add):
    """
    Add a number of dates to a given date.
    :param original_date: (string) DD/MM/YYYY
    :param days_to_add: (integer)
    :return final_date: (string) DD/MM/YYYY
    """
    original_date_obj = string_date_to_date_object(original_date)
    final_date_obj = original_date_obj + timedelta(days=days_to_add)
    final_date = date_object_to_string_date(final_date_obj)
    return final_date
