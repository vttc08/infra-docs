# Find the most recently updated files in a directory based on frontmatter and update the documentation index markdown file

import os
import frontmatter
import datetime

dir = '!documentation'

filedict = {}

def find_and_update(path):
    """Find the update date of a file and add it to the filedict dictionary."""
    post = frontmatter.load(path)
    try:
        update = post.metadata['update'].timestamp()
    except KeyError:
        update = datetime.datetime.now().timestamp()
    filedict[path] = update

for root, dirs, files in os.walk(dir):
    for file in files:
        if file.endswith('.md') and '.obsidian' not in root and file != "index.md":
            path = os.path.join(root, file)
            find_and_update(path)

# Sorting the dictionary by the values and reversing it to get the most recent files
sorted_files = {k: v for k, v in sorted(filedict.items(), key=lambda item: item[1])}
recent = list(sorted_files.keys())[-10:][::-1]

with open(f'{dir}/index.md', 'w') as f:
    f.write("# Home\n### Recent Updates\n\n")
    for file in recent:
        text = frontmatter.load(file).content.split('\n')[0].replace('# ', '') # first line is the title
        md = file.split('\\')[-1] # only the file name.md
        f.write(f"- [{text}]({md})\n")