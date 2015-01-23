#!/usr/bin/env python
# coding=utf-8
import sys
import os
from glancesync import GlanceSync

if __name__ == '__main__':
    glancesync = GlanceSync()
    glancesync.backup_glancemetadata()
