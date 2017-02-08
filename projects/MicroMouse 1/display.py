from Tkinter import *
import tkFont
import math

root = Tk()
root.title("MicroMouse Project")

def close_window (): 
    root.destroy()

frame = Frame(root)
frame.pack()
button = Button (frame, text = "Quit", command = close_window)
button.grid(row  = 0, column = 0, padx = 10, sticky='w')

value_labels = ('Maze', 'Motion', 'Algorithm', 'Search Time', 'Avg Time', 'Max Time', 'Search Nodes', 'Avg Nodes', 'Max Nodes', 'Total Time', '1st Run', '1st Return', '2nd Run', '2nd Return', '3rd Run')
value_text = []
for i, value_label in enumerate(value_labels):
    Label(frame, text = value_label).grid(row = 0, column = i+1, padx = 20)
    if i == 0:
        value_text.append(Text(frame, height = 1, width = 20))
    else:
        value_text.append(Text(frame, height = 1, width = 10))
    value_text[i].grid(row = 1, column = i + 1, padx = 10)
    value_text[i].insert(END, '-')


def update_value(label, value):
    i = value_labels.index(label)
    value_text[i].delete("1.0", END)
    if label in ('Maze', 'Motion', 'Algorithm'):
        value_text[i].insert("1.0", value)
    elif label in ('Search Nodes', 'Avg Nodes', 'Max Nodes'):
        value_text[i].insert("1.0", '{:8.0f}'.format(value))
    else:
        value_text[i].insert("1.0", '{:8.3f}'.format(value))
    root.update()
    return


class Display(object):
    def __init__(self):
        # create canvas
        #cw = 980 # canvas width
        cw = 1820 # canvas width
        ch = 910 # canvas height
        canvas = Canvas(root, width=cw, height=ch, background="grey15")
        canvas.pack()
        self.canvas = canvas
        self.cw = cw
        self.ch = ch
        self.wall_thickness = 4
        self.cell_spacing = 50
        self.h_offset_l = 0 # initially the offset is zero but we'll change it later when we know the maze size
        self.h_offset_r = 0 # initially the offset is zero but we'll change it later when we know the maze size
        self.v_offset = 0 # initially the offset is zero but we'll change it later when we know the maze size
        #self.v_cells = 0 # initially the number of cell rows is zero but we'll change it later when we know the maze size

    def delete_id(self, id):
        self.canvas.delete(id)
        self.canvas.update()
        return

    def draw_ir(self, maze, state, wall_yx):
        wy, wx = wall_yx
        my, mx = state.myx(maze.info)
        oy, ox = state.offset_yx()
        # make starting point of ir at the front of the mouse
        uy, ux = state.unit_vector() # get the unit vector of dir
        half_mouse_length = 0.6 # hack, fraction of cell spacing * 2
        my = my - half_mouse_length * uy
        mx = mx + half_mouse_length * ux
        v_offset = self.v_offset # vertical offset to center - height/2
        if maze.side == 'right':
            h_offset = self.h_offset_r # horizontal offset to center - width/2
        else: 
            h_offset = self.h_offset_l
        y0 = self.cell_spacing * (oy + my / 2) + v_offset # this is just the center of the front of the mouse, not the corner point the IR comes from :-(
        x0 = self.cell_spacing * (ox + mx / 2) + h_offset # this is just the center of the front of the mouse, not the corner point the IR comes from :-(
        y1 = (self.cell_spacing * wy) / 2 + v_offset # this is just the center of the wall, not the actual point on the wall that the IR is shining on :-(
        x1 = (self.cell_spacing * wx) / 2 + h_offset # this is just the center of the wall, not the actual point on the wall that the IR is shining on :-(
        id =  self.canvas.create_line(x0, y0, x1, y1, fill='red', capstyle = ROUND, width = 3)
        self.canvas.update()
        return id


def draw_maze(display, maze):
    '''draw maze'''
    cw = display.cw # canvas width
    ch = display.ch # canvas hieght
    cell_spacing = display.cell_spacing
    wall_thickness = display.wall_thickness
    (v_cells, h_cells) = maze.info
    display.v_cells = v_cells
    if display.h_offset_l == 0:
        display.h_offset_l = 0.25 * cw - (h_cells * cell_spacing) / 2 # horizontal offset to upper left corner of maze on left 
    if display.h_offset_r == 0:
        display.h_offset_r = 0.75 * cw - (h_cells * cell_spacing) / 2 # horizontal offset to upper left corner of maze on right 
    if display.v_offset == 0:
        display.v_offset = 0.5 * ch - (v_cells * cell_spacing) / 2 # vertical offset to upper left corner of maze on either side 

    #print 'display.h_offset: {}, cw: {}, h_cells: {}, cell_spacing: {}'.format(display.h_offset, cw, h_cells, cell_spacing)
    #print 'display.v_offset: {}, ch: {}, v_cells: {}, cell_spacing: {}'.format(display.v_offset, ch, v_cells, cell_spacing)
    draw_maze_3(display, maze)
    display.canvas.update()

    return


def draw_maze_3(display, maze_obj):
    ''' draw maze 3'''
    maze = maze_obj.walls
    if maze_obj.side == 'left':
        h_offset = display.h_offset_l
    else:
        h_offset = display.h_offset_r
    canvas = display.canvas
    # maze is a numpy array
    #(cell_rows, cell_cols) = maze_obj.info
    #rows = 2*cell_rows + 1
    #cols = 2*cell_cols + 1
    rows = maze.shape[0]
    cols = maze.shape[1]
    print 'draw_maze_3(), rows: {}, cols: {}'.format(rows, cols)
    spacing = display.cell_spacing
    thickness = display.wall_thickness
    cell_dim = spacing - thickness # spacing = post to post distance
    large_font_size = int(0.75 * cell_dim)
    small_font_size = int(0.15 * cell_dim)
    y0 = display.v_offset - thickness/2 # need to get the cell spacing corner on offset
    large_maze_font = tkFont.Font(size = -large_font_size) # negative font size uses pixels
    small_maze_font = tkFont.Font(size = -small_font_size) # negative font size uses pixels
    for row in range(rows):
        if row % 2 == 0:
            y1 = y0 + thickness
        else:
            y1 = y0 + cell_dim
        x0 = h_offset - thickness/2 # need to get the cell spacing corner on offset
        for col in range(cols):
            if col % 2 == 0:
                x1 = x0 + thickness
            else:
                x1 = x0 + cell_dim
            cell_value = maze[row,col]
            if cell_value == 1:
                canvas.create_rectangle(x0, y0, x1, y1, fill='red', outline='white')
            elif cell_value == -1:
                canvas.create_rectangle(x0+1, y0+1, x1, y1, fill='grey40', outline = '')
            elif cell_value == 2:
                canvas.create_text((x0+x1)/2, (y0+y1)/2, text = "S", font = large_maze_font, fill = 'white', anchor = CENTER) # negative font size uses pixels
                #canvas.create_text((x0+x1)/2, (y0+y1)/2, text = "S", font = (size = -20), fill = 'white', anchor = CENTER) # negative font size uses pixels
            elif cell_value == 3:
                canvas.create_text((x0+x1)/2, (y0+y1)/2, text = "G", font = large_maze_font, fill = 'white', anchor = CENTER) # negative font size uses pixels
            x0 = x1
        y0 = y1
    return


def draw_wall(display, y, x):
    h_offset = display.h_offset_r
    v_offset = display.v_offset
    thickness = display.wall_thickness
    spacing = display.cell_spacing
    width = spacing - thickness
    if y % 2 == 0:
        h = thickness
    else:
        h = width
    if x % 2 == 0:
        w = thickness
    else:
        w = width
    x0 = (x * spacing)/2 + h_offset - w/2 
    x1 = x0 + w
    y0 = (y * spacing)/2 + v_offset - h/2 
    y1 = y0 + h
    display.canvas.create_rectangle(x0, y0, x1, y1, fill='red', outline='white')
    display.canvas.update()
    return


def draw_mouse(display, ids, mouse):
    if ids == None:
        draw_maze(display, mouse.maze) # draw the mouse's maze if the first time
    else:
        display.canvas.delete(ids[0])
        display.canvas.delete(ids[1])
    angle = 90.0 - mouse.state.dir * 45.0
    # draw the mouse on the left and right sides
    ids = []
    marker_size = 5
    marker_color = 'green'
    for side in ('left', 'right'):
        coords = state_to_display(display, mouse.state, side)
        ids.append(draw_part(display.canvas, mouse.outline, coords, angle, 0.1, 'green', 'none'))
        draw_marker(display, mouse.state, side, marker_size, marker_color)
    display.canvas.update()
    return ids


def state_to_display(display, state, side):
    """ converts state cell location into display coordinates for maze on left or right side
    """
    cy, cx = state.cell
    dy, dx = state.offset_yx() # offset from center of cell
    spacing = display.cell_spacing
    if side == 'left':
        x = +(cx + dx + 0.5) * spacing + display.h_offset_l
    else:
        x = +(cx + dx + 0.5) * spacing + display.h_offset_r
    y = -(cy - dy + 0.5) * spacing + display.ch - display.v_offset # account for maze cell y=0 at bottom, tk canvas y=0 is at the top
    return [x, y]


def draw_marker(display, state, side, size, color):
    """ draws marker at state location in maze on left or right side
    """
    circle = False
    coords = state_to_display(display, state, side)
    if circle:
        delta = size
        x0 = coords[0]-delta
        y0 = coords[1]-delta
        x1 = coords[0]+delta
        y1 = coords[1]+delta
        marker = display.canvas.create_oval(x0, y0, x1, y1, outline = color)
    else:
        # draw marker with orientation in cell
        uy, ux = state.unit_vector()
        delta = size
        x0 = coords[0] + delta * (ux + ux - uy)
        y0 = coords[1] - delta * (uy + uy + ux)
        x1 = coords[0] + delta * (ux + ux + ux)
        y1 = coords[1] - delta * (uy + uy + uy)
        x2 = coords[0] + delta * (ux + ux + uy)
        y2 = coords[1] - delta * (uy + uy - ux)
        marker = display.canvas.create_polygon(x0, y0, x1, y1, x2, y2, outline = color)
        # draw marker at correct position within cell
        #state.offset_yx()
    display.canvas.update()
    return marker


def create_mouse_outline():
    """ Returns an array with 2 elements,
        the first is an array of x,y coordinates used to draw the part
        the second element is the reference point for the part
    """
    # make simple outline ~rounded on each end
    # assumes dia1 >= dia2
    # center at center of axle extends to the right
    # +-----+
    # |     |
    # +-+ +-+
    #   | +----------+
    #   |            |
    #   | +----------+
    # +-----+
    # |     |
    # +-+ +-+
    tire_width = 50.0
    tire_dia_half = 50.0
    axle_length = 50.0
    axle_thickness_half = 10.0
    body_width_half = 20.0
    body_length = 150.0
    inside_tire_half = axle_length + body_width_half
    width_half = tire_width + inside_tire_half

    mouse_outline = [[-axle_thickness_half, 0.0],
        [-axle_thickness_half, -inside_tire_half],
        [-tire_dia_half, -inside_tire_half],
        [-tire_dia_half, -width_half],
        [tire_dia_half, -width_half],
        [tire_dia_half, -inside_tire_half],
        [axle_thickness_half, -inside_tire_half],
        [axle_thickness_half, -body_width_half],
        [body_length, -body_width_half],
        [body_length,  body_width_half],
        [axle_thickness_half,  body_width_half],
        [axle_thickness_half,  inside_tire_half],
        [tire_dia_half,  inside_tire_half],
        [tire_dia_half,  width_half],
        [-tire_dia_half,  width_half],
        [-tire_dia_half,  inside_tire_half],
        [-axle_thickness_half,  inside_tire_half],
        [-axle_thickness_half, 0.0]]
 
    #   +----+  +-----+  +----+
    #  /     |  |     |  |     \
    # +      |  +-+ +-+  |      +
    # |      +----+ +----+      |
    # |                         |
    # |      +----+ +----+      |
    # +      |  +-+ +-+  |      +
    #  \     |  |     |  |     /
    #   +----+  +-----+  +----+
    mouse = [mouse_outline, [0,0]]
    return mouse


def draw_part(chart,part, translation, rotation, scale, color, tags):
    """ Draws a Part whose drawing points have been translated, rotated and scaled around the Part's center point
    by translation, rotation and scale with the specified color and tags
    """
    # part: [point_list, center_point]
    # translation: [dx, dy]
    # rotation: angle in degrees (rotates about the center_point of the part)
    # scale: scale factor (scales about the center_point of the part)
    translated_part = translate_part(part, translation)
    rotated_part = rotate_part(translated_part, rotation)
    scaled_part = scale_part(rotated_part, scale)
    #flip y values for stupid tkinter coord convention
    #chart.create_polygon(scaled_part[0], fill=color, outline=color, tags=tags)
    id = chart.create_polygon(scaled_part[0], outline=color, tags=tags) # no fill
    return id


def transform_part(part, translation, rotation, scale):
    """ Returns a new Part whose drawing points have been translated, rotated and scaled around the Part's center point
    by translation, rotation and scale
    """
    translated_part = translate_part(part, translation)
    rotated_part = rotate_part(translated_part, rotation)
    scaled_part = scale_part(rotated_part, scale)
    return scaled_part


def scale_part(part, scale):
    """ Returns a new Part whose drawing points have been scaled around the Part's center point by scale"""
    # scale: scale factor (scales about the center_point of the part)
    center_point = part[1]
    cx = center_point[0]
    cy = center_point[1]
    part_points = []
    for p in part[0]: part_points.append([scale * (p[0] - cx) + cx,scale * (p[1] - cy) + cy])
    return [part_points,center_point]


def rotate_part(part, rotation):
    """ Returns a new Part whose drawing points have been rotated around the Part's center point by rotation"""
    cx = part[1][0]
    cy = part[1][1]
    angle = math.radians(rotation)
    sin = math.sin(angle)
    cos = math.cos(angle)
    part_points = []
    for p in part[0]:
        #flip y values for stupid tkinter coord convention
        part_points.append([cos * (p[0] - cx) + sin * (p[1] - cy) + cx,-sin * (p[0] - cx) + cos * (p[1] - cy) + cy])
        #part_points.append([cos*(p[0]-cx)-sin*(p[1]-cy)+cx,sin*(p[0]-cx)+cos*(p[1]-cy)+cy])
    return [part_points,part[1]]


def translate_part(part, translation):
    """Returns a new Part whose drawing points and center point have been modified by the translation"""
    part_points = []
    for p in part[0]: part_points.append([p[0] + translation[0],p[1] + translation[1]])
    p = part[1]
    new_center_point = [p[0] + translation[0],p[1] + translation[1]]
    return [part_points,new_center_point]


