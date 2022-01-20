disqus2s9y
==========

DISQUS to Serendipity importer.


Usage
-----

Fetch all the comments from your site using the Disqus API. Basically go
into your admin area, go to the "Moderate" section and check the HTTP
requests.

You should find something going to `https://disqus.com/api/3.0/posts/list`.
It will return a JSON structure. In the section `cursor`, there's a value
`hasNext`. If that's `true`, do the request again but add the parameter
`cursor` with the value from the `next` key to it. This will get you the
next bunch of comments. Rinse and repeat until you got everything.

Now copy all the files into the directory with these scripts and add
their names to the `DISQUS_FILES` variable in the Python scripts.

Also download your Serendipity SQLite database into the directory as `serendipity.db`.

Now run `dump_urls_to_csv.py` to create 2 CSV files. One is `disqus2s9y.csv`
which contains all the URLs from your DISQUS dump and an empty column
`s9y_entry_id`. The second file is `s9y_urls.csv` which contains all the
URLs from your Serendipity database.

The important step is now to match both, i.e. DISQUS-URL to Serendipity
entry_id. Fill in the matching entry_id into the `s9y_entry_id` column.

After you're done, run `disqus2s9y.py` and it should import all comments
into your `serendipity.db`. Afterwards copy that back to the server and
you're done.
