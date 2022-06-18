import copy

from cli_log import CLITag, log

def build_active_config_from_args_and_config(args, config):
    activeConfig = copy.deepcopy(config)

    if args.username is not None:
        if args.password is None or args.price is None:
            log(CLITag.WARN, f"Username '{args.username}' was specified, but not in conjunction with a password and price. The given username argument will be ignored and config values are used instead.")
        else:
            accountToUse = {
                "username": args.username,
                "password": args.password,
                "price": args.price,
                "host": None
            }
            activeConfig["uberspaceValues"]["accounts"] = [accountToUse]
    if args.no_humanization:
        activeConfig["humanization"]["enableHumanization"] = False
    if args.p_noop is not None:
        activeConfig["humanization"]["probabilities"]["noop"] = args.p_noop
    if args.p_only_login is not None:
        activeConfig["humanization"]["probabilities"]["onlyLogin"] = args.p_only_login
    if args.force_after_days is not None:
        activeConfig["humanization"]["forceAfterDays"]= args.force_after_days

    return activeConfig

def sanity_check_active_config(active_config):
    return True