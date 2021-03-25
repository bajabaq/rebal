#rebal_aux.py

#auxillary functions for the rebal code

#------------------------------------------------------------------------------
#python imports
#------------------------------------------------------------------------------
import logging

#------------------------------------------------------------------------------
#user imports
#------------------------------------------------------------------------------
from rebal.tadconfig import tadconfig

#------------------------------------------------------------------------------
#global variables
#------------------------------------------------------------------------------
logger = logging.getLogger(__name__)

#==============================================================================
#SUBROUTINES
#==============================================================================
#--------------------------------------------------------------------------------
#return the logger handle
#--------------------------------------------------------------------------------
def setup_logging(log_location):
    level     = tadconfig.get_setting("rebal","log_level",type="string")
    log_level = "logging." + level
    logging.basicConfig(filename=log_location, filemode='w', format='%(asctime)s %(levelname)-8s %(filename)s %(funcName)s() %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')
    logging.getLogger().setLevel(eval(log_level))  #set the level based on settings file
    logger = logging.getLogger(__name__)
    logger.info('Logging started for this run')
    return logger
#enddef
