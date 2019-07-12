##################################################################################################
#  Name:        Oracle.py                                                                        #
#  Author:      Randy Johnson                                                                    #
#  Description: This is a Python function/class library for Oracle. The idea is to put reusable  #
#               code here in order to simplify managing changes to duplicate code across dozens  #
#               of scripts.                                                                      #
#                                                                                                #
#  Functions:   LoadOratab(Oratab='')                                                            #
#               SetOracleEnv(Sid, Oratab='/etc/oratab')                                          #
#               ChunkString(InStr, Len)                                                          #
#               CheckPythonVersion()                                                             #
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

# ------------------------------------------------
# ---- Function and Class Definitions ------------
# ------------------------------------------------
# ---------------------------------------------------------------------------
# Def : LoadOratab()
# Desc: Parses the oratab file and returns a dictionary structure of:
#        {'dbm'      : '/u01/app/oracle/product/11.2.0.3/dbhome_1',
#         'biuat'    : '/u01/app/oracle/product/11.2.0.3/dbhome_1',
#         ...
#        }
#       Note** the start/stop flag is parsed but not saved.
#       If the fully qualified oratab file name is passed in it is prepended
#       to a list of standard locations (/etc/oratab, /var/opt/oracle/oratab)
#       This list of oratab locations are then searched in order. The first
#       one to be successfully opened will be used.
# Args: Oratab (optional, defaults to '')
# Retn: OratabDict (dictionary object)
# ---------------------------------------------------------------------------
def LoadOratab(Oratab=''):
  OraSid     = ''
  OraHome    = ''
  OraFlag    = ''
  OratabDict = {}
  OratabList = []
  OratabLoc  = ['/etc/oratab','/var/opt/oracle/oratab']
  f          = None
  
  # If an _ORATAB_ environment variable is set...
  if '_ORATAB_' in environ:
    if (not (environ['_ORATAB_'] in OratabLoc)):
      OratabLoc.insert(0, environ['_ORATAB_'])

  # If an oratab file name was passed in...
  if (Oratab != ''):
    if (not (Oratab in OratabLoc)):
      OratabLoc.insert(0, Oratab)

  # Load the first readable file in OratabLoc and then break.
  for Oratab in OratabLoc:
    if (isfile(Oratab)):
      try:
        f = open(Oratab)
        break
      except:
        print('\n%s' % traceback.format_exc())
        print('\nCannot open oratab file: ' + Oratab + ' for read.')
        return {}

  # Parse the oratab file and load elements of the Oratab dictionary...
  if (not f):
    return {}
  else:
    for line in f.readlines():
      line = line.split('#', 1)[0].strip()
      Count = line.count(':')
      if (Count >= 1):
        OraFlag = ''
        if (Count == 1):
          (OraSid, OraHome) = line.split(':')
        elif (Count == 2):
          (OraSid, OraHome, OraFlag) = line.split(':')
        elif (Count >= 3):
          OraSid = line.split(':')[0]
          OraHome = line.split(':')[1]
          OraFlag = line.split(':')[2]
        OratabDict[OraSid] = OraHome

  return(OratabDict)

# ---------------------------------------------------------------------------
# Def : SetOracleEnv()
# Desc: Setup your environemnt, eg. ORACLE_HOME, ORACLE_SID. (Parses oratab
#       file).
# Args: Sid = The ORACLE_SID of the home you want to configure for
#       Oratab = FQN of the oratab file (optional)
# Retn: OracleSid = $ORACLE_SID
#       OracleHome = $ORACLE_HOME
# ---------------------------------------------------------------------------
def SetOracleEnv(Sid, Oratab='/etc/oratab'):
  OracleSid  = ''
  OracleHome = ''
  OratabDict = LoadOratab()
  SidCount   = len(OratabDict.keys())

  if (SidCount > 0):
    if (Sid in OratabDict.keys()):
      OracleSid  = Sid
      OracleHome = OratabDict[OracleSid]
      environ['ORACLE_SID']  = OracleSid
      environ['ORACLE_HOME'] = OracleHome

      if ('LD_LIBRARY_PATH' in environ.keys()):
        if (environ['LD_LIBRARY_PATH'] != ''):
          environ['LD_LIBRARY_PATH'] = OracleHome + '/lib' + ':' + environ['LD_LIBRARY_PATH']       # prepend to LD_LIBRARY_PATH
        else:
          environ['LD_LIBRARY_PATH'] = OracleHome + '/lib'
      else:
        environ['LD_LIBRARY_PATH'] = OracleHome + '/lib'

  return(OracleSid, OracleHome)
# ---------------------------------------------------------------------------
# End SetOracleEnv()
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Def : ChunkString()
# Desc: This function returns Cgen (a generator), using a generator
#       comprehension. The generator returns the string sliced, from 0 + a
#       multiple of the length of the chunks, to the length of the chunks + a
#       multiple of the length of the chunks.
#
#       You can iterate over the generator like a list, tuple or string -
#          for i in ChunkString(s,n): ,
#       or convert it into a list (for instance) with list(generator).
#       Generators are more memory efficient than lists because they generator
#       their elements as they are needed, not all at once, however they lack
#       certain features like indexing.
# Args: 1=String value
#     : 2=Length of chunks to return.
# Retn:
# ---------------------------------------------------------------------------
def ChunkString(InStr, Len):
  return((InStr[i:i+Len] for i in range(0, len(InStr), Len)))
# ---------------------------------------------------------------------------
# End ChunkString()
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Def : CheckPythonVersion()
# Desc: Checks the version of Python and prints error and exit(1) if not
#       within required range.
# Args: rv=requried version
# Retn: 0 or exit(1)
# ---------------------------------------------------------------------------
def CheckPythonVersion():
  import sys

  v = float(str(sys.version_info[0]) + '.' + str(sys.version_info[1]))
  if v >= PyMinVer and v <= PyMaxVer:
    return(str(sys.version_info[0]) + '.' + str(sys.version_info[1]) + '.' + str(sys.version_info[2]))
  else:
    print( "\nError: The version of your Python interpreter (%1.1f) must between %1.1f and %1.1f\n" % (v, PyMinVer, PyMaxVer) )
    exit(1)
# ---------------------------------------------------------------------------
# End CheckPythonVersion()
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# End LoadOratab()
# ---------------------------------------------------------------------------

