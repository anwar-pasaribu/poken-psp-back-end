from PIL import Image
import os

if __name__ == '__main__':

    for f in os.listdir('.'):
        if f.startswith('asa'):
            print f

    img1 = Image.open('asa.jpg')
    img1.save('asa.png')
