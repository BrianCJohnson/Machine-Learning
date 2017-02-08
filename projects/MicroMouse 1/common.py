import math

class State(object):
    def __init__(self, cell, pos, dir, spd):
        self.cell = cell
        self.pos = pos
        self.dir = dir
        self.spd = spd
        #   position (not used)               pos                     dir
        # -+-------------------+-  -+-------------------+-  -+-------------------+-
        #  |      8     7      |    |                   |    |         0         |
        #  |    /    0    \    |    |    +4        +1   |    |     7   |   1     |
        #  |  10     |      5  |    |                   |    |       \ | /       |
        #  |     3---+---1     |    |         +0        |    |  6 -----+----- 2  |
        #  |  11     |      4  |    |                   |    |       / | \       |
        #  |    \    2    /    |    |    +3        +2   |    |     5   |   3     |
        #  |      9     6      |    |                   |    |         4         |
        # -+-------------------+-  -+-------------------+-  -+-------------------+-
        
    def __hash__(self):
        return hash((self.cell, self.pos, self.dir, self.spd))

    def __eq__(self, other): 
        return self.__dict__ == other.__dict__

    #def __ne__(self, other): 
    #    return self.__dict__ != other.__dict__

   
    def offset_yx(self):
        """returns (dy, dx) of State.loc
        """
        #   position (not used)               pos                     dir
        # -+-------------------+-  -+-------------------+-  -+-------------------+-
        #  |      8     7      |    |                   |    |         0         |
        #  |    /    0    \    |    |    +4        +1   |    |     7   |   1     |
        #  |  10     |      5  |    |                   |    |       \ | /       |
        #  |     3---+---1     |    |         +0        |    |  6 -----+----- 2  |
        #  |  11     |      4  |    |                   |    |       / | \       |
        #  |    \    2    /    |    |    +3        +2   |    |     5   |   3     |
        #  |      9     6      |    |                   |    |         4         |
        # -+-------------------+-  -+-------------------+-  -+-------------------+-
        offset_yx = [( 0.00, 0.00), (-0.25, 0.25), ( 0.25, 0.25), ( 0.25,-0.25), (-0.25,-0.25)]
        return offset_yx[self.pos]


    def myx(self, maze_info):
        """returns (my, my) of state
        """
        my, mx = cell_to_maze(maze_info, self.cell)
        return (my, mx)


    def yx_w_offset(self, maze_info):
        """returns (my, my) of state with offset in cell
        """
        my, mx = self.myx(maze_info)
        dy, dx = self.offset_yx()
        return (my+dy, mx+dx)


    def unit_vector(self):
        """returns the unit vector of State
        """
        r45 = math.radians(45)
        angle = r45 * (2 - self.dir) # dir == 0 points straight up, dir == 2 points to the right
        uy = math.sin(angle)
        ux = math.cos(angle)
        return (uy, ux)


class Vector(object):
    def __init__(self, y, x, s):
        self.y = y
        self.x = x
        self.s = s


def get_sensor_vectors(maze, state):
    """ return far and near sensor vectors from state
    5 sensors, 5 tuples
    """
    y_size, x_size = maze.walls.shape
    maxy = y_size - 1 # calculate the max y index of walls
    maxx = x_size - 1 # calculate the max x index of walls
    y0, x0 = cell_to_maze(maze.info, state.cell)

    dir = state.dir
    if state.pos == 0:
        # we're at the center

        # +---------+----1----+---------+
        # |         |    |    |         |
        # |         9    |    9         |  diagram of the 5
        # |         |\   |   /|         |  sensor vectors
        # +---------+26-73-26-+---------+  and signal strengths
        # |         |   \|/   |         |  if there is a wall
        # 1 ------ 24 -- o -- 25 ------ 1  for loc == 0
        # |         |         |         |
        # +---------+---------+---------+

        #      ((0:L3:1,     1:L1:9,     2:F3:1,     3:R2:9,     4:Rx:1))
        far = [( 0,-3, 1), (-2,-1, 9), (-3, 0, 1), (-2, 1, 9), ( 0, 3, 1)]
        for i, entry in enumerate(far):
            (y, x, s) = entry
            if   dir==0: (dy, dx, s) = ( y, x, s) # y's =  y's, x's =  x's
            elif dir==2: (dy, dx, s) = ( x,-y, s) # y's =  x's, x's = -y's
            elif dir==4: (dy, dx, s) = (-y,-x, s) # y's = -y's, x's = -x's
            elif dir==6: (dy, dx, s) = (-x, y, s) # y's = -x's, x's =  y's
            else: print 'ERROR'
            y = y0 + dy # reassigning y but we're done with it for now
            y = 0 if y < 0 else maxy if y > maxy else y # keeps the sensor from looking past the outer walls ;-)
            x = x0 + dx # reassigning x but we're done with it for now
            x = 0 if x < 0 else maxx if x > maxx else x # keeps the sensor from looking past the outer walls ;-)
            far[i] = Vector(y, x, s) # update the sensor vector entry based on dir

        #       ((0:L0:24,    1:F1:26,    2:F1:73,    3:F1:26,    4:R0:24))
        near = [( 0,-1,24), (-1, 0,26), (-1, 0,73), (-1, 0,26), ( 0, 1,24)]
        for i, entry in enumerate(near):
            (y, x, s) = entry
            if   dir==0: (dy, dx, s) = ( y, x, s) # y's =  y's, x's =  x's
            elif dir==2: (dy, dx, s) = ( x,-y, s) # y's =  x's, x's =  y's
            elif dir==4: (dy, dx, s) = (-y,-x, s) # y's = -y's, x's = -x's
            elif dir==6: (dy, dx, s) = (-x, y, s) # y's = -x's, x's = -y's
            else: print 'ERROR'
            y = y0 + dy # reassigning y but we're done with it for now
            x = x0 + dx # reassigning x but we're done with it for now
            near[i] = Vector(y, x, s)
            # don't need to worry about the sensor looking past the outer walls here ;-)

    else:
        # we're at one of the 4 corner locations, the far sensors don't read anything but we want to show the IR beam
        # assume we're at possition == 4 => loc = 2 (bottom right), dir = 1 (up & to left)
        # the dir is looking counter clockwise

        # none of the far entries return a signal but use them to show ir beam when there isn't a near wall
        far =  [(-2,-1, 0), (-3, 0, 0), (-2, 3, 0), ( 0, 3, 0), ( 2, 3, 0)]
        near = [(-1, 0, 5), (-1, 0,14), (-1, 2, 2), ( 0, 3, 2), ( 1, 2, 6)]
        if ((state.pos << 1) + 1) % 8 == state.dir:
            # we're in a position where the dir is looking clockwise
            temp_far = far[::-1] # reverse the far list order,  [ <first element to include> : <first element to exclude> : <step> ]
            temp_near = near[::-1] # reverse the near list order,  [ <first element to include> : <first element to exclude> : <step> ]
            # reorder, swap x, y, negate x, y
            far = []
            near = []
            for next in temp_far:
                far.append((-next[1], -next[0], next[2]))
            for next in temp_near:
                near.append((-next[1], -next[0], next[2]))

        for i, entry in enumerate(far):
            (y, x, s) = entry
            if   dir==1: (dy, dx, s) = ( y, x, s) # y's =  y's, x's =  x's
            elif dir==3: (dy, dx, s) = ( x,-y, s) # y's =  x's, x's =  y's
            elif dir==5: (dy, dx, s) = (-y,-x, s) # y's = -y's, x's = -x's
            elif dir==7: (dy, dx, s) = (-x, y, s) # y's = -x's, x's = -y's
            else: print 'ERROR'
            y = y0 + dy # reassigning y but we're done with it for now
            y = 0 if y < 0 else maxy if y > maxy else y # keeps the sensor from looking past the outer walls ;-)
            x = x0 + dx # reassigning x but we're done with it for now
            x = 0 if x < 0 else maxx if x > maxx else x # keeps the sensor from looking past the outer walls ;-)
            far[i] = Vector(y, x, s) # make far entries vector type

        for i, entry in enumerate(near):
            (y, x, s) = entry
            if   dir==1: (dy, dx, s) = ( y, x, s) # y's =  y's, x's =  x's
            elif dir==3: (dy, dx, s) = ( x,-y, s) # y's =  x's, x's =  y's
            elif dir==5: (dy, dx, s) = (-y,-x, s) # y's = -y's, x's = -x's
            elif dir==7: (dy, dx, s) = (-x, y, s) # y's = -x's, x's = -y's
            else: print 'ERROR'
            y = y0 + dy # reassigning y but we're done with it for now
            y = 0 if y < 0 else maxy if y > maxy else y # keeps the sensor from looking past the outer walls ;-)
            x = x0 + dx # reassigning x but we're done with it for now
            x = 0 if x < 0 else maxx if x > maxx else x # keeps the sensor from looking past the outer walls ;-)
            near[i] = Vector(y, x, s)
            # don't need to worry about the sensor looking past the outer walls here ;-)

    sensor_vectors = (far, near)
  
    return sensor_vectors



def cell_to_maze(maze_info, cell):
    """ Convert cell coords to maze array coords
        cy, cx : 0-15 => my, mx : 1-31 (maze array : 0-32)
    """
    cy, cx = cell
    rows, cols = maze_info
    mx = cx * 2 + 1
    my = (rows - cy) * 2 - 1
    return (my, mx)


def maze_to_cell(maze_info, my, mx):
    """ Convert maze array coords to cell coords
        my, mx : 1-31 (maze array : 0-32) => cy, cx : 0-15 
    """
    rows, cols = maze_info
    cx = (mx - 1) / 2
    cy = rows - (my + 1) / 2
    return (cy, cx)


def cell_delta_to_dir(start_cell, end_cell):
    """returns the direction (0,2,4,6) between two cells
    """
    sy, sx = start_cell
    ey, ex = end_cell
    if sy == ey:
        if ex > sx:
            dir = 2
        else:
            dir = 6
    elif sx == ex:
        if ey > sy:
            dir = 0
        else:
            dir = 4
    else:
        raise ValueError('start cell and end cell not in same row or column, start_cell: {}, end_cell: {}'.format(start_cell, end_cell))
    return dir
