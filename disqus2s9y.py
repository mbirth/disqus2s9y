#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import datetime
import json
import sqlite3
import sys
from pprint import pprint

DISQUS_FILES = ["DISQUS1.json", "DISQUS2.json"]


mappings = {}
with open("disqus2s9y.csv", "rt") as f:
    for row in csv.DictReader(f):
        if not row["s9y_entry_id"]:
            # Skip lines without entry_id
            continue
        mappings[row["disqus_url"]] = row["s9y_entry_id"]

print("Found {} mappings in disqus2s9y.csv.".format(len(mappings)))

comments = []
for filename in DISQUS_FILES:
    with open(filename, "rt") as f:
        response = json.load(f)
        comments += response["response"]

print("Found {} comments in {} file(s).".format(len(comments), len(DISQUS_FILES)))

# Sort
print("Sorting comments by timestamp ascending.")
comments = sorted(comments, key=lambda c: c["createdAt"])

db = sqlite3.connect("serendipity.db")
cursor = db.cursor()


def insert_dict(db_cursor, table, data):
    fields = []
    placeholders = []
    values = []
    for k, v in data.items():
        fields.append(k)
        placeholders.append("?")
        values.append(v)
    sql = "INSERT INTO {} ({}) VALUES ({})".format(table, ", ".join(fields), ", ".join(placeholders))
    db_cursor.execute(sql, values)
    return db_cursor.lastrowid

def sanitise_text(message):
    # This is for Markdown as I'm using the Markdown plugin
    message = message.replace("<code>", "`").replace("</code>", "`")
    message = message.replace("\n", "  \n")
    return message


disqus_to_s9y_id = {}
for c in comments:
    c_url = c["thread"]["link"]
    if not str(c_url) in mappings:
        print(f"ERROR: Can't map {c_url} to Serendipity page. Check disqus2s9y.csv!")
        continue
    parent_id = 0
    if c["parent"]:
        if not str(c["parent"]) in disqus_to_s9y_id:
            print("ERROR: DISQUS Parent ID {} not found.".format(c["parent"]))
            sys.exit(255)
        parent_id = disqus_to_s9y_id[str(c["parent"])]

    author_email = ""
    if "email" in c["author"]:
        author_email = str(c["author"]["email"])

    author_url = ""
    if "url" in c["author"]:
        author_url = str(c["author"]["url"])

    new_comment = {
        "entry_id": mappings[c_url],
        "parent_id": parent_id,
        "timestamp": int(datetime.datetime.fromisoformat(c["createdAt"]).timestamp()),
        "title": "",
        "author": c["author"]["name"],
        "email": author_email,
        "url": author_url,
        "ip": c["ipAddress"],
        "body": sanitise_text(c["raw_message"]),
        "type": "NORMAL",
        "subscribed": "false",
        "status": "approved",
        "referer": ""
    }

    new_rowid = insert_dict(cursor, "comments", new_comment)
    disqus_to_s9y_id[c["id"]] = new_rowid
    print("Inserted comment with id {}".format(new_rowid))

cursor.close()
db.commit()
db.close()
