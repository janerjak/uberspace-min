from argparse import ArgumentParser

import argument_filters as ArgType

def parse():
    mainParser = ArgumentParser(
        description="Tool to set the price of Uberspace accounts repeatedly over-time, which enables lower than 5 euros consistently.",
        epilog="If not already done, start by copying settings/config-example.yaml to settings/config.yaml and edit settings in this file. Alternatively you can provide basic settings as arguments."
    )

    ## Overrides for the config file
    mainParser.add_argument("--username", "-u", metavar="username", type=str, required=False, help="Uberspace account name")
    mainParser.add_argument("--password", "-p", metavar="password", type=str, required=False, help="Uberspace account password (plain)")
    mainParser.add_argument("--price", "-P", metavar="price", type=float, required=False, help="price to set your Uberspace account to")
    mainParser.add_argument("--force", "-f", action="store_true", help="force price change now")
    mainParser.add_argument("--settings-path", "-S", metavar="directory", required=False, default="settings/", help="Path to the directory containing the config file and execution cache")
    mainParser.add_argument("--config-file", "-Fc", metavar="file", required=False, default="config.yaml", help="Filename of the configuration file to use")
    mainParser.add_argument("--execution-cache-file", "-Fec", metavar="file", required=False, default="execution-cache.yaml", help="Filename of the execution cache")

    ## Modifiers
    # Humanization arguments
    humanGroup = mainParser.add_argument_group("human", description="Humanization arguments, including probabilities to perform no action, only login, request other pages in the account page, after how many days to force price updates.")
    humanGroup.add_argument("--no-humanization", "-nh", action="store_true", help="Do not use humanization in any way")
    humanGroup.add_argument("--p-noop", "-Pno", metavar="Pno", type=ArgType.pfloat, help="The probability of execution stopping immediately without performing actions, given that setting the price is not forced by --force or --human:force-after-days")
    humanGroup.add_argument("--p-only-login", "-Pol", metavar="Pol", type=ArgType.pfloat, help="The probability of execution stopping after loging in, given that setting the price is not forced by --force or --human:force-after-days")
    humanGroup.add_argument("--force-after-days", "-fAD", metavar="days", type=int, help="The amount of days after which a price update is forced. This feature only works if execution caches are writable.")

    # CLI behavior arguments
    cliGroup = mainParser.add_argument_group("cli", description="Arguments that modify the behavior of the CLI or logging.")
    cliGroup.add_argument("--silent", "-s", action="store_true", help="Do not output anything to STDOUT")
    cliGroup.add_argument("--no-init", "-Ninit", action="store_true", help="Do not output init info")
    cliGroup.add_argument("--no-info", "-Ni", action="store_true", help="Do not output info")
    cliGroup.add_argument("--no-warn", "-Nw", action="store_true", help="Do not output warnings")
    cliGroup.add_argument("--no-error", "-Ne", action="store_true", help="Do not output errors")
    cliGroup.add_argument("--no-human", "-Nh", action="store_true", help="Do not output humanization information")
    cliGroup.add_argument("--error-log-file", "-EL", metavar="logPath", type=str, help="Path where errors are logged additionally to STDOUT and executation-cache.yaml. This option ignores silencing applied through --silent or --noerror")

    return mainParser.parse_args()