from time import strftime


def get_time_string(timeformat="%Y_%m_%d_%H_%M_%S", time=None):
    if not time:
        return strftime(timeformat)
    else:
        return strftime(timeformat, time)
