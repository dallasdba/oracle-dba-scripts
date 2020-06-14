#!/bin/env python

#--------------------------------------------------------------------------------------------------#
# Name:   endian                                                                                   #
# Author: Randy Johnson                                                                            #
# Descr:  Prints contents of the V$TRANSPORTABLE_PLATFORM view.                                    #
#                                                                                                  #
# Date       Ver. Who              Change Description                                              #
# ---------- ---- ---------------- -------------------------------------------------------------   #
# 03/06/2015 1.00 Randy Johnson    Initial write.                                                  #
# 06/12/2020 3.01 Randy Johnson    Reset header formatting.                                        #
#--------------------------------------------------------------------------------------------------#


# --------------------------------------
# ---- Main Program --------------------
# --------------------------------------
if (__name__ == '__main__'):
  Cmd            = basename(argv[0]).split('.')[0]
  CmdDesc        = 'Endian'
  Version        = '3.01'
  VersionDate    = 'Fri Jun 12 22:00:50 CDT 2020'
  DevState       = 'Production'
  Banner         = CmdDesc + ': Release ' + Version + ' '  + DevState + '. Last updated: ' + VersionDate
  Sql            = ''
  SqlHeader      = '/***** ' + CmdDesc.upper() + ' *****/'
  ErrChk         = False
  InStr          = ''
  TnsName        = ''
  Username       = ''
  Password       = ''
  ConnStr        = ''
  
  # For handling termination in stdout pipe; ex: when you run: oerrdump | head
  signal(SIGPIPE, SIG_DFL)

  # Process command line options
  # ----------------------------------
  Usage  =  '%s [options]'  % Cmd
  Usage += '\n\n%s'         % CmdDesc
  Usage += '\n-------------------------------------------------------------------------------'
  Usage += '\nReport endian orientation of OS platforms known to the database.'
  ArgParser = OptionParser(Usage)

  ArgParser.add_option('--s', dest='Show',     action='store_true', default=False,           help="print SQL query.")
  ArgParser.add_option('--v', dest='ShowVer',  action='store_true', default=False,           help="print version info.")

  # Parse command line arguments
  Options, args = ArgParser.parse_args()

  exit(0)
# --------------------------------------
# ---- End Main Program ----------------
# --------------------------------------
