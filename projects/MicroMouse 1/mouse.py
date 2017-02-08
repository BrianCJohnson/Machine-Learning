from common import *
from display import create_mouse_outline, draw_wall
from maze import Maze
import time
from graph import *
import random
from copy import copy, deepcopy

class Mouse(object):
    def __init__(self, maze_info, display, move_strategy, algorithm):
        '''
        Sets up attributes of mouse, maze_info and algorithm to be used
        '''
        self.algorithm = algorithm

        # define starting state for mouse
        start_cell = (0, 0) # just location (cy, cx)
        start_pos = 0
        start_dir = 0
        start_spd = 0  
        start_state = State(start_cell, start_pos, start_dir, start_spd)   # cell, pos, dir, spd
    
        print 'creating mouse, move strategy: {}, algorithm: {}'.format(move_strategy, self.algorithm)
        self.state = start_state
        self.maze_info = maze_info
        self.display = display
        self.outline = create_mouse_outline()
        self.maze = Maze("mouse", maze_info)
        self.graph = Graph(self.maze, move_strategy)
        self.phase = 'exploring' # 'exploring','returning','racing'
        self.path = None


    def show_info(self):
        print 'showing mouse info, state:', self.state
        state = self.state
        pos = state.pos
        print 'mouse1, cx:', pos.cx, ', cy:', pos.cy, ', pos:', pos.pos, ', loc:', pos.loc, ', dir:', pos.dir, ', vel:', state.v
        print 'mouse2, cx:{}, cy:{}, pos:{}, loc:{}, dir:{}, vel:{}'.format(pos.cx, pos.cy, pos.pos, pos.loc, pos.dir, state.v)
        pos.show()


    def move(self, sensor_data):
        '''updates mouse.maze with the sensor_data and returns move'''
        changed = self.update_map(sensor_data) # this is detecting any change in the map, ideally we'd just note if any edges on the current path changed
        # assume changed is a list of (cell, parent_cell) tuples
        # look through self.path to see if any of the moves are affected
        node = self.state
        path = self.path
        if self.phase == 'exploring' or self.phase == 'racing':
            goals = self.maze.goals
        elif self.phase == 'returning':
            goals = [(0, 0)]
        else:
            raise ValueError('unknown phase in mouse.move()')

        if self.phase == 'racing':
            self.graph.speed_limited(False) # don't limit the speed, hopefully we know the maze by now and won't get caught in a speed based unknown 'dead end'
        else:
            self.graph.speed_limited(True) # limit max speed so that we don't get caught in speed based unknown 'dead ends' during exploration

        change_path = self.path_changed(changed)
        with_markers = True  # if true will draw markers for search nodes, looks good but slows down search
        if change_path or self.path == None:
            if self.algorithm == 'Dijkstra':
                path = self.graph.dijkstra_path_s(self.display, node, goals, with_markers) # returns path
            else:
                path = self.graph.astar_path_s(self.display, node, goals, with_markers) # returns path
            self.path = deepcopy(path)
        path = self.path
        move = self.graph.move_on_path(node, goals, path) # returns move = [action, next_state, cost]
        
        state = move[1]
        if state.cell in goals:
            # reached current goal, either maze.goals or start
            if self.phase == 'exploring' or self.phase == 'racing': 
                self.phase = 'returning'
                self.path = None
            elif self.phase == 'returning':
                self.phase = 'racing' # this will cause the mouse to race over and over unless stopped by externally
                self.path = None

        return move


    def path_changed(self, changed):
        change_path = False
        path = self.path
        if path != None:
            for i, node in enumerate(path[1:-1]): # for each node in path, excluding first and last nodes
                next_cell = path[i+2].cell
                for cell_pair in changed:
                    if node.cell == cell_pair[0] or node.cell == cell_pair[1]:
                        # this may be an impacted path
                        if next_cell == cell_pair[0] or next_cell == cell_pair[1]:
                            # need to change path
                            change_path = True
                            return change_path
        return change_path


    def update_map(self, sensor_data):
        '''updates mouse.maze with the sensor_data'''
        (y, x) = cell_to_maze(self.maze.info, self.state.cell)
        walls = self.maze.walls
        # build map with sensor_data
        # remember that maze coords increase down!! and to the right

        # if we're at the center
        # +---------+----1----+---------+
        # |         |    |    |         |
        # |         9    |    9         |  diagram of the 5
        # |         |\   |   /|         |  sensor vectors
        # +---------+26-73-26-+---------+  and signal strengths
        # |         |   \|/   |         |  if there is a wall
        # 1 ------ 24 -- o -- 25 ------ 1  for loc == 0
        # |         |         |         |
        # +---------+---------+---------+
        maze = self.maze
        walls = maze.walls
        far, near = get_sensor_vectors(maze, self.state) # get a list of walls we'd see for both far and near walls
        delay = 0.1
        changed = []
        ir_id = []
        for i, s in enumerate(sensor_data):
            f = far[i]
            n = near[i]
            #ir = None
            if s > 0 and s == n.s: 
                # detected a near wall, set the wall if we detected it for the first time
                if self.set_wall(n.y, n.x): # set_wall will set the wall if not there and return True if changed
                    cell_pair = self.impacted_cells(n.y, n.x)# find cells on either side of wall
                    changed.append(cell_pair)
                ir_id.append(self.display.draw_ir(maze, self.state, (n.y, n.x)))
            else:
                # detected a far wall
                if s > 0 and s == f.s: 
                    if self.set_wall(f.y, f.x):  # set_wall will set the wall if not there and return True if changed
                        cell_pair = self.impacted_cells(f.y, f.x)# find cells on either side of wall
                        changed.append(cell_pair)
                ir_id.append(self.display.draw_ir(maze, self.state, (f.y, f.x)))
        time.sleep(delay)
        for ir in ir_id:
            self.display.delete_id(ir)
        return changed


    def impacted_cells(self, my, mx):
        """ returns tuple of two cells on either side of wall at my, mx
        """
        (row_num, col_num) = self.maze_info
        # find orientation of wall
        if my % 2 == 0:
            # it's a horizontal wall
            cy0 = row_num - (my >> 1)
            cy1 = cy0 - 1
            cx0 = (mx >> 1)
            cx1 = cx0
        else:
            # it's a vertical wall
            cy0 = row_num - (my >> 1) - 1
            cy1 = cy0
            cx0 = (mx >> 1)
            cx1 = cx0 - 1
        return ((cy0, cx0), (cy1, cx1))


    def set_wall(self, y, x):
        changed = False
        if self.maze.walls[y][x] != 1:
            self.maze.walls[y][x] = 1
            draw_wall(self.display, y, x)
            changed = True
        return changed


