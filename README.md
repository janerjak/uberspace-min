# uberspace-min
### A tool to set the price of Uberspace accounts repeatedly over-time, which enables lower than 5 euros consistently.

## Requirements
- Python installation with version >= 3.6.
- Pip-Packages installed as specified in requirements.txt
  - Can be achieved by `pip3 install -r requirements.txt`
### Recommended
- A scheduling utility like cron

## Usage
1. Copy `settings/config-example.yaml` to `settings/config.yaml` and specify entries for all of your Uberspace accounts.
   (The tool supports multi-accounting natively. However, you could duplicate the codebase for each account as well.)
   - Make sure to comply with the YAML-syntax when creating multiple accounts (start another array entry in `uberspaceValues.accounts` with a leading `-`)
   - Enable or disable humanization. It is recommended to leave it enabled. To force execution, you can specify the `-f` switch or set the `humanization.forceAfterDays` setting to `0`. You can view all available arguments and switches by passing `--help` or `-h` as an argument.
   - If you want to run this script on a schedule, as it is intended to be used, you may run into the issue that the settings directory is specified relativelyby default. If you use cron, you can change the `HOME` variable in your crontab, but this may affect other jobs. Thus you can also specify the folder yourself (relative to the current working directory or absolute) using `-S <directory>`. If you wish to use multiple configurations for some reason, consider arguments `--config-file <file>` and `--execution-cache-file <file>`.
   - Change probabilities for humanization according to your invocation schedule. How to obtain probabilities is given in the example configuration.
2. Either run `uberspace_min.py` directly or pass arguments `-u <username> -p <password> -P <price>` at minimum. To quickly check if the script works, you can specify `--no-humanization` and to mute any CLI output that are neither warnings, errors or success statements, specify `-Ninit -Ni -Nh`.

## Cron
Example crontab entries are given in `crontab-example.txt`.

## Notes considering detectability
This is by no means an undetectable script as it is not required to be, however:
- HTTP headers are set such that the requests appear to be originating from default Firefox actions 
- Basic humanization tries to ensure that requests are not made at recurring intervals or with too similar patterns
- Eventhough closing the browser usually flushes Uberspace sessions (as in logs out the user), the last uberspace-session cookie is still transmitted across browser sessions, which this script mimics
  
Yet as said, it is not perfect and probably detectable if for instance the cronjob is configured to run in too specific intervals. Although fairly basic humanization methods are implemented, this in no way ensures staying undetected. There are a lot of attack vectors here and all methods are solely implemented to ensure long-term feasibility. Similarly, this tool requires you to store your password in some sort of form that it can be provided in plain text, which is only a good idea, if the file permissions are set correctly. Use with caution.

## Legal notice
I am not responsible for any actions caused directly or indirectly by this program (or utility or tool or script) to you, your Uberspace account or any other property. This program is provided without any warranty. Use at your own risk. Additionally all conditions of the MIT License given in `LICENSE.txt` as well as specified in the license property of this repository apply.

## Code changes
Feel free to cleanup code syntax or swap parts for better suited ones. Please create a pull request for me to review in this case.