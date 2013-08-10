# -*- coding: utf-8 -*-

import os
import getpass
import yaml
import sys


class Logger(object):
    def __init__(self, name, loglevel, logfile):
        # Create log directory if not exists.
        logdir = os.path.dirname(logfile)
        if not os.path.exists(logdir):
            try:
                os.makedirs(logdir)
            except OSError as oserr:
                print("Unable to create log directory: %s" % oserr)
                sys.exit(1)

        # Initialize logger
        import logging
        self.logger = logging.getLogger(name)
        self.logger.setLevel(loglevel.upper())

        # Add file handler.
        file_formatter = logging.Formatter(
            '%(asctime)s '+ getpass.getuser() +' %(levelname)s: %(message)s'
        )
        file_handler = logging.FileHandler(logfile)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Add console handler.
        cli_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s'
        )
        cli_handler = logging.StreamHandler()
        cli_handler.setFormatter(cli_formatter)
        self.logger.addHandler(cli_handler)


    def debug(self, msg, prompt='', quit=False):
        self.logger.debug('(%s) %s' % (prompt, msg) if prompt else msg)
        if quit:
            sys.exit(0)


    def info(self, msg, prompt='', quit=False):
        self.logger.info('(%s) %s' % (prompt, msg) if prompt else msg)
        if quit:
            sys.exit(0)


    def warn(self, msg, prompt='', quit=False):
        self.logger.warn('(%s) %s' % (prompt, msg) if prompt else msg)
        if quit:
            sys.exit(1)


    def error(self, msg, prompt='', quit=False):
        self.logger.error('(%s) %s' % (prompt, msg) if prompt else msg)
        if quit:
            sys.exit(1)
