import random
import colorsys

from PIL import Image, ImageDraw

# ASCII art?

def rand_hue_shift(col, max_hue_shift=0.3):
    col = colorsys.rgb_to_hsv(*col)

    col = (col[0] + random.uniform(-0.5, 0.5) * max_hue_shift, 
           col[1],
           col[2])

    col = colorsys.hsv_to_rgb(*col)

    return tuple(map(int, col))


def random_rectangles(img_draw, img_height, img_width, rec_max_width, base_color, grid_based=False, MARGIN=3):
    
    if grid_based:

        grid = [int(img_width/rec_max_width), int(img_height/rec_max_width)] # div by 80
        for x in range(grid[0]):
            for y in range(grid[1]):
        
                mid_x = (x + 0.5) * rec_max_width
                mid_y = (y + 0.5) * rec_max_width

                rec_width = rec_max_width * random.uniform(0, 1)
                rec_height = rec_max_width * 0.95

                col = rand_hue_shift(base_color)
                rectangle_shape = [(mid_x - 0.5 * rec_width, mid_y - 0.5 * rec_height), 
                                (mid_x + 0.5 * rec_width, mid_y + 0.5 * rec_height)]
                img_draw.rounded_rectangle(rectangle_shape, fill=(col))            

    else:
        next_x, next_y = 0, 0
        x, y = MARGIN, MARGIN

        while(y <= img_height):
            dy = rec_max_width * random.uniform(0, 1)
            next_y = min(y + dy, img_height - MARGIN)

            while(x <= img_width):
                dx = rec_max_width * random.uniform(0, 1)
                next_x = min(x + dx, img_width - MARGIN)

                col = rand_hue_shift(base_color)
                rectangle_shape = [(x, y), (next_x, next_y)]
                img_draw.rounded_rectangle(rectangle_shape, fill=(col))

                x += dx + MARGIN
            
            y += dy + MARGIN
            x = MARGIN

    return img_draw


def middle_stamp(img_draw, sides_byte, img_height, img_width, base_color, stamp_size=200, stamp_outline_width=20):

    # Draws a polygon in center of image with number of sides defined by n_sides (byte[0])
    # Exceptions: n_sides < 3 -> draw pie slice

    n_sides = int(sides_byte / 16)

    if n_sides <=2:
        # 11.25 = 360/32 for a smooth transition to circle
        d_angle = int(sides_byte) * 11.25
        start, stop = - 90 - d_angle/2, - 90 + d_angle/2

        img_draw.pieslice([(img_width/2 - stamp_size - stamp_outline_width, img_height/2 - stamp_size - stamp_outline_width), 
                           (img_width/2 + stamp_size + stamp_outline_width, img_height/2 + stamp_size + stamp_outline_width)],
                           0, 360, fill=(0,0,0), width=stamp_outline_width)
        img_draw.pieslice([(img_width/2 - stamp_size, img_height/2 - stamp_size), 
                           (img_width/2 + stamp_size, img_height/2 + stamp_size)],
                           start, stop, fill=base_color, width=stamp_outline_width)
        

    else:
        if n_sides == 3:
            stamp_outline_width += 0.3 * stamp_outline_width
        outer_bound = (img_width/2, img_height/2, stamp_size+stamp_outline_width)
        inner_bound = (img_width/2, img_height/2, stamp_size)
        img_draw.regular_polygon(outer_bound, n_sides, rotation=0, fill=(0,0,0))
        img_draw.regular_polygon(inner_bound, n_sides, rotation=0, fill=base_color)

    return img_draw

def draw_artwork(card):
    # Card = row entry of df_cards:
    # Price, Power, Toughness, # Keyword Abilities, # Special Abilities, # Triggers, Hash

    pri, pow, thg, kw, sp, tr, hash = card

    byte_array = bytearray.fromhex(hash)

    '''
        Extracting info from hash:
        Byte 1: n_sides of middle polygon
        Bytes 26-28: Hue of type shape
        Bytes 29-32: Mean hue value of rectangles 
    '''
    n_sides_polygon = byte_array[0]
    rec_max_width = int(byte_array[1])
    base_color = tuple(int(x) for x in byte_array[29:])

    img_width = 1280
    img_height = 720
    img = Image.new('RGB', (img_width, img_height))
    img_draw = ImageDraw.Draw(img)

    img_draw = random_rectangles(img_draw, img_height, img_width, rec_max_width, base_color)
    img_draw = middle_stamp(img_draw, n_sides_polygon, img_height, img_width, base_color)

    img.save(f'{hash}.png')

    return

if __name__ == '__main__':

    card1 = [6, 1, 1, 2, 3, 1, '010140bd78605b2c97143d178d1ffdc2f502fb188fa701d65a446781ae5014f1']
    card2 = [5, 1, 2, 4, 1, 1, '0d5f4e10daabfb8bf3008fb52a534c5322b26a04139f0840c93b4dfd48f0dc07']
    card3 = [2, 0, 3, 2, 0, 0, '137ef27c8fc7c2e62ae25c4c10f669f98e5125670a2554ea7d83d673460000ff']
    card4 = [5, 0, 3, 2, 3, 1, '1ea3071aa2409b67b1fe96e51570a3f2754b9d19bbdf62a5b9230b63a32be9d4']

    cards = [card1, card2, card3, card4]

    for card in cards:
        draw_artwork(card)
