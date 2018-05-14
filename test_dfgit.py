import dfgit
import click
from click.testing import CliRunner
import unittest
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


# ff = os.popen("git config --file .gitmodules --get-regexp path ").read()
# submodules = ff.split('\n')
# for sub in submodules:
#     print(sub.split())

# def test_init():
#     runner = CliRunner()
#     result = runner.invoke(dfgit.init, ["git@github.com:higginsro/gtest.git","gtest"])
#     assert result==None, "nope"
#     print(result.output)
# cli()

print(dfgit.find_submodules())
# already existing repo
# dfgit.init("https://github.com/higginsro/gtest.git","sv_scratch")
# print('saving current state of sv_scratch')
# dfgit.save_state(True,True, 'sv_scratch')
# WORKS as of 14/05/2018 v1 api still

# print('trying load_state for sv_scratch')
# dfgit.load_state('sv_scratch')
# works as of 14/05/2018
# new agent
#dev_key = 648e5dadfa00426f9ecdcf02d024d991
dfgit.init("https://github.com/higginsro/sv_git_test.git",'sv_git_test')


# dfgit.environment_valid()

# dfgit.save_state(True, True)

# dfgit.load_state()
# test_init()