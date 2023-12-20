#!/usr/bin/python3
# Copyright 1999-2023. Plesk International GmbH. All rights reserved.

import sys

import pleskdistup.main
import pleskdistup.registry

import ubuntu18to20.upgrader

if __name__ == "__main__":
    pleskdistup.registry.register_upgrader(ubuntu18to20.upgrader.Ubuntu18to20Factory())
    sys.exit(pleskdistup.main.main())
