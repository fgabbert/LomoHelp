# Let's try to make Lomo's life easier.
# FKG - fischergabbert@yahoo.com
import os
import csv
import json
import requests
from urllib.request import urlopen


# Set up Lomo's Clients
#Clients = ['valderramaortho','321boatclub','moongolf'];
Clients = ['valderramaortho'];

# Loop through the clients and build spreadsheets
for client in Clients:

    # Load Master Blog spreadsheet
    masterfile = client + "_master.csv"
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


    # Now read in all of the blog posts off of the website and look for new posts
    url_link="http://"+ client +".com/wp-json/wp/v2/posts/"
    print('Checking ' + client + ' for new blog posts...')

    # Write the blog posts to a temporary text file until I make this more elegant
    with urlopen(url_link) as url:
        data = url.read()
    filename = client + "_posts_temp .txt"
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
    #print('I found: '+ str(len(new_post_ids))+ ' blog posts on the website.')

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
        print('No new blog posts for ' +client+ ', Lomo!')
    #TODO: for any unmatched post, prompt Lomo to enter a FB status and then post the blog post link to FB
    #

    # Append any new posts to the master stylesheet
    for post in unmatched_posts:
        print('Writing '+post["Title"]+' to the Master file.')
        save_to_file (masterfile, post, ['Title', 'Link'])
