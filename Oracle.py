##################################################################################################
#  Name:        Oracle.py                                                                        #
#  Author:      Randy Johnson                                                                    #
#  Description: This is a Python function/class library for Oracle. The idea is to put reusable  #
#               code here in order to simplify managing changes to duplicate code across dozens  #
#               of scripts.                                                                      #
#                                                                                                #
##################################################################################################

# --------------------------------------
# ---- Import Python Modules -----------
# --------------------------------------
import traceback

from datetime     import datetime
from getpass      import getpass
from math         import floor
from math         import log
from math         import pow
from subprocess   import PIPE
from subprocess   import Popen
from subprocess   import STDOUT
from os           import environ
from os           import access
from os           import path
from os           import walk
from os           import getpgid
from os           import unlink
from os           import getpgid
from os           import unlink
from os           import W_OK as WriteOk
from os           import R_OK as ReadOk
from os           import X_OK as ExecOk
from os.path      import basename
from os.path      import isfile
from os.path      import join as pathjoin
from re           import match
from re           import search
from re           import IGNORECASE
from re           import compile
from sys          import exit
from sys          import exc_info
from sys          import stdout as termout
from sys          import version_info
from signal       import SIGPIPE
from signal       import SIG_DFL
from signal       import signal
from time         import strptime
from time         import sleep


# ------------------------------------------------
# Imports that are conditional on Python Version.
# ------------------------------------------------
if (version_info[0] >= 3):
  import pickle
  from configparser import SafeConfigParser
  from base64       import b64decode
else:
  import cPickle as pickle
  from ConfigParser import SafeConfigParser
# ------------------------------------------------

# For handling termination in stdout pipe; ex: when you run: oerrdump | head
signal(SIGPIPE, SIG_DFL)


# Set min/max compatible Python versions.
# ----------------------------------------
PyMaxVer = 3.4
PyMinVer = 2.4

# -------------------------------------------------
# ---- Function and Class Definitions ------------
# -------------------------------------------------
