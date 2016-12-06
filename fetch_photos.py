#!/usr/bin/python
# -*- coding: UTF-8 -*-

import vk_auth
import json
import urllib2
from urllib import urlencode
import os
import getpass
import sys


def call_api(method, params, token):
    params.append(("access_token", token))
    url = "https://api.vk.com/method/%s?%s" % (method, urlencode(params))
    return json.loads(urllib2.urlopen(url).read())["response"]


def get_albums(user_id, token):
    return call_api("photos.getAlbums", [("uid", user_id)], token)


def get_photos_urls(user_id, album_id, token):
    photos_list = call_api("photos.get", [("uid", user_id), ("aid", album_id)], token)
    result = []
    for photo in photos_list:
        # Choose photo with largest resolution
        if "src_xxbig" in photo:
            url = photo["src_xxbig"]
        elif "src_xbig" in photo:
            url = photo["src_xbig"]
        else:
            url = photo["src_big"]
        result.append(url)
    return result


def get_photos_urls(user_id, token):
    photos_list = call_api("photos.getAll", [("uid", user_id), ("count", 200)], token)[1:]
    with open('response_getAll.json', 'w') as outfile:
        json.dump(photos_list, outfile)
    result = []
    print photos_list
    for photo in photos_list:
        print photo
        # Choose photo with largest resolution
        if "src_xxbig" in photo:
            url = photo["src_xxbig"]
        elif "src_xbig" in photo:
            url = photo["src_xbig"]
        else:
            url = photo["src_big"]
        result.append(url)
    return result


def get_messages(user_id, token):
    messages_history = call_api("messages.getHistory", [("uid", user_id), ("count", 200)], token)
    print messages_history
    results = []
    results += messages_history[1:]
    current_message_id = messages_history[-1]["mid"]
    print current_message_id
    while True:
        messages_history = call_api("messages.getHistory",
                                    [("uid", user_id), ("count", 200), ("start_message_id", current_message_id),
                                     ("rev", 1)], token)[1:]
        print messages_history
        if current_message_id == messages_history[0]["mid"]:
            print "Last message found:%s" % current_message_id
            break
        results += (messages_history[::-1])[1:]  # excludes count and first message
        current_message_id = messages_history[0]["mid"]
    print results
    with open('messages_getHistory_utf8' + user_id +'.json', 'w') as outfile:
        outfile.write(json.dumps(results, ensure_ascii=False).encode('utf8'))
    with open('messages_getHistory_unicode' + user_id +'.json', 'w') as outfile:
        json.dump(results, outfile)


def save_photos(urls, directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    names_pattern = "%%0%dd.jpg" % len(str(len(urls)))
    for num, url in enumerate(urls):
        filename = os.path.join(directory, names_pattern % (num + 1))
        print "Downloading %s" % filename
        open(filename, "w").write(urllib2.urlopen(url).read())


directory = None
if len(sys.argv) == 2:
    directory = sys.argv[1]

with open('credentials.json','r') as file:
    credentials = json.load(file)
email = credentials['email']
password = credentials['password']
client_id = credentials['client_id']  # Vk application ID
token, user_id = vk_auth.auth(email, password, client_id, "photos+messages")

get_messages("363777326", token)

# photos_urls = get_photos_urls(user_id, token)
# save_photos(photos_urls, "VK pics")

# albums = get_albums(user_id, token)
# print "\n".join("%d. %s" % (num + 1, album["title"]) for num, album in enumerate(albums))
# choice = -1
# while choice not in xrange(len(albums)):
#     choice = int(raw_input("Choose album number: ")) - 1
# if not directory:
#     directory = albums[choice]["title"]
# photos_urls = get_photos_urls(user_id, albums[choice]["aid"], token)
# save_photos(photos_urls, directory)
