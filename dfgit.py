#!/bin/python3
# Authored by Joshua Hurt 05/08/17
# altered by RH
import os
import requests
import click
from git import Repo
import json
import configparser
from time import gmtime, strftime
import shutil
DF_HEADERS = None
BASE_URL = 'https://api.dialogflow.com/v1/'
# DEV_KEY = '605918452fca446e8518703aa4750c0e'
# DEV_TOKEN_ENV_NAME = 'DF_DEV_TOKEN'
# DF_HISTORY_DIR = 'df_history'
# DF_REPO = os.path.join(os.getcwd(), DF_HISTORY_DIR)
DF_REPO = None
AGENT_DIR = None
DEV_KEY = None


@click.group()
def cli():
    pass

# @cli.command()
# @click.argument('repo_name')
# @click.argument('dev_token')
def create_new(repo_name, dev_token):
    """
    Creates new git repository for storing an agent's entities and intents.
    For clarity, naming of repo should match agent's name on DF.
    :return: 
    """
    pass
@cli.command()
@click.argument('repo_url')
@click.argument('agent_name') #formerly DF_HISTORY_DIR
def init(repo_url, agent_name):
    """
    Clones submodule (separate repo) to keep track of dialogflow.com history separately. This is required before use.
    """
    # TODO(jhurt): Handle private repos by using user's Github credentials
    # try:
    #     if requests.get(repo_url).status_code != 200:
    #         print('Cannot reach this URL. Terminating.')
    #         return
    # except Exception:
    #     # Likely a malformed URL, but requests can throw any number of different URL related Exceptions, so catch all
    #     print('Likely a malformed URL. Terminating.')
    #     return
    if not repo_url:
        print("no repo url supplied.\n"
              "Usage: dfgit.py init <existing git repo url to store DF agent intents and entities> <agent_name>")
        return
    # repo = Repo(os.getcwd())
    print('git submodule add {} {}'.format(repo_url, agent_name))
    os.system('git submodule add {} {}'.format(repo_url, agent_name))
    config = configparser.ConfigParser()
    # if config file exists already
    config.read('agents.ini')
    if agent_name not in config:
        config[agent_name] = {'agent_name':agent_name,
                           'dev_token':input("{}'s dev token: ".format(agent_name)),
                           'git_repo':repo_url
                           }
        with open('agents.ini','w') as configfile:
            config.write(configfile)
    # repo.create_submodule(DF_HISTORY_DIR, '{}\\{}'.format(os.getcwd(), DF_HISTORY_DIR), url=repo_url, branch='master')
    print('Submodule added. You may now save/load your state from/to Dialogflow')

@cli.command()
@click.argument('agent_name')
def rm_agent(agent_name):
    """
    !DANGER! deletes submodule of an agent from this repo.
    :return:
    """
    conf = configparser.ConfigParser()
    conf.read("agents.ini")
    if agent_name in conf:
        del conf[agent_name]
        with open("agents.ini", "w") as f:
            conf.write(f)
        print("removing {} from agents.ini".format(agent_name))
    if agent_name in find_submodules():
        os.system('git rm {}'.format(agent_name))
        path = os.path.join(".git", "modules", agent_name)
        shutil.rmtree(path)
        print("deleted "+agent_name)


@cli.command()
@click.option('--commit', is_flag=True, help='Automatically commit the saved state.')
@click.option('--push', is_flag=True, help='Automatically push (and commit) the saved state')
@click.option('--delta', default=None, type=str, help='commit message')
@click.argument('agent_name')
def save_state(push, commit, agent_name, delta):
    """
    Saves dialogflow.com agent's state (Intents/Entities) as json files
    """
    return save_state_internal(push, commit, agent_name, delta=delta)

def save_state_internal(push, commit, agent_name, delta=None):
    """
    Saves dialogflow.com agent's state (Intents/Entities) as json files
    """
    if not environment_valid(agent_name):
        return
    print('Saving entire state!')
    intents = get_resource_dict('intents')
    entities = get_resource_dict('entities')
    intents_path = os.path.join(agent_name, 'intents.json')
    entities_path = os.path.join(agent_name, 'entities.json')
    with open(intents_path, 'w', encoding='utf-8') as f, open(entities_path, 'w', encoding='utf-8') as f2:
        json.dump(intents, f, ensure_ascii=False, indent=4, sort_keys=True)
        json.dump(entities, f2, ensure_ascii=False, indent=4, sort_keys=True)
    os.chdir(AGENT_DIR)
    os.system('git add {} {}'.format('intents.json', 'entities.json'))
    print("in {}".format(os.getcwd()))
    if not delta and push:
        delta = input("Commit message: ")
    message = '"{} {}"'.format(strftime("%d-%m-%Y %H:%M", gmtime()), delta)
    if push or delta:
        commit = True
    if commit:
        os.system('git commit -m {}'.format(message))
    if push:
        os.system('git push')
    os.chdir('..')

def load_state_internal(agent_name, commit_hash=None):
    """
    Restores state of all Intents/Entities from a commit hash to dialogflow.com
    """
    if not environment_valid(agent_name):
        print('env not valid ..')
        return
    repo = Repo(DF_REPO)
    target_commit = None
    # Get the Commit object based on the hash user provided
    if commit_hash:
        for c in repo.iter_commits():
            if c.hexsha == commit_hash:
                target_commit = c
                break
    # User didn't provide a commit hash so show last 10 for them to choose from
    if not commit_hash:
        # Show last 10 commits from CURRENT BRANCH
        commits = list(repo.iter_commits(max_count=10))
        for i, commit_obj in enumerate(commits):
            print("({})  {}  {}".format(i, commit_obj.hexsha, commit_obj.message))
        try:
            num_pressed = int(input("Press number corresponding to which commit you'd like to load the state from: "))
            if 0 <= num_pressed <= min(len(commits) - 1, 9):
                target_commit = commits[num_pressed]
            else:
                raise ValueError
        except ValueError:
            print('Enter a value between 0-{}. Terminating.'.format(min(len(commits) - 1, 9)))
            return

    print('Loading entire state! Please be patient.')
    intents, entities = None, None
    # TODO(jhurt): make this only iterate through the dialogflow.com specific pickle files.
    # Maybe put them in their own directory and limit the "tree" path to blobs in that path?
    for b in target_commit.tree.blobs:
        if b.name == "intents.json":
            intents = json.loads(b.data_stream.read().decode('utf-8'))
        if b.name == "entities.json":
            entities = json.loads(b.data_stream.read().decode('utf-8'))

    sync_api_ai(intents, entities)
    print('Refresh the dialogflow.com dashboard to see changes')
    # TODO update repo to reflect restore

@cli.command()
@click.option('--commit-hash', default=None, help="A commit hash to make the state of dialogflow.com match.")
@click.argument('agent_name')
def load_state(agent_name, commit_hash=None):
    """
    Restores state of all Intents/Entities from a commit hash to dialogflow.com
    """
    return load_state_internal(agent_name, commit_hash)


@cli.command()
@click.argument('master_agent')
@click.argument('dev_agent')
def overwrite(master_agent, dev_agent):
    '''
    saves current state of both agents,
    and overwrites master_agent with current dev_agent by copying locally..
    and
    :param master_agent:agent to be overwritten
    :param dev_agent: agent that is overwriting
    :return:None
    '''
    # saving current versions of both
    print("saving prior to overwrite")
    saving_message = "Save prior to overwriting {} with {}".format(dev_agent, master_agent)
    save_state_internal(push=True, commit=True, agent_name=master_agent, delta=saving_message)
    save_state_internal(True, True, agent_name=dev_agent, delta=saving_message)

    # local overwrite
    shutil.copy(dev_agent+'/intents.json', master_agent+'/intents.json')
    shutil.copy(dev_agent+'/entities.json', master_agent+'/entities.json')
    # push local master_agent
    os.chdir(master_agent)
    os.system('git add {} {}'.format('intents.json', 'entities.json'))
    delta = 'overwriting this agent with {}'.format(dev_agent)
    message = '"{} {}"'.format(strftime("%d-%m-%Y %H:%M", gmtime()), delta)
    os.system('git commit -m {}'.format(message))
    os.system('git push')

    os.chdir('..')

    # pushing changes to DF for master_agent
    load_state_internal(master_agent, commit_hash=get_latest_commit_hash(master_agent))

@cli.command()
def list_agents():
    '''
    lists DF agents currently tracked by this repo in submodules
    '''
    conf = configparser.ConfigParser()
    conf.read('agents.ini')
    for agent_name in conf:
        if agent_name != 'DEFAULT':
            print(agent_name)


def sync_api_ai(old_intents, old_entities):
    cur_intents = get_resource_dict('intents')
    cur_entities = get_resource_dict('entities')
    cur_intents_ids = { x['id'] for x in cur_intents.values() }
    cur_entities_ids = { x['id'] for x in cur_entities.values() }

    # TODO(jhurt): Currently deleting everything then recreating everything due to odd behavior regarding IDs.
    # Make this more efficient cuz numerous or large Intents/Entities could take a long time to send over the network.

    # DELETE all current Intents
    for intent_id in cur_intents_ids:
        requests.delete(BASE_URL +'intents/' + intent_id, headers=DF_HEADERS)

    # DELETE all current Entities
    for entity_id in cur_entities_ids:
        requests.delete(BASE_URL +'entities/' + entity_id, headers=DF_HEADERS)

    # CREATE all old Intents (will have new IDs now but that's okay)
    for intent in old_intents.values():
        # Intent object can't have the 'id' attribute for a POST
        if intent.get('id') is not None:
            del intent['id']
        requests.post(BASE_URL +'intents', headers=DF_HEADERS, json=intent)

    # CREATE all old Entities (will have new IDs now but that's okay)
    for entity in old_entities.values():
        # Entity object can't have the 'id' attribute for a POST
        if entity.get('id') is not None:
            del entity['id']
        requests.post(BASE_URL +'entities', headers=DF_HEADERS, json=entity)

def get_resource_dict(resource):
    """
    Meh.
    :param resource: either 'intents' or 'entities' as of right now
    :return: dict in form { 'id' : resource_dict }
    """
    resource_json = requests.get(BASE_URL + resource, headers=DF_HEADERS).json()
    resources = {}
    for d in resource_json:
        resources[d['id']] = requests.get(BASE_URL + resource +'/' + d['id'], headers=DF_HEADERS).json()
    return resources

def environment_valid(agent_name):
    global DF_HEADERS
    global BASE_URL
    global DEV_KEY
    global DEV_TOKEN_ENV_NAME
    global AGENT_DIR
    global DF_REPO
    DF_REPO = os.path.join(os.getcwd(), agent_name)
    # DEV_KEY = os.getenv(DEV_TOKEN_ENV_NAME)
    config = configparser.ConfigParser()
    config.read('agents.ini')
    if agent_name not in config:
        print("{} not found in agents.ini config file. ".format(agent_name))
        print("Before save_state try running: dfgit.py init <repo_url> <agent_name>")
        return False
    else:
        AGENT_DIR = config[agent_name]['agent_name']
        DEV_KEY = config[agent_name]['dev_token']
    if DEV_KEY is None:
        print("Please set environment variable for agent {}".format(agent_name))
        return False
    DF_HEADERS = {'Authorization' : 'Bearer {}'.format(DEV_KEY)}

    if AGENT_DIR not in find_submodules():
        print("Re-run tool with 'init <REPO_URL>' command where <REPO_URL> is a "
              "public Github/bitbucket repo where you would like to save your dialogflow history.")
        return False
    return True
# @cli.command()
def find_submodules():
    ff = os.popen("git config --file .gitmodules --get-regexp path ").read()
    assert ff, "no submodules found"
    submodules = [line.split()[-1] for line in ff.strip().split('\n')]
    # print(submodules)
    return submodules

def get_latest_commit_hash(target_dir=None):
    if target_dir:
        os.chdir(target_dir)
    ff = os.popen('git log --date=format:"%d-%m-%Y %H:%M:%S" --pretty=format:"%H, %cn, %ad, %s"').read()
    assert ff, "no commits found"
    commits = [line.split(', ') for line in ff.strip().split('\n')]
    latest_commit_hash = commits[0][0]
    latest_commit_message = commits[0][-1]
    print("retrieving commit {} {}".format(latest_commit_hash,latest_commit_message))
    if target_dir:
        os.chdir('..')
    return latest_commit_hash

if __name__ == '__main__':
    cli()