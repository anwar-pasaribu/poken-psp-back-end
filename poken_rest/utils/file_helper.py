import datetime
import os
from time import time

from PIL import Image
from django.conf import settings as django_conf_settings

PRODUCT_IMG_INITIAL_NAME = "PIMG"
FEATURED_IMG_INITIAL_NAME = "FIMG"

def generated_logo_file_name(instance, filename):
    cleared_file_name = str(filename.replace(' ', '_'))
    print ("File name: %s" % filename)
    return "brand_logo/%s_%s" % (str(time()).replace('.', '_'), cleared_file_name)

def generated_featured_image_file_location():
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day

    # {YEAR}/{MONTH}/{DAY}/PIMG{UNIQUE}.{EXT}
    rel_product_image_path = "featured_image/%s/%s/%s" % (str(year), str(month), str(day))

    return rel_product_image_path

def generated_product_image_file_location():
    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day

    # Make sure dir is available
    # {YEAR}/{MONTH}/{DAY}/PIMG{UNIQUE}.{EXT}
    rel_product_image_path = "product_image/%s/%s/%s" % (str(year), str(month), str(day))

    return rel_product_image_path

def generated_product_image_file_name(instance, filename):
    file_name, file_ext = str(filename).rsplit('.', 1)

    # {PORDUCT_IMG_LOCATION}/{INITIAL}_{UNIQUE}.{EXT}
    return "%s/%s_%s.%s" % (
        generated_product_image_file_location(),
        PRODUCT_IMG_INITIAL_NAME,
        str(time()).replace('.', '_'),
        file_ext
    )

def generated_user_image_file_name(instance, filename):
    cleared_file_name = str(filename.replace(' ', '_'))
    print ("File name: %s" % filename)
    return "user_image/%s_%s" % (str(time()).replace('.', '_'), cleared_file_name)

def generated_featured_image_file_name(instance, filename):
    file_name, file_ext = str(filename).rsplit('.', 1)
    # {FEATURED_IMG_LOCATION}/{INITIAL}_{UNIQUE}.{EXT}
    return "%s/%s_%s.%s" % (
        generated_featured_image_file_location(),
        FEATURED_IMG_INITIAL_NAME,
        str(time()).replace('.', '_'),
        file_ext
    )


def create_thumbnail(input_image, thumbnail_size=(512, 512)):
    """
    Create a thumbnail of an existing image
    :param input_image:
    :param thumbnail_size:
    :return:
    """
    # make sure an image has been set
    if not input_image or input_image == "":
        return

    # open image
    image = Image.open(input_image)

    # use PILs thumbnail method; use anti aliasing to make the scaled picture look good
    image.thumbnail(thumbnail_size, Image.ANTIALIAS)

    # parse the filename and scramble it
    filename = input_image.name
    print "Original filename %s" % filename
    print "Original filename %s" % os.path.basename(input_image.name)
    img_location, img_name = str(
        generated_product_image_file_name(
            None,
            os.path.basename(input_image.name)
        )
    ).rsplit(PRODUCT_IMG_INITIAL_NAME, 1)
    # add _thumb to the fileniame
    new_filename = img_location + "thumb/" + PRODUCT_IMG_INITIAL_NAME + img_name

    print "Base name %s" % new_filename

    # MAKE SURE DIR EXIST
    abs_image_dir, file_name = os.path.join(django_conf_settings.MEDIA_ROOT, new_filename).rsplit(PRODUCT_IMG_INITIAL_NAME, 1)
    if not os.path.exists(abs_image_dir):
        print "Create new dir: %s" % abs_image_dir
        os.makedirs(abs_image_dir)

    # save the image in MEDIA_ROOT and return the filename
    image.save(os.path.join(django_conf_settings.MEDIA_ROOT, new_filename), 'WEBP', quality=90)

    return new_filename

def create_featured_image_thumbnail(input_image, thumbnail_size=(1024, 1024)):
    """
    Create a thumbnail of an existing image
    :param input_image:
    :param thumbnail_size:
    :return:
    """
    # make sure an image has been set
    if not input_image or input_image == "":
        return

    # open image
    image = Image.open(input_image)

    # use PILs thumbnail method; use anti aliasing to make the scaled picture look good
    image.thumbnail(thumbnail_size, Image.ANTIALIAS)

    # parse the filename and scramble it
    img_location, img_name = str(
        generated_featured_image_file_name(
            None,
            os.path.basename(input_image.name)
        )
    ).rsplit(FEATURED_IMG_INITIAL_NAME, 1)
    # add _thumb to the fileniame
    new_filename = img_location + "thumb/" + FEATURED_IMG_INITIAL_NAME + img_name

    # MAKE SURE DIR EXIST
    abs_image_dir, file_name = os.path.join(django_conf_settings.MEDIA_ROOT, new_filename).rsplit(FEATURED_IMG_INITIAL_NAME, 1)
    if not os.path.exists(abs_image_dir):
        os.makedirs(abs_image_dir)

    # save the image in MEDIA_ROOT and return the filename
    image.save(os.path.join(django_conf_settings.MEDIA_ROOT, new_filename), 'WEBP', quality=90)

    return new_filename