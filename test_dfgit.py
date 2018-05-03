# import dfgit
# import unittest
#
# class GitInit(unittest.TestCase):
#     """test repo init functionality"""
#
#     def test_init(self):
import os
from dfgit import init
import sys
import io
import subprocess
from contextlib import redirect_stdout
# repo_url = "https://rhiggins@rndwww.nce.amadeus.net/git/scm/~rhiggins/df_history.git"
# repo_url = "https://rhiggins@rndwww.nce.amadeus.net/git/scm/~mvrabie/vita.git"
# init(repo_url)

ff = os.popen("git config --file .gitmodules --get-regexp path ").read()
submodules = ff.split('\n')
for sub in submodules:
    print(sub.split())