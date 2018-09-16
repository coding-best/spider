################################################################################
#
# This module provide log init, for log format and others.
#
################################################################################

#!/usr/bin/env python

import os
import logging.handlers

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_DIR = BASE_DIR + '/log'
LOG = LOG_DIR + '/spider.log'
LOG_FORMAT = "%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d -- %(message)s"  # %(thread)d
LOG_BACKUP_FORMAT = '%m-%d %H:%M:%S'

def init_log(level=None, when=None, backup=None, logformat=None, datefmt=None):
    """
    init_log - initialize log module

    Args:
      level:        - msg above the level will be displayed
                      DEBUG < INFO < WARNING < ERROR < CRITICAL
                      the default value is logging.INFO
      backup        - how many backup file to keep
                      default value: 30
      logformat     - format of the log
                      default format:
                      %(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s
                      INFO: 12-09 18:02:42: log.py:40 * 139814749787872 HELLO WORLD

    Raises:
        OSError: fail to create log directories
        IOError: fail to open log file
    """
    if level is None:
        level = logging.DEBUG
    if when is None:
        when = 'D'
    if backup is None:
        backup = 30
    if logformat is None:
        logformat = LOG_FORMAT
    if datefmt is None:
        datefmt = LOG_BACKUP_FORMAT
    formatter = logging.Formatter(logformat, datefmt)
    logger = logging.getLogger()
    logger.setLevel(level)

    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)

    handler = logging.handlers.TimedRotatingFileHandler(LOG, when=when, backupCount=backup)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
