from PIL import Image
from PIL import ImageDraw
import sys
import random

def analyseImage(path):
    im = Image.open(path)
    results = {
        'size': im.size,
        'mode': 'full',
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return results

#editables
image_path = sys.argv[1]
new_path = sys.argv[2]


mode = analyseImage(image_path)['mode']

im = Image.open(image_path)

i = 0
p = im.getpalette()
last_frame = im.convert('RGBA')

all_frames = []

order = []
for j in range(im.n_frames): order.append(j)
random.shuffle(order)

while i < im.n_frames-1:
    if not im.getpalette(): im.putpalette(p)
    
    new_gif = Image.new('RGBA', im.size)

    if mode == 'partial': new_gif.paste(last_frame)

    new_gif.paste(im, (0, 0), im.convert('RGBA'))
    new_gif = new_gif.resize((im.width,im.height), Image.ANTIALIAS)

    new_frame = Image.new('RGBA', (im.width,im.height), "white")
    new_frame.paste(new_gif,(0, 0))

    all_frames.append(new_frame)

    i += 1
    last_frame = new_frame
    im.seek(order[i])

print(len(all_frames))

try: all_frames[0].save(new_path, optimize=False, save_all=True, append_images=all_frames[1:], loop=1000, duration=20)
except: all_frames[0].save(new_path, optimize=False, save_all=True, append_images=all_frames[1:], loop=1000)

print("gumion!")