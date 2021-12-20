import random
import colorsys

from PIL import Image, ImageDraw

# ASCII art?

WIDTH = 1280
HEIGHT = 720

def rand_hue_shift(col, max_hue_shift=0.3):
    col = colorsys.rgb_to_hsv(*col)

    col = (col[0] + random.uniform(-0.5, 0.5) * max_hue_shift, 
           col[1],
           col[2])

    col = colorsys.hsv_to_rgb(*col)

    return tuple(map(int, col))


def random_rectangles(img_draw, rec_max_width, base_color, grid_based=True, MARGIN=3):
    
    if grid_based:
        grid_size = int(WIDTH/(rec_max_width - WIDTH % rec_max_width))
        grid = [grid_size, grid_size] # div by 80
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

        while(y <= HEIGHT):
            dy = rec_max_width * random.uniform(0, 1)
            next_y = min(y + dy, HEIGHT - MARGIN)

            while(x <= WIDTH):
                dx = rec_max_width * random.uniform(0, 1)
                next_x = min(x + dx, WIDTH - MARGIN)

                col = rand_hue_shift(base_color)
                rectangle_shape = [(x, y), (next_x, next_y)]
                img_draw.rounded_rectangle(rectangle_shape, fill=(col))

                x += dx + MARGIN
            
            y += dy + MARGIN
            x = MARGIN

    return img_draw


def middle_stamp(img_draw, sides_byte, base_color, stamp_size=200, stamp_outline_width=20):

    # Draws a polygon in center of image with number of sides defined by n_sides (byte[0])
    # Exceptions: n_sides < 3 -> draw pie slice

    n_sides = int(sides_byte / 16)

    if n_sides <=2:
        # 11.25 = 360/32 for a smooth transition to circle
        d_angle = int(sides_byte) * 11.25
        start, stop = - 90 - d_angle/2, - 90 + d_angle/2

        img_draw.pieslice([(WIDTH/2 - stamp_size - stamp_outline_width, HEIGHT/2 - stamp_size - stamp_outline_width), 
                           (WIDTH/2 + stamp_size + stamp_outline_width, HEIGHT/2 + stamp_size + stamp_outline_width)],
                           0, 360, fill=(0,0,0), width=stamp_outline_width)
        img_draw.pieslice([(WIDTH/2 - stamp_size, HEIGHT/2 - stamp_size), 
                           (WIDTH/2 + stamp_size, HEIGHT/2 + stamp_size)],
                           start, stop, fill=base_color, width=stamp_outline_width)
        

    else:
        if n_sides == 3:
            stamp_outline_width += 0.3 * stamp_outline_width
        outer_bound = (WIDTH/2, HEIGHT/2, stamp_size+stamp_outline_width)
        inner_bound = (WIDTH/2, HEIGHT/2, stamp_size)
        img_draw.regular_polygon(outer_bound, n_sides, rotation=0, fill=(0,0,0))
        img_draw.regular_polygon(inner_bound, n_sides, rotation=0, fill=base_color)

    return img_draw


def contour_lines(img_draw, nb_lines):

    max_nb_lines = 64
    fill = 'black'
    l_width = 2

    adjust_line_width_threshold = 16

    # Upper right
    if nb_lines < adjust_line_width_threshold:
        l_width = adjust_line_width_threshold - nb_lines


    d_x = WIDTH / (2 * min(max_nb_lines, nb_lines))
    d_y = HEIGHT / (2 * min(max_nb_lines, nb_lines))
    x_s, x_e, y_s, y_e = WIDTH/2, WIDTH, 0, d_y

    for i in range(min(nb_lines, max_nb_lines)):
        img_draw.line([(x_s + i * d_x, y_s), (x_e, y_e + i * d_y)], fill=fill, width=l_width)

    remaining_lines = nb_lines - max_nb_lines

    # Lower right
    if remaining_lines > 0:

        if remaining_lines < adjust_line_width_threshold:
            l_width = adjust_line_width_threshold - remaining_lines
            
        d_x = WIDTH / (2 * min(max_nb_lines, remaining_lines))
        d_y = HEIGHT / (2 * min(max_nb_lines, remaining_lines))
        x_s, x_e, y_s, y_e = WIDTH, WIDTH - d_x, HEIGHT/2, HEIGHT

        for i in range(min(remaining_lines, max_nb_lines)):
            img_draw.line([(x_s, y_s  + i * d_y), (x_e - i * d_x, y_e)], fill=fill, width=l_width)

    remaining_lines = nb_lines - 2 * max_nb_lines

    # Lower left
    if remaining_lines > 0:

        if remaining_lines < adjust_line_width_threshold:
            l_width = adjust_line_width_threshold - remaining_lines

        d_x = WIDTH / (2 * min(max_nb_lines, remaining_lines))
        d_y = HEIGHT / (2 * min(max_nb_lines, remaining_lines))
        x_s, x_e, y_s, y_e = WIDTH/2, 0, HEIGHT, HEIGHT - d_y

        for i in range(min(remaining_lines, max_nb_lines)):
            img_draw.line([(x_s - i * d_x, y_s), (x_e, y_e - i * d_y)], fill=fill, width=l_width)

    remaining_lines = nb_lines - 3 * max_nb_lines

    # Upper left 
    if remaining_lines > 0:

        if remaining_lines < adjust_line_width_threshold:
            l_width = adjust_line_width_threshold - remaining_lines

        d_x = WIDTH / (2 * min(max_nb_lines, remaining_lines))
        d_y = HEIGHT / (2 * min(max_nb_lines, remaining_lines))
        x_s, x_e, y_s, y_e = 0, d_x, HEIGHT/2, 0

        for i in range(min(remaining_lines, max_nb_lines)):
            img_draw.line([(x_s, y_s  - i * d_y), (x_e + i * d_x, y_e)], fill=fill, width=l_width)

    return img_draw


def draw_artwork(card):
    # Card = row entry of df_cards:
    # Price, Power, Toughness, # Keyword Abilities, # Special Abilities, # Triggers, Hash
    pri, pow, thg, kw, sp, tr, hash = card

    '''
        Extracting info from hash:
        Byte 1:         n_sides of stamp polygon
        Byte 2:         rec_max_width
        Byte 3:         nb_lines in upper right corner
        Byte X: (flags) grid, lb, rb, tb, bb, 
        Bytes 26-28:    Hue of type shape
        Bytes 29-32:    Mean hue value of rectangles 
    '''
    byte_array = bytearray.fromhex(hash)

    n_sides_polygon = byte_array[0]
    rec_max_width = int(byte_array[1])
    nb_lines = 256 - int(byte_array[2])
    base_color = tuple(int(x) for x in byte_array[29:])
    type_color = tuple(int(x) for x in byte_array[26:29])
    
    img = Image.new('RGB', (WIDTH, HEIGHT))
    img_draw = ImageDraw.Draw(img)

    img_draw = random_rectangles(img_draw, rec_max_width, base_color, grid_based=False)
    img_draw = middle_stamp(img_draw, n_sides_polygon, base_color)
    img_draw = contour_lines(img_draw, nb_lines)
    # img_draw.ellipse([(100, 100), (400, 300)], fill=type_color)
    # img_draw.ellipse([(100, 100), (300, 300)], fill=None)

    img.save(f'./Artworks/out/{hash}.png')

    return

if __name__ == '__main__':

    card1 = [6, 1, 1, 2, 3, 1, '010130bd78605b2c97143d178d1ffdc2f502fb188fa701d65a446781ae5014f1']
    card2 = [5, 1, 2, 4, 1, 1, '0d5fc010daabfb8bf3008fb52a534c5322b26a04139f0840c93b4dfd48f0dc07']
    card3 = [2, 0, 3, 2, 0, 0, '137ea27c8fc7c2e62ae25c4c10f669f98e5125670a2554ea7d83d673460000ff']
    card4 = [5, 0, 3, 2, 3, 1, '1ea3e01aa2409b67b1fe96e51570a3f2754b9d19bbdf62a5b9230b63a32be9d4']

    cards = [card3, card4, card2, card1]

    for card in cards:
        draw_artwork(card)
