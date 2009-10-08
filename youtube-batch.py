#!/usr/bin/python

from pprint import pprint as px
from glob import glob
import gdata.youtube
import gdata.youtube.service
import os.path
from sys import argv
import xdg.BaseDirectory as bd
import ConfigParser

if len(argv) != 2:
    print "Usage: yt-bulk-py video_list"
    exit(1)

resource_name = 'yt-bulk-py'

if not bd.load_first_config(resource_name):
    sys.stderr.write('Creating config directory: ' + bd.save_config_path(resource_name))

conf_dir = bd.load_first_config(resource_name)
conf_file = os.path.join(conf_dir, 'config')

conf_skel = """# Configuration file for yt-bulk-py

# Account information for the user doing the uploading.
[user]
email = address@example.com
password = secret"""

if not os.path.isfile(conf_file):
    with open(conf_file, 'w+b') as f:
        f.write(conf_skel)

config = ConfigParser.ConfigParser()
config.read(conf_file)

if not 'user' in config.sections():
    sys.stderr.write('Error: No [user] section in config file.')
    exit(1)

if not 'email' in config.options('user') and 'password' in config.options('user'):
    sys.stderr.write('Error: Missing "email" or "password" options in config file.')
    exit(1)

yt_service = gdata.youtube.service.YouTubeService()
yt_service.email = config.get('user', 'email')
yt_service.password = config.get('user', 'password')
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
    print "Uploading", os.path.basename(f), "..."
    entry = upload_one_video(f)
    upload_status = yt_service.CheckUploadStatus(entry)

    if upload_status is not None:
        video_upload_state = upload_status[0]
        detailed_message = upload_status[1]
        print "Uploaded state:", video_upload_state, "Detailed status:", detailed_message, "URL:", entry.media.player.url
    else:
        print "URL:", entry.media.player.url

    with open(file_list, 'w+b') as l:
        l.write("\n".join(videos))
