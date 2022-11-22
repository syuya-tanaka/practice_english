"""Module for path resolution of 'sql directory'"""
import os
import sys


# importされた瞬間に実行されるようにしている。
sys.path.append((os.path.dirname(__file__) + '/sql'))
