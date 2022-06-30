from os import path
from shutil import copyfile
from yaml import dump, full_load

from cli_log import log, log_exception, CLITag

CONFIG_EXAMPLE_FILE_NAME = "config-example.yaml"
# Concatenation of --setings-path (settings/) and file names given in --config-file, --execution-cache-file. Are Initialized in init_file_paths()
PATH_CONFIG_EXAMPLE, PATH_CONFIG, PATH_EXECUTION_CACHE = None, None, None

class LoadedConfigs:
    config = None
    executionCache = None

def init_file_paths(args):
    global PATH_CONFIG_EXAMPLE, PATH_CONFIG, PATH_EXECUTION_CACHE
    PATH_CONFIG_EXAMPLE = path.join(args.settings_path, CONFIG_EXAMPLE_FILE_NAME)
    PATH_CONFIG = path.join(args.settings_path, args.config_file)
    PATH_EXECUTION_CACHE = path.join(args.settings_path, args.execution_cache_file)

def does_config_file_exist() -> bool:
    return path.exists(PATH_CONFIG)

def parse(file_name : str, parse_error_message : str = None):
    try:
        configFileHandle = open(file_name, "r")
        return full_load(configFileHandle)
    except Exception as ex:
        if parse_error_message is None:
            parse_error_message = file_name
        log_exception(f"Error reading config file {file_name}", ex)
        return None

def parse_config():
    return parse(PATH_CONFIG)

def parse_execution_cache():
    execCache = parse(PATH_EXECUTION_CACHE)
    if execCache["errors"] is None:
        execCache["errors"] = []
    return execCache

def get_config():
    if LoadedConfigs.config is None:
        LoadedConfigs.config = parse_config()
    return LoadedConfigs.config

def get_execution_cache():
    if LoadedConfigs.executionCache is None:
        LoadedConfigs.executionCache = parse_execution_cache()
    return LoadedConfigs.executionCache

def write_loaded_config(config_obj, file_name : str) -> bool:
    if config_obj is None:
        return False
    try:
        configFileHandle = open(file_name, "w")
        configFileHandle.write(dump(config_obj))
    except Exception as ex:
        log_exception(f"Writing loaded config {file_name} failed", ex)
        return False
    return True

def write_config():
    return write_loaded_config(LoadedConfigs.config, PATH_CONFIG)

def write_execution_cache():
    return write_loaded_config(LoadedConfigs.executionCache, PATH_EXECUTION_CACHE)

def copy_config_file_if_none_present() -> bool:
    if does_config_file_exist():
        return False
    log(CLITag.WARN, "No configuration file was found")
    log(CLITag.INIT, "Copying example configuration file to expected location")
    try:
        copyfile(PATH_CONFIG_EXAMPLE, PATH_CONFIG)
    except Exception as ex:
        log_exception(f"Could not copy example configuration file", ex)
        return None
    return True