import os
import secrets
from PIL import Image
from flaskapp import app

OUT_SIZE = {'pfp': (125, 125), 'media': (200, 200)}

# Directory paths
PROFILE_PIC_DIR = os.path.join(app.root_path, 'static/profile_pics/')
MEDIA_DIR = os.path.join(app.root_path, 'static/media/')

# Ensure the directories exist
if not os.path.exists(PROFILE_PIC_DIR):
    os.makedirs(PROFILE_PIC_DIR)
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)


def save_picture(picture, pic_type):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture.filename)
    pic_fname = random_hex + f_ext
    pic_path = os.path.join(PROFILE_PIC_DIR, pic_fname)

    # Resize and save image locally
    i = Image.open(picture)
    i.thumbnail(OUT_SIZE[pic_type])
    i.save(pic_path)

    # Return filename
    return pic_fname


def save_media(picture, pic_type):
    random_hex = secrets.token_hex(10)
    _, f_ext = os.path.splitext(picture.filename)
    pic_fname = random_hex + f_ext
    pic_path = os.path.join(MEDIA_DIR, pic_fname)

    # Open image and resize to specific dimensions for media
    i = Image.open(picture)
    bwidth = 600
    ratio = bwidth / float(i.size[0])
    height = int((float(i.size[1]) * ratio))
    i = i.resize((bwidth, height), Image.LANCZOS)
    i.save(pic_path)

    # Create and save thumbnails, mid, and large images
    # Thumb image
    thumb_path = os.path.join(MEDIA_DIR, 'thumb' + pic_fname)
    j = i.copy()  # Create a copy for the thumbnail
    bwidth = 125
    ratio = bwidth / float(j.size[0])
    height = int((float(j.size[1]) * ratio))
    j = j.resize((bwidth, height), Image.LANCZOS)
    j.save(thumb_path)

    # Mid-size image
    mid_path = os.path.join(MEDIA_DIR, 'mid' + pic_fname)
    k = i.copy()  # Create a copy for the mid-size image
    bwidth = 500
    ratio = bwidth / float(k.size[0])
    height = int((float(k.size[1]) * ratio))
    k = k.resize((bwidth, height), Image.LANCZOS)
    k.save(mid_path)

    # Return filename
    return pic_fname


def get_file_url(f_path):
    # construct a URL relative to static directory
    return f'/static/{f_path}'


def delete_file(f_path):
    # Delete files from local storage
    for item in ['media/', 'media/mid', 'media/thumb']:
        file_path = os.path.join(app.root_path, 'static', item + f_path)
        if os.path.exists(file_path):
            os.remove(file_path)
