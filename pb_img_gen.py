from PIL import Image, ImageDraw, ImageFont
import os

def gen_pb(filename, rank, username, score):
    #Draw a text on an Image, saves it, show it
    Tinos = ImageFont.truetype('Tinos-Regular.ttf', 52)
    # sorath eye open
    eye = Image.open('sorath_eye.png')
    # sorath eye copy
    eyecopy = eye.copy()
    # create image
    image = Image.new(mode = "RGB", size = [1100, 84])
    draw = ImageDraw.Draw(image)

    user_x_initial = 100 
    min_dist_rank_user = 28
    char_width = 24

    if len(rank) == 1:
        user_x = user_x_initial
    elif len(rank) == 2:
        user_x = user_x_initial
    elif len(rank) == 3:
        user_x = user_x_initial + min_dist_rank_user
    elif len(rank) == 4:
        user_x = user_x_initial + (2 * min_dist_rank_user)

    txt_color = (158, 0, 0)

    # draw rank
    draw.text((16, 40), rank, font=Tinos, fill=txt_color, anchor="lm")
    # draw username
    draw.text((user_x, 40), username, font=Tinos, fill=(179, 179, 179), anchor="lm")
    # draw score
    draw.text((1000, 40), score, font=Tinos, fill=txt_color, anchor="rm")
    # paste sorath eye
    image.paste(eyecopy, (1021, 24, 1080, 60))
    # save file
    image.save(filename)
    # show file
    os.system(filename)