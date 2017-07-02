from time import time


def generated_logo_file_name(instance, filename):
    cleared_file_name = str(filename.replace(' ', '_'))
    print ("File name: %s" % filename)
    return "brand_logo/%s_%s" % (str(time()).replace('.', '_'), cleared_file_name)


def generated_product_image_file_name(instance, filename):
    cleared_file_name = str(filename.replace(' ', '_'))
    print ("File name: %s" % filename)
    return "product_image/%s_%s" % (str(time()).replace('.', '_'), cleared_file_name)


def generated_user_image_file_name(instance, filename):
    cleared_file_name = str(filename.replace(' ', '_'))
    print ("File name: %s" % filename)
    return "user_image/%s_%s" % (str(time()).replace('.', '_'), cleared_file_name)


def generated_featured_image_file_name(instance, filename):
    cleared_file_name = str(filename.replace(' ', '_'))
    print ("File name: %s" % filename)
    return "featured_image/%s_%s" % (str(time()).replace('.', '_'), cleared_file_name)