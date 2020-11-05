from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import sys

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

def get_avg_fps(PIL_Image_object):
    """ Returns the average framerate of a PIL Image object """
    PIL_Image_object.seek(0)
    frames = duration = 0
    while True:
        try:
            frames += 1
            duration += PIL_Image_object.info['duration']
            PIL_Image_object.seek(PIL_Image_object.tell() + 1)
        except EOFError:
            return frames / duration * 100
    return None

#setup
width = 500
margin = 25
threshold = 470
fontsize = 44
padding = fontsize*1.15
font = ImageFont.truetype("font.otf",fontsize)

#editables
image_path = sys.argv[1]
content_raw = sys.argv[2].replace("\n","")
new_path = sys.argv[3]

#wrap text
content_split = content_raw.split(" ")
text = ""
for word in content_split:
    if font.getsize_multiline(text+word+" ")[0] <= threshold: text += " " + word
    else: text+="\n"+word
text = text[1:]


text_size = font.getsize_multiline(text)
mode = analyseImage(image_path)['mode']

im = Image.open(image_path)
im.seek(0)

i = 0
p = im.getpalette()
last_frame = im.convert('RGBA')

all_frames = []

try:
    while True:
        print("saving %s (%s) frame %d, %s %s" % (new_path, mode, i, im.size, im.tile))
        if not im.getpalette(): im.putpalette(p)

        
        new_gif = Image.new('RGBA', im.size)

        if mode == 'partial': new_gif.paste(last_frame)

        '''
        im = im.resize((width,int(width*im.size[1]/im.size[0])), Image.ANTIALIAS)
        new_frame.paste(im,(0, new_frame.size[1]-im.size[1],new_frame.size[0],new_frame.size[1]), im.convert("RGBA"))
        '''

        new_gif.paste(im, (0, 0), im.convert('RGBA'))
        new_gif = new_gif.resize((width,int(width*new_gif.size[1]/new_gif.size[0])), Image.ANTIALIAS)

        print(text_size[1])
        print(new_gif.size[1])
        print(text_size[1]+margin*2-5+new_gif.size[1])
        new_frame = Image.new('RGBA', (width,text_size[1]+margin*2-5+new_gif.size[1]), "white")
        new_frame.paste(new_gif,(0, new_frame.size[1]-new_gif.size[1],new_frame.size[0],new_frame.size[1]))
        
        draw = ImageDraw.Draw(new_frame)
        h = margin-12
        lines = text.split("\n")
        for line in lines:
            draw.multiline_text(xy=((width - font.getsize_multiline(line)[0]) / 2, h),text=line,font=font,fill="black")
            h+=padding

        all_frames.append(new_frame)

        i += 1
        last_frame = new_frame
        im.seek(im.tell() + 1)
except:
    pass
print("hi")
print(len(all_frames))
all_frames[0].save(new_path, optimize=False, save_all=True, append_images=all_frames[1:], loop=1000, duration=im.info['duration'])
#all_frames[0].save("b"+new_path, optimize=False, save_all=True, append_images=all_frames[1:], loop=1000)
print("wawawwaaw:::::"+new_path)

'''
im = Image.open("squirl.png")
im = im.resize((width,int(width*im.size[1]/im.size[0])), Image.ANTIALIAS)

text_size = font.getsize_multiline(text)
bg = Image.new(im.mode, (width,text_size[1]+margin*2-5+im.size[1]), "white")
bg.paste(im,box=(0,bg.size[1]-im.size[1],bg.size[0],bg.size[1]))

draw = ImageDraw.Draw(bg)
h = margin-12
lines = text.split("\n")
for line in lines:
    draw.multiline_text(xy=((width - font.getsize_multiline(line)[0]) / 2, h),text=line,font=font,fill="black")
    h+=padding

bg.save("bolus.png")
'''