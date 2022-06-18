from datetime import datetime as timestamp
import random
import string

def random_string(length : int) -> string:
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def string_represents_integer(string : str) -> bool:
    try:
        int(string)
        return True
    except (TypeError, ValueError):
        return False

def string_as_int_none(string : str) -> int:
    try:
        return int(string)
    except (TypeError, ValueError):
        return None

def string_is_neither_none_nor_whitespace(string : str) -> bool:
    return string is not None \
            and isinstance(string, str) \
            and len(string) > 0 \
            and not string.isspace()

def string_starts_with(string : str, prefix : str) -> bool:
    return string[:len(prefix)] == prefix

def string_ends_with(string : str, suffix : str) -> bool:
    return string[-len(suffix):] == suffix

def format_time_to_string(timeObj : timestamp) -> str:
    return timeObj.strftime("%Y-%m-%d %H:%M:%S")

def get_current_time_string() -> str:
    return format_time_to_string(get_current_time())

def get_current_time() -> timestamp:
    return timestamp.now()

def nchar(inStr : str, length : int, fillChar : str = '-') -> str:
    inStr = str(inStr)
    return inStr[0:length] if len(inStr) >= length else inStr + (fillChar * (length - len(inStr)))

def nchar_front(inStr : str, length : int, fillChar : str = '0'):
    inStr = str(inStr)
    return inStr[0:length] if len(inStr) >= length else (fillChar * (length - len(inStr))) + inStr

def get_dictionary_value_or_lookup_none(dict : dict, key):
    if key in dict.keys():
        return dict[key]
    elif not None in dict.keys():
        raise Exception("Key was not found in dictionary, but default key None has no value. None is returned.")
    else:
        return dict[None]

def get_dictionary_value_or_none(dict : dict, key):
    if key in dict.keys():
        return dict[key]
    else:
        return dict[None]

def raise_exception_if(condition_eval : bool, exception : Exception = None):
    if condition_eval:
        raise Exception() if exception is None else \
                (exception if isinstance(exception, Exception) else Exception(str(exception)))

def get_file_extension(filename : str) -> str:
    if not '.' in filename:
        return None
    return filename.rsplit('.', 1)[1].lower()

def has_filename_allowed_extension(filename : str, allowed_extensions : list) -> bool:
    return get_file_extension(filename) in allowed_extensions

def is_last_iter(iterIndex : int, iterRangeNonInclusive : int) -> bool:
    return iterIndex <= iterRangeNonInclusive - 1