#!/usr/bin/python

from pprint import pprint as px
from glob import glob
import gdata.youtube
import gdata.youtube.service
import os.path
from sys import argv

if len(argv) != 2:
    print "Wrong number of arguments."
    exit(1)

yt_service = gdata.youtube.service.YouTubeService()
#yt_service.debug = True
yt_service.email = 'brown.ballroom@gmail.com'
yt_service.password = 'secret'
#yt_service.account_type = 'GOOGLE'
yt_service.source = 'my-example-application'
yt_service.auth_service_url = 'https://www.google.com/youtube/accounts/ClientLogin'
yt_service.developer_key = 'AI39si573dorSANLKW4umMAT7awL4jVnlZSfI_J-U5kFvUnNLNFFruGmIRxutNY4UTjP4y_Qx0mZYTkH1b_bocV4g1rJUr3Z4g'
yt_service.client_id = 'ytapi-DanHackney-PythonYoutubebat-qa3chdm6-0'
yt_service.ProgrammaticLogin()

print "logged in"

# Load the contents of dirname(<basepath>)/<name>
def local_meta_info(basepath, name):
    meta_path = os.path.join(os.path.dirname(basepath), name)
    with open(meta_path) as f:
        meta_text = f.read()
    return meta_text

def media_group(filename):
    desc_text = local_meta_info(filename, 'description')
    tags = local_meta_info(filename, 'tags')
    category = local_meta_info(filename, 'category')
    # Get the basename without the file extension.
    title = os.path.splitext(os.path.basename(filename))[0]

    my_media_group = gdata.media.Group(
        title=gdata.media.Title(text=title),
        description=gdata.media.Description(description_type='plain',
                                            text=desc_text),
        keywords=gdata.media.Keywords(text=tags),
        category=gdata.media.Category(
            text=category,
            scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
            label=category),
        player=None
        )
    return my_media_group

def upload_one_video(filename):
    video_entry = gdata.youtube.YouTubeVideoEntry(media=media_group(filename))
    new_entry = yt_service.InsertVideoEntry(video_entry, filename)
    return new_entry

file_list = argv[-1]

with open(file_list) as f:
    videos = map(str.strip, f.readlines())

while videos:
    f = videos.pop()
    print "Uploading ", os.path.basename(f), "..."
    entry = upload_one_video(f)
    print "Uploaded with url: ", entry.GetMediaURL()
    with open(file_list, 'w+b') as l:
        l.write("\n".join(videos))
