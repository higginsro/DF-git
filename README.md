# dialogflow-ai-git
### Reason for creation:
This is a CLI tool to version control intents and entities in dialogflow.com borne out of a frustration of having them constantly mangled by other team members without a way to rollback to a working version.

### List of supported actions:
* List agents being tracked in repos currently
* Save current state of all Intents and Entities with the option to automatically commit and/or push the changes
* Load the state of Intents and Entities from a previous commit to dialogflow.ai
* Overwrite the Intents and Entities of one agent with another's.
* Remove an agent's repo as a submodule from this one
### Instructions for setup:
Clone this repo using:

```
> git clone --recursive https://rhiggins@rndwww.nce.amadeus.net/git/scm/~rhiggins/dialogflow-git.git
```
The --recursive flag is required to also copy the existing submodules\
They will be cloned but the HEAD of each submodule may be detached.\
To reattach navigate to the repo in question and use:

```
> git checkout master
```
#### Option 1 (No python installation required Windows only)
Use the dfgit.exe included in this repo in cmd:
```
~/DF-git>dfgit [OPTIONS] [COMMAND]
e.g. dfgit load_state <agent_name>
```
#### Option 2
Using Python 3.5.5
preferably in a virtual env use:
```
> pip install -r requirements.txt
```
if using conda you can create an env using the .yml file in this repo:
```
~/dialogflow-git> conda create -f df-git.yml
~/dialogflow-git> activate df-git   # on windows
~/dialogflow-git> source activate df-git # on unix
```

Check the list of agents currently being tracked using:
```
~/dialogflow-git> dfgit.py list_agents
```
Create a nonempty github/bitbucket repo for each agent you wish to have version control for
that isn't currently being tracked.\
Changes will be tracked in these repos.\
For example create first an empty repo on bitbucket and then locally:
```
mkdir some_agent
touch README.md
git init
git add *
git commit -m "Initial Commit"
git remote add origin <repo_url>
git push -u origin master
```

Clone each of these as a submodule in current repo using:
```
~/dialogflow-git> dfgit.py init <URL_to_repo> <agent_name>
```
You will be prompted for the agent's developer token only once.\
This can be found in the settings section of your agent dashboard on dialogflow

### Usage:
For more details about how to run a command use --help:
```
~/dialogflow-git> dfgit.py init --help
```
Save state of all Intents & Entities and commit
```
~/dialogflow-git> dfgit.py save_state --commit <agent_name>
```
You can commit and push by giving just the --push flag
```
~/dialogflow-git> dfgit.py save_state --push <agent_name>
```
you will be prompted for a commit message in both cases

Alternatively use --delta option to supply a commit message:
```
~/dialogflow-git> dfgit.py save_state --push --delta "4th commit" <agent_name>
```
Load a saved state from a specific commit hash
```
~/dialogflow-git> dfgit.py load_state --commit-hash 11edc81f6d2a1e9ede198b75a90d021124c5207b <agent_name>
```
Or you can pick from a list of up to the last 10 commits to load a state
```
~/dialogflow-git> dfgit.py load_state <agent_name>
(0)  2ee277719bff7d92ae4e27efd5ca2cb069e33fe3  # Intents: 3, # Entities: 1
(1)  fedb991cd6667e73c662ad74b03773955e189f9b  # Intents: 3, # Entities: 1
(2)  11edc81f6d2a1e9ede198b75a90d021124c5207b  test
(3)  520006c8aae7c632c7805c76f6668b27804813f9  Initial commit
Press number corresponding to which commit you'd like to load the state from:
```

Overwrite one bot with another .e.g. production bot with dev bot
```
~/dialogflow-git> dfgit.py overwrite <prod_bot> <dev_bot>
```
This will save and push the current state of both bots
and overwrite the <prod_bot> with the most recent version of the <dev_bot>

rm_agent removes a submodule from your local repo. Use with caution:
````
~/dialogflow-git> dfgit.py rm_agent <agent_name>
