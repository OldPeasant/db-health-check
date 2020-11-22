#!/usr/bin/python3

import sys

from health_lib import run_health_checks
from checks import *

if __name__ == "__main__":
    run_health_checks('--debug' in sys.argv)
