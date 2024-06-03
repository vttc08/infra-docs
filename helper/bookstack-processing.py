#!/usr/bin/env python3

import os
import re
import urllib.request

# === Variables ===
bookshelf = "Bookshelf" # the local directory of downloaded markdown files

image_regex = r"!\[.*\]\((.*)\)" # regex to find image links in markdown files
regex_scaled = r"(\(https*:\/\/.*scaled*.*\.png\))(])" # remove scaled images
regex_clean = r"\[!\[.*\]\]" # cleanup markdown files
regex_link = r'\((https://bookstack.link/books/.*/page.*[^.png])\)' # find links in markdown files

# Change and rename markdown files
for root, dirs, files in os.walk(bookshelf):
    for file in files:
        if file.endswith(".md"):
            os.rename(os.path.join(root, file), os.path.join(root, file.replace(" ", "-").replace(",","").replace("(","").replace(")","").lower()))
            # replace spaces, commas, and parentheses with hyphens and lowercase the filename

pages = [] # list of path to markdown files
for root, dirs, files in os.walk(bookshelf):
    for file in files:
        if file.endswith(".md"):
            pages.append(os.path.join(root, file))

for page in pages:
    print(f"Processing {page}")
    with open(page, "r") as f:
        page_content = f.read()
        dir = os.path.dirname(page) # get the directory of the markdown file
        dl_path = f'{dir}/assets'
        image_urls = re.findall(image_regex, page_content)
        try: 
            os.mkdir(dl_path)
        except FileExistsError: pass
        for url in image_urls: # download images and replace the url with the local path
            directory = "/".join(url.split("/")[-3:-1])
            filename = "/".join(url.split("/")[-3:])
            os.makedirs(f"{dl_path}/{directory}", exist_ok=True)
            filepath = f"{dl_path}/{filename}"
            urllib.request.urlretrieve(url, filepath)
            new_url = f"assets/{filename}"
            page_content = page_content.replace(url, new_url)

        # Fix inconsistencies in the markdown files with how bookstack handles scaled images
        page_content = re.sub(regex_scaled, "]", page_content)
        page_content = re.sub(regex_clean, "![]", page_content)

        # Convert bookstack links to markdown local links
        for found in re.findall(regex_link, page_content):
            relist = found.split("/")
            folder = relist[-3]
            for book in os.listdir(bookshelf):
                if folder == book.replace(" ", "-").lower():
                    folder = book
                    folder = folder.replace(" ", "%20") # obsidian uses %20 for spaces in links
            page_name = relist[-1]
            constructed_path = f"/{folder}/{page_name}" # "/folder/page.md" is recognized by both obsidian and mkdocs
            # todo: only link page_name because mkdocs has plugin roamlinks that auto convert links
            page_content = page_content.replace(found, f"{constructed_path}")
    with open(page, "w") as f:
        f.write(page_content)
        print(f"Finished processing {page}")