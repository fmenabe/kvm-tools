# -*- coding: utf-8 -*-

import os
import sys
import getpass
import yaml
import kvm
from unix.utils import kb2gb, gb2kb

ROOT =  os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MODELS =  yaml.load(open(os.path.join(ROOT, 'conf', 'models.yml')))


class ResourceError(Exception):
    pass


class QuitOnError(Exception):
    pass


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
            raise QuitOnError(msg)


    def info(self, msg, prompt='', quit=False):
        self.logger.info('(%s) %s' % (prompt, msg) if prompt else msg)
        if quit:
            raise QuitOnError(msg)


    def warn(self, msg, prompt='', quit=False):
        self.logger.warn('(%s) %s' % (prompt, msg) if prompt else msg)
        if quit:
            raise QuitOnError(msg)


    def error(self, msg, prompt='', quit=False):
        self.logger.error('(%s) %s' % (prompt, msg) if prompt else msg)
        if quit:
            raise QuitOnError(msg)


def check_memory(host, memory):
    vms_memory = sum([host.conf(guest)['memory']
        for guest in host.vms if host.state(guest) == kvm.RUNNING])

    mem_diff = host.memory - vms_memory - gb2kb(memory)
    if mem_diff < 0:
        raise ResourceError('missing %.3f Gb' % kb2gb(float(-mem_diff), False))


def check_storage(host, disks):
    # Get needed size for each partition.
    partitions = {}
    for disk in disks:
        partition = host.execute(
            'df -k %s' % os.path.dirname(disk['path'])
        )[1].split('\n')[1].strip().split()[5]
        partitions.setdefault(partition, 0)
        partitions[partition] += disk['size']

    for partition, needed_size in partitions.iteritems():
        available_size = kb2gb(host.execute('df -k %s' % partition)[1]
            .split('\n')[1].strip().split()[3])
        if needed_size >= available_size:
            raise ResourceError(
                "missing %dG on '%s'" % (needed_size - available_size, partition))
