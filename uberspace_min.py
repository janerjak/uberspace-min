#!/bin/python3

# Author: Jan Erik Karuc
# Project: uberspace-min
# Description: A tool to set the price of Uberspace accounts repeatedly over-time. Intended for use in combination with scheduling suites such as crond.
# Version: 1.0.0
# License: MIT License (See LICENSE.txt shipped with project)

# -- Coding style --
# Method-names, parameters: lower_snake
# In-function variables: camelCase
# Rest should be PEP-8 compliant. Feel free to fix.

import argument_parser as ARG_PARSE
import config_manager as CONFIG_MANAGER
import config_merger as CONFIG_MERGER
import request_routine as REQUEST_ROUTINE
import utility as UTIL
from cli_log import CLITag, SilenceSettings, log

def main():
    args = ARG_PARSE.parse()
    if args.silent:
        # Silence all log messages
        SilenceSettings.silenced.append(None)
    silenceArgsToCheck = [
        "init", "info", "warn", "error", "human"
    ]
    for silenceArg in silenceArgsToCheck:
        cliTag = CLITag[silenceArg.upper()]
        if cliTag is not None and getattr(args, f"no_{silenceArg}"):
            SilenceSettings.silenced.append(cliTag)

    # Initialize file paths
    CONFIG_MANAGER.init_file_paths(args)

    # If no config file is present at the expected path, copy the example config
    exampleCopied = CONFIG_MANAGER.copy_config_file_if_none_present()
    config = CONFIG_MANAGER.get_config()
    executionCache = CONFIG_MANAGER.get_execution_cache()

    # Replace certain none arguments with specified values in the settings file
    activeConfig = CONFIG_MERGER.build_active_config_from_args_and_config(args, config)

    log(CLITag.INIT, "Initialization complete. Starting main routine...")
    
    REQUEST_ROUTINE.request_routine_main(args, activeConfig, executionCache)

    # After execution is finished, save the execution cache to disk
    executionCacheWritten = CONFIG_MANAGER.write_execution_cache()
    if CONFIG_MANAGER.LoadedConfigs.executionCache is not None and not executionCacheWritten:
        log(CLITag.ERROR, "Error writing execution cache. Features that rely on this might be impacted.")

    log(CLITag.OK, "Terminating.")

if __name__ == "__main__":
    main()