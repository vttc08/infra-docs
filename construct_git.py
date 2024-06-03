"""
Windows Only, changes the system time to the date created of the file using win32api, commits the file to git
then changes the system time to the date updated of the file and commits the file to git again.
This is to make sure previous files that have a date created and updated in the frontmatter are
compatible with mkdocs=git-revision-date-localized plugin as mkdocs do not support frontmatter/metadata

This assumes you are using obsidian to edit the note not directly, but in another folder and you copy the 
files to the mkdocs documentation folder when you're ready to publish.
"""

import frontmatter
import os
import shutil
import subprocess
import win32api
import datetime

path = "!documentation" # mkdocs docs directory
original_dir = "C:/your/notes/" # original directory if using obsidian vault in another dir

def get_date(path, key):
    """ Get date created or updated from frontmatter metadata. Returns a datetime object."""
    post = frontmatter.load(path)
    try: 
        date = post.metadata[key]
    except KeyError:
        date = datetime.datetime.now()
    return date

def set_time(dt_object):
    """ Set the system time to the date created or updated of the file."""
    win32api.SetSystemTime(dt_object.year, dt_object.month, dt_object.weekday(), dt_object.day, dt_object.hour, dt_object.minute, dt_object.second, 0)

def run_command(command):
    """ Wrapper to run shell commands such as git """
    return subprocess.run(command, shell=True, capture_output=True).stdout.decode('utf-8')

def restore_original(path):
    """ Copy original files into the mkdocs documentas directory so git marks it as modified. """
    original_path = f"{original_dir}{path}"
    shutil.copy(path, original_path)

def git_flow(path, date):
    """ Run git add and commit commands. """
    run_command(f'git add "{path}"')
    run_command(f'git commit -m "Update {path} at {date}"')

for root, dirs, files in os.walk(path):
    for file in files:
        if file.endswith(".md") and '.obsidian' not in root:
            print(file)
            path = os.path.join(root, file)
            created = get_date(path,'date')
            updated = get_date(path,'update')
            set_time(created)
            git_flow(path, created)
            restore_original(path)
            set_time(updated)
            git_flow(path, updated)
            
