"""Datetime utilities
"""
import datetime

standard_datetime_format = "%Y-%m-%d %H:%M:%S"

def get_current_time_str():
    """Return the current time as a string
    """
    return datetime.datetime.now().strftime(
        standard_datetime_format
    )


def convert_str_to_unix_timestamp(datestring, formatter):
    """Convert a timestamp string to unix time
    """
    unix_time = datetime.timestamp(
        datetime.strptime(datestring, formatter)
    )
    return int(unix_time * 1000)


def reformat_datetime_str(datetime_str, source_format, dest_format):
    """Reformat the given datetime string
    """
    return datetime.datetime.strptime(
        datetime_str, source_format
    ).strftime(dest_format)


def start_end_times_from_hoursago(hoursago: int=0):
    """given an integer number of hours ago, returns
       the start and end datetimes as strings
    """
    now = datetime.datetime.now()
    then = now - datetime.timedelta(hours=hoursago)
    start_str = then.strftime(standard_datetime_format)
    end_str = now.strftime(standard_datetime_format)
    return start_str, end_str
