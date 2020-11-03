from pkg_resources import resource_string
from mhrc.automation import VERSION

build_time = resource_string(__name__, 'BuildTime.txt').decode().strip()
print("PSCAD Automation Library v{} ({})".format(VERSION, build_time))
print("(c) Manitoba Hydro International Ltd.")
