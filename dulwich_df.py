import os
from dulwich.repo import Repo

repo = Repo(os.getcwd())
index = repo.open_index()
print(list(index))
print(repo, type(repo))