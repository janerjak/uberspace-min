import random
import sys
import time

from bs4 import BeautifulSoup as HTML
from datetime import datetime
from requests import Request, Session

import config_manager as CONFIG_MANAGER
import utility as UTIL

from cli_log import CLITag, log, log_exception

PERSISTENT_REQUEST_HEADERS = {
    "Host": "dashboard.uberspace.de",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://dashboard.uberspace.de",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "TE": "trailers",
}

DEFAULT_DELAY = None

#CONFIG_MANAGER.LoadedConfigs.executionCache["humanizationMetaInfo"]["lastPriceActionDate"] = UTIL.get_current_time_string()

def roll_dice(prob):
    if prob is None or prob <= 0.0:
        return None
    return random.random() < prob

def wait_expected_deviation(probability_dict : dict):
    maxDeviation = probability_dict["maxDeviation"]
    deviation = random.randint(0, maxDeviation * 2)
    duration = probability_dict["expected"] - maxDeviation + deviation
    log(CLITag.HUMAN, f"Waiting {duration} ms due to humanization")
    time.sleep(duration / 1000)

def perform_request(request_main_function, request_main_function_kwargs, session, url, description, enable_humanization = True, delay = None, status_code_method = None, eng_verb : str = "load", ok_message_suffix = None) -> bool:
    statusCode = None
    resp = None
    try:
        log(CLITag.INFO, f"{eng_verb.capitalize()}ing {description}...")
        resp = request_main_function(url, **request_main_function_kwargs)
        statusCode = status_code_method(resp) if status_code_method is not None else resp.status_code
        UTIL.raise_exception_if(statusCode not in [200, 302])

        # Set the referer for the next request
        session.headers.update({"Referer": resp.request.url})
        
        # Extract session cookie
        cookieDict = resp.cookies.get_dict()
        sessionCookie = UTIL.get_dictionary_value_or_none(cookieDict, "uberspace_session")
        if sessionCookie is not None:
           CONFIG_MANAGER.LoadedConfigs.executionCache["lastSessionCookie"] = sessionCookie

        okMessage = f"{description.capitalize()} was {eng_verb}ed"
        if ok_message_suffix is not None:
            okMessage += f": ({ok_message_suffix})"
        log(CLITag.OK, okMessage)

        delay = delay if delay is not None else DEFAULT_DELAY
        if delay is not None and enable_humanization:
            wait_expected_deviation(delay)
    except:
        log(CLITag.ERROR, f"Could not {eng_verb} {description}. Received HTTP status code {statusCode}.")
        return False, resp
    return True, resp

def perform_get_request(session, url, description, enable_humanization = True, delay = None, status_code_method = None, eng_verb = "load", ok_message_suffix = None) -> bool:
    return perform_request(session.get, {}, session, url, description, enable_humanization, delay, status_code_method, eng_verb, ok_message_suffix)

def perform_post_request(session, url, description, enable_humanization = True, delay = None, status_code_method = None, data = None, eng_verb="perform", ok_message_suffix = None) -> bool:
    return perform_request(session.post, {"data": data}, session, url, description, enable_humanization, delay, status_code_method, eng_verb, ok_message_suffix)

def randomly_visit_other_pages(rsession, probability_request_another_page, delay_between_pages):
    while random.random() < probability_request_another_page:
        log(CLITag.INFO, "Requesting another random page")
        urlPart = random.choice([
            "dashboard",
            "dashboard/datasheet",
            "dashboard/authentication",
            "dashboard/mail",
            "dashboard/domain",
            "dashboard/dpa",
        ])
        url = f"https://dashboard.uberspace.de/{urlPart}"
        perform_get_request(rsession, url, "random page", enable_humanization=True, delay=delay_between_pages)

def request_routine_main(args, active_config, execution_cache):
    humanizationSettings = active_config["humanization"]
    uberspaceValues = active_config["uberspaceValues"]
    accounts = uberspaceValues["accounts"] if uberspaceValues is not None else None
    enableHumanization = humanizationSettings["enableHumanization"] if humanizationSettings is not None else False
    probabilities = humanizationSettings["probabilities"] if humanizationSettings is not None else None
    delays = humanizationSettings["delays"] if humanizationSettings is not None else None
    global DEFAULT_DELAY
    DEFAULT_DELAY = delays["betweenPages"] if delays is not None else None
    
    if accounts is None or len(accounts) <= 0:
        log(CLITag.WARN, f"No accounts to perform routines for. Provide them as execution arguments or in settings/config.yaml")

    log(CLITag.INIT, f"Will perform routines for {len(accounts)} account{('s' if len(accounts) > 1 else '')}")

    firstAccount = True
    for account in accounts:    
        log(CLITag.INFO, f"Performing routine for user {account['username']}")

        # Check for password is none
        if account["password"] is None:
            log(CLITag.ERROR, f"There is no password given for user '{account['username']}'. This is most likely due to the configuration being the example configuration. Please edit settings/config.yaml or provide execution arguments. See --help for more information.")
            continue

        if firstAccount:
            firstAccount = False
        elif len(accounts > 1):
            wait_expected_deviation(delays["betweenAccounts"])

        ## Check if this account has to be forced now
        force = True if args.force else False
        humanizationMetaInfo = execution_cache["humanizationMetaInfo"]
        if (not force) and humanizationMetaInfo is not None and humanizationMetaInfo["lastPriceUpdateDates"] is not None and account["username"] in humanizationMetaInfo["lastPriceUpdateDates"]:
            lastPriceUpdateDateStr = humanizationMetaInfo["lastPriceUpdateDates"][account["username"]]
            if lastPriceUpdateDateStr is not None and isinstance(lastPriceUpdateDateStr, str):
                lastPriceUpdateDateObj = datetime.strptime(lastPriceUpdateDateStr, "%Y-%m-%d %H:%M:%S")
                delta = datetime.now() - lastPriceUpdateDateObj
                if delta.days >= humanizationSettings["forceAfterDays"]:
                    force = True
                    log(CLITag.HUMAN, f"Forcing to set the price, as too many days ({delta.days}) have passed since the last successful price update")
        else:
            force = True
            log(CLITag.HUMAN, f"Forcing to set the price, as this accounts' price has never been successfully set")

        if force:
            log(CLITag.INFO, "This invocation is forcefully executed (no termination due to humanization)")

        ## Basic noop roll
        if (not force) and enableHumanization:
            # If noop-probability is significant, roll the dice
            if roll_dice(probabilities["noop"]):
                log(CLITag.HUMAN, "Not performing any actions this invocation due to humanization")
                return
        
        ## Perform login
        # Load last uberspace session cookie if it exists from execution cache
        lastSessionCookie = execution_cache["lastSessionCookie"]
        # Create a requests.Session used for the entirety of requests. This handles cookie management automatically
        with Session() as rsession:
            if lastSessionCookie is not None:
                rsession.cookies.set("uberspace_session", lastSessionCookie, domain="dashboard.uberspace.de")
            rsession.headers.update(PERSISTENT_REQUEST_HEADERS)

            # Load the homepage
            success, resp = perform_get_request(rsession, "https://uberspace.de", "the homepage", enableHumanization, status_code_method=lambda resp: resp.history[0].status_code)
            if not success:
                return

            # Load the login page
            success, resp = perform_get_request(rsession, "https://dashboard.uberspace.de/login?lang=en", "login page", enableHumanization)
            if not success:
                return
            
            # Parse the CSRF token from the given login DOM
            csrfToken = None
            try:
                loginDom = HTML(resp.content, "html.parser")
                csrfInputs = [input for input in loginDom.find_all("input") if "name" in input.attrs and input.attrs["name"] == "_csrf_token"]
                csrfToken = csrfInputs[0].attrs["value"]
                UTIL.raise_exception_if(not UTIL.string_is_neither_none_nor_whitespace(csrfToken))
            except Exception as ex:
                log_exception("Extracting the CSRF token from the login form was not successful.", ex)
                return

            if enableHumanization:
                log(CLITag.INFO, "Simulating delay of entering credentials")
                wait_expected_deviation(delays["loginCredentials"])

            ## Send login request
            success, resp = perform_post_request(rsession, "https://dashboard.uberspace.de/login", "login request", enableHumanization,
                data = {
                    "_csrf_token": csrfToken,
                    "login": account["username"],
                    "password": account["password"],
                    "submit": "login",
                },
            )

            # Failed logins redirect to dashboard.uberspace.de/login, successful to dashboard.uberspace.de/dashboard
            if not success or resp is None or not UTIL.string_ends_with(resp.url, "dashboard"):
                log(CLITag.INFO, "Could not login. Either the credentials are wrong or the login method used is outdated")
                continue

            ## View other pages by chance
            if enableHumanization:
                randomly_visit_other_pages(rsession, probabilities["requestAnotherPage"], delays["betweenPages"])

            ## Check if this is enough for this iteration due to humanization
            if (not force) and enableHumanization and roll_dice(probabilities["onlyLogin"]):
                log(CLITag.HUMAN, "Only logged in and not changing the price this iteration due to humanization")
                continue

            ## Set the price
            # Visit accounting page
            success, resp = perform_get_request(rsession, "https://dashboard.uberspace.de/dashboard/accounting", "accounting page", enableHumanization)
            if not success:
                log(CLITag.ERROR, "Could not load accounting page")

            # Visit cross financed price page
            success, resp = perform_get_request(rsession, "https://dashboard.uberspace.de/dashboard/accounting/cross_financed_price", "cross financed price page", enableHumanization)
            if not success:
                log(CLITag.ERROR, "Could not load cross financed pricing page")

            # Parse the CSRF token from the given cross financed price DOM
            csrfToken = None
            try:
                cfpDom = HTML(resp.content, "html.parser")
                csrfInputs = [input for input in cfpDom.find_all("input") if "name" in input.attrs and input.attrs["name"] == "_csrf_token"]
                csrfToken = csrfInputs[0].attrs["value"]
                UTIL.raise_exception_if(not UTIL.string_is_neither_none_nor_whitespace(csrfToken))
            except Exception as ex:
                log_exception("Extracting the CSRF token from the accounting page was not successful.", ex)
                return

            ## Perform the price update POST request
            
            price = "{:.2f}".format(account["price"]).replace(".", ",")
            success, resp = perform_post_request(rsession, "https://dashboard.uberspace.de/dashboard/set_price", "price update", enableHumanization,
                data = {
                    "came_from_cross_financed_price": "1",
                    "_csrf_token": csrfToken,
                    "price": price,
                },
                ok_message_suffix=f"{account['username']} -> {account['price']}"
            )
            if not success or resp is None or not UTIL.string_ends_with(resp.url, "accounting"):
                log(CLITag.ERROR, f"Failed to set the price for account {account['username']}")
            
            ## Set the execution cache last update time
            lastPriceUpdateDates = CONFIG_MANAGER.LoadedConfigs.executionCache["humanizationMetaInfo"]["lastPriceUpdateDates"]
            if lastPriceUpdateDates is None:
                lastPriceUpdateDates = {}
            lastPriceUpdateDates[account["username"]] = UTIL.get_current_time_string()
            CONFIG_MANAGER.LoadedConfigs.executionCache["humanizationMetaInfo"]["lastPriceUpdateDates"] = lastPriceUpdateDates
            
            ## One last time visit other pages by chance
            if enableHumanization:
                randomly_visit_other_pages(rsession, probabilities["requestAnotherPage"], delays["betweenPages"])

            ## Potentially actively log out of the account
            if enableHumanization and roll_dice(probabilities["logout"]):
                log(CLITag.HUMAN, "Actively log out of the account")
                success, resp = perform_get_request(rsession, "https://dashboard.uberspace.de/logout", "logout", enable_humanization=False, status_code_method=lambda resp: resp.history[0].status_code, eng_verb="perform")