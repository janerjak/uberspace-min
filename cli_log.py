from enum import Enum
import utility as UTIL

import config_manager as CONFIG_MANAGER

TAG_LENGTH = 6

class CLITag(str, Enum):
    def __str__(self):
        return str(self.value)
    INIT = "INIT"
    CONFIG = "CONFIG"
    INFO = "INFO"
    ERROR = "ERROR"
    WARN = "WARN"
    OK = "OK"
    HUMAN = "HUMAN"

class SilenceSettings:
    silenced = []

def message_should_be_silenced(tag : CLITag) -> bool:
    return None in SilenceSettings.silenced or tag in SilenceSettings.silenced

def log(tag : CLITag, message : str) -> None:
    logStr = None
    if tag == CLITag.ERROR or not message_should_be_silenced(tag):
        logStr = f"{UTIL.get_current_time_string()} [{UTIL.nchar(tag, TAG_LENGTH)}]: {message}"
    if not message_should_be_silenced(tag):
        print(logStr)
    if tag == CLITag.ERROR:
        CONFIG_MANAGER.LoadedConfigs.executionCache["errors"].append(logStr)

def log_exception(message : str, ex : Exception) -> None:
    log(CLITag.ERROR, f"{message}\nException information: {ex}")