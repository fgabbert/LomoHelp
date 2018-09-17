# Let's try to make Lomo's life easier.
# FKG - fischergabbert@yahoo.com

import os
import csv
import json
import tkinter as tk
import requests
import facebook
from tkinter import messagebox as msg
from tkinter import simpledialog as sdg
from tkinter import ttk
from pathlib import Path
from urllib.request import urlopen
#_________________________________________________________________________________________________________________________________________________#

import LomoClients
Clients = LomoClients.Clients

#_________________________________________________________________________________________________________________________________________________#
justBuildMasters = 0
# Loop through the clients and build spreadsheets
for client in Clients:
    url_link="http://"+ client['Name']+client['Ext']+"/wp-json/wp/v2/posts/"
    request = requests.get(url_link)
    if request.status_code != 200:
        print('Couldnt get to blog posts! Skipping '+ client['Name'])
        continue
    graph = facebook.GraphAPI(access_token="EAAGyZBb0Wu50BAP5U7X7D0qndoRZALbtcZA9cZA0UuHxW0eYiLUshm5hKF7PVLDsKoeTXqEqUqsxIsMUUqp6Rv5SSUmycBkbuuRLXQybThZCVvM3UIGrqeh9eCEO9sZC5oCc8UoLvmfZAQnHP11Gr2YxJyxaeKS7Cak2SnAHgzSegZDZD", version="2.12")

    # Load Master Blog spreadsheet
    masterfile = Path(client['Name'] + "_master.csv")
    if masterfile.is_file() == 0:
        print('No Master File Found! \nCreating Master CSV for '+client['Name'])
        with open(masterfile, 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=' ',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow(['Title'] + ['Link'])

    with open(masterfile) as csv_file:
        csv_reader   = csv.reader(csv_file, delimiter=',')
        line_count   = 0
        post_ids     = []
        new_post_ids = []
        # Loop through rows and build structure of blog post IDs
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                post_ids.append(row[1])
                line_count += 1
        #print('Rows in Master: ' + str(len(post_ids)))


    # Now read in all of the blog posts off of the website and look for new posts. Added ping test
    url_link="http://"+ client['Name'] +client['Ext']+"/wp-json/wp/v2/posts/"
    print('Checking ' + client['Name'] + ' for new blog posts...')

    # Write the blog posts to a temporary text file until I make this more elegant
    with urlopen(url_link) as url:
        data = url.read()
    filename = client['Name'] + "_posts_temp .txt"
    file_ = open(filename, 'wb')
    file_.write(data)
    file_.close()

    def save_to_file (fn, row, fieldnames):
             if (os.path.isfile(fn)):
                 m="a"
             else:
                 m="w"
             with open(fn, m, encoding="utf8", newline='' ) as csvfile:
                 writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                 if (m=="w"):
                     writer.writeheader()
                 writer.writerow(row)

    # Now read in the text file and parse the JSON from it for the Title and URL
    with open(filename) as json_file:
        json_data = json.load(json_file)

    for n in json_data:
      r={}
      r["Title"] = n['title']['rendered']
      r["Link"] = n['guid']['rendered']
      thispost = n['guid']['rendered']
      new_post_ids.append(r)

    # Delete the temp file used to parse JSON data for good housekeeping
    os.remove(filename)

    # Now loop through the blog posts from the website and see if there are any that don't exist in the master file
    unmatched_posts = []
    for newpost in new_post_ids:
        match_found = 0
        for post in post_ids:
            link  = newpost["Link"]
            if link[link.find("=")+1:len(link)] == post[post.find("=")+1:len(post)]:
                match_found = 1
                break
            else:
                continue
        if match_found:
            continue
        else:
            print('New Post Found: ' + newpost["Title"])
            unmatched_posts.append(newpost)
    if len(unmatched_posts) == 0:
        print('No new blog posts for ' +client['Name']+ ', Lomo!')

    # Append any new posts to the master stylesheet
    for post in unmatched_posts:
        print('Writing '+post["Title"]+' to the Master file.')
        save_to_file (masterfile, post, ['Title', 'Link'])
        # As Lomo for new facebook status for related blog post
        if justBuildMasters != 1:
            blogContent = input('Text file name for status for: \''+ post['Title']+'\'?')
            statusfile = Path(blogContent + ".txt")
            if statusfile.is_file() == 0:
                print('No Status File Found! \n Check the link?')
                continue
            txtstatus = open(statusfile,'r')
            statustext = txtstatus.read()
            graph.put_object(
                parent_object=277429155607359,
                connection_name="feed",
                message=statustext,
                link=post["Link"])
