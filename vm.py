#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import clg

OPTIONS_FILE = os.path.join(os.path.dirname(__file__), 'conf', 'options.yml')
try:
    OPTIONS = yaml.load(open(OPTIONS_FILE), Loader=clg.YAMLOrderedDictLoader)
except Exception as exc:
    print("Unable to load command-line configuration: %s" % exc)
    sys.exit(1)

def main():
    parser = clg.CommandLine(OPTIONS)
    parser.parse()

if __name__ == '__main__':
    main()
