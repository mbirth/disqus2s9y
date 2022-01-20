#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sqlite3
from os.path import basename

# 1. Match URLs from JSON to permalinks/entries in SQLite
# 2. Sort JSON comments old-to-new
# 3. After writing comment into SQLite, store new SQLite-ID and Disqus-ID (for threads)

DISQUS_FILES = ["DISQUS1.json", "DISQUS2.json"]

comments = []

for filename in DISQUS_FILES:
    with open(filename, "rt") as f:
        response = json.load(f)
        comments += response["response"]

print("Found {} comments in {} file(s).".format(len(comments), len(DISQUS_FILES)))

old_urls = []
for c in comments:
    #old_urls += c["thread"]["identifiers"]
    old_urls.append(c["thread"]["link"])

old_urls = list(set(old_urls))

print("Found {} unique URLs.".format(len(old_urls)))

with open("disqus2s9y.csv", "wt") as f:
    f.write("\"disqus_url\",\"disqus_title\",\"s9y_entry_id\"\n")
    for ou in old_urls:
        old_name = basename(ou).replace(".html", "")
        f.write("\"{}\",\"{}\",\n".format(ou, old_name))


db = sqlite3.connect("serendipity.db")
req = db.execute("SELECT permalink, entry_id FROM permalinks WHERE type='entry'")
response = req.fetchall()


with open("s9y_urls.csv", "wt") as f:
    f.write("\"s9y_title\",\"s9y_url\",\"entry_id\"\n")
    for r in response:
        (url, entry_id) = r
        name = basename(url).replace(".html", "")
        f.write("\"{}\",\"{}\",{}\n".format(name, url, entry_id))


