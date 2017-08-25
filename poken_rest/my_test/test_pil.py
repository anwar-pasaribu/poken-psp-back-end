from unicodedata import name, category

from PIL import Image
import os

from PIL._imaging import path
from django.conf import settings as django_conf_settings
import datetime
from time import time

from pilprint import description

PRODUCT_IMG_INITIAL_NAME = "PIMG"

from poken_rest.models import Product, Seller, ProductBrand, ProductCategory, ProductImage, ProductSize


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
    print ("File name: %s" % filename)

    # {PORDUCT_IMG_LOCATION}/{INITIAL}_{UNIQUE}.{EXT}
    return "%s/%s_%s.%s" % (
        generated_product_image_file_location(),
        PRODUCT_IMG_INITIAL_NAME,
        str(time()).replace('.', '_'),
        file_ext
    )


def create_thumbnail(input_image, thumbnail_size=(256, 256)):
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
    abs_image_dir, file_name = os.path.join(django_conf_settings.MEDIA_ROOT, new_filename).rsplit(
        PRODUCT_IMG_INITIAL_NAME, 1)
    if not os.path.exists(abs_image_dir):
        print "Create new dir: %s" % abs_image_dir
        os.makedirs(abs_image_dir)

    # save the image in MEDIA_ROOT and return the filename
    image.save(os.path.join(django_conf_settings.MEDIA_ROOT, new_filename), 'WEBP', quality=90)

    return new_filename


def run():
    main_dir = 'c:\Users\PID-T420S\Downloads\Compressed\shopify-product-csvs-and-images-master\shopify-product-csvs-and-images-master\images\mix'
    main_dir = str(main_dir).replace('\\', u'%s' % os.sep)
    imgs = os.listdir(main_dir)

    seller1 = Seller.objects.first()
    p_brand = ProductBrand.objects.first()
    p_category = ProductCategory.objects.first()
    p_size = ProductSize.objects.first()

    os_sep = os.sep
    for f in imgs:
        abs_path = '%s%s%s' % (main_dir, os_sep, f)
        print("Abs path: " + abs_path)

        img = Image.open(abs_path)

        p_image = ProductImage.objects.create()
        p_image.path = img
        # p_image.thumbnail = create_thumbnail(img, thumbnail_size=(150, 150))
        p_image.title = "title"
        p_image.description = "desc"
        p_image.save()

        p_name = str(img.filename).replace('-', ' ')
        p_desc = p_name
        p_is_posted = True  #TODO Random
        p_is_discount = True  #TODO Random
        p_discount_amount = 10 #TODO Randomize
        p_is_cod = True
        p_is_new = True
        p_stock = 9
        p_price = 100000
        p_weight = 300
        new_p = Product.objects.create(
            name=p_name,
            description=p_desc,
            seller=seller1,
            is_posted=p_is_posted,
            is_discount=p_is_discount,
            discount_amount=p_discount_amount,
            is_cod=p_is_cod,
            is_new=p_is_new,
            brand=p_brand,
            category=p_category,
            size=p_size,
            stock=p_stock,
            price=p_price,
            weight=p_weight
        )
        new_p.images = p_image
        new_p.save()


    # img1 = Image.open('asa.jpg')
    # img1.save('asa.png')

    products = Product.objects.all()

    for p in products:
        print p.name


if __name__ == '__main__':
    run()
