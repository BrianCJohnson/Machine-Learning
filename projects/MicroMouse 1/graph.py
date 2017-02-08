from common import State, cell_to_maze, cell_delta_to_dir
import random
import Queue
import time
from display import draw_marker, update_value


class Graph(object):
    def __init__(self, maze, type = 'MRF'):
        """ creates a graph object from 2D maze 
            each node is a tuple contains the 2D coordinates (cy, cx) of the maze
            plus other state information depending on type:
            type=='MCF' = 'manhattan, cartesian, fixed speed'   
            type=='MCV' = 'manhattan, cartesian, variable speed' 
            type=='MRF' = 'manhattan, rotation, fixed speed'      
            type=='MRV' = 'manhattan, rotation, variable speed'    
            type=='SPF' = 'smooth path, fixed speed'           
            type=='SPV' = 'smooth path, variable speed'       
        """
        self.__maze = maze
        self.__type = type
        self.__speed_limited = True
        self.__searchs = 0
        self.__time = 0
        self.__max_time = 0
        self.__nodes = 0
        self.__max_nodes = 0

    def speed_limited(self, limited):
        self.__speed_limited = limited
        return

    def moves(self, node):
        """ returns a list of possible move from the current node/state
            each move = (action, new_node/state, cost)
        """
        connected_cells = self.connected_cells(node)
        type = self.__type
        #node_y, node_x = node.cell
        moves = []
      
        if type == 'MRF': # manhattan, rotation, fixed speed
            # actions = ('F', '90', '180', '270')
            actions = ('F', '90', '180', '270')
            dir = node.dir # dir = 0-7, (N, E, S, W)
            for cell in connected_cells:
                # move forward in dir to next cell
                new_dir = cell_delta_to_dir(node.cell, cell)
                if new_dir == dir:
                    action = actions[0]
                    new_node = State(cell, 0, new_dir, 0)
                    moves.append((action, new_node, self.cost(type, node, action, new_node))) # go forward in current direction
            # stay in same location, rotate
            # rotate 90, 180, 270
            for rot in range(1,4):
                new_dir = (dir + 2*rot) % 8
                action = actions[rot]
                new_node = State(node.cell, 0, new_dir, 0)
                moves.append((action, new_node, self.cost(type, node, action, new_node)))

        elif type == 'MRV': # manhattan, rotation, variable speed
            actions = ('VM', 'VS', 'VP', '90', '180', '270')
            dir = node.dir
            spd = node.spd
            if self.__speed_limited:
                speeds = 1 # limit max speed so that we don't get caught in speed based unknown 'dead ends' during exploration
            else:
                speeds = 3 # allow 3 different speeds in each direction including 0
            for cell in connected_cells:
                # move forward in dir to next cell if possible
                new_dir = cell_delta_to_dir(node.cell, cell)
                if new_dir == dir: # cell is in direction we're headed
                    if spd == 0: 
                        action = actions[1] # velocity stays the same, starts at 0, ends at 0
                        new_node = State(cell, 0, dir, 0)
                        moves.append((action, new_node, self.cost(type, node, action, new_node))) # go forward in current direction and stop again
                        action = actions[2] # velocity increases, starts at 0, ends at 1
                        new_node = State(cell, 0, dir, 1)
                        moves.append((action, new_node, self.cost(type, node, action, new_node))) # go forward in current direction, increase speed to 1
                    else:
                        # spd is > 0
                        action = actions[0] # decrease speed
                        new_node = State(cell, 0, dir, spd - 1)
                        moves.append((action, new_node, self.cost(type, node, action, new_node))) # go forward in current direction and decrease speed
                        action = actions[1] # maintain speed
                        new_node = State(cell, 0, dir, spd)
                        moves.append((action, new_node, self.cost(type, node, action, new_node))) # go forward in current direction and maintain speed
                        if spd < speeds - 1:
                            # not at top speed
                            action = actions[2] # increase speed
                            new_node = State(cell, 0, dir, spd+1)
                            moves.append((action, new_node, self.cost(type, node, action, new_node))) # go forward in current direction and increase speed
                if spd == 0:
                    # we can stay in same location and rotate
                   
                    for rot in range(1,4): # rot:rotatation 1:90, 2:180, 3:270
                        new_dir = (dir + 2*rot) % 8
                        action = actions[rot + 2]
                        new_node = State(node.cell, 0, new_dir, 0)
                        moves.append((action, new_node, self.cost(type, node, action, new_node)))


        elif type == 'SPF': # smooth path, fixed speed
            actions = ('L', 'M', 'R', '90', '180', '270') # Left, Middle, Right, rotate 90, 180, 270 (90 and 270 speed up navigation in unknown maze)
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
            for cell in connected_cells:
                # move forward in dir to next cell if possible
                dir_to_cell = cell_delta_to_dir(node.cell, cell) # returns a 0,2,4,6 direction
                next_pos = {'L':(3,4,1,2), 'M':(0,0,0,0), 'R':(2,3,4,1)} # then next pos given the action and the entry dir
                next_dir = {'L':(7,1,3,5), 'M':(0,2,4,6), 'R':(1,3,5,7)} # then next dir given the action and the entry dir
                position =  ((0, 4, 1), (0, 1, 2), (0, 2, 3), (0, 3, 4))
                direction = ((7, 0, 1), (1, 2, 3), (3, 4, 5), (5, 6, 7))
                pos = node.pos
                dir = node.dir
                spd = 0 # in this movement strategy we always stop
                if pos in position[dir_to_cell >> 1] and dir in direction[dir_to_cell >> 1]: # shifting to convert 0,2,4,6 to 0,1,2,3
                    # the connected cell is in the direction we're heading
                    for action in actions[:3:]:
                        new_pos = next_pos[action][dir_to_cell >> 1]
                        new_dir = next_dir[action][dir_to_cell >> 1]
                        dir_change_p = (new_dir - dir + 9) % 8 # direction change could be 7, 0, 1, dir_change plus 1 should be 0, 1, 2
                        #if not self.__speed_limited or dir_change_p < 3: 
                        # if we're in exploration (speed_limited) and the change in direction is +/- 2 then we might be turning into an unseen/unknown wall and become trapped
                        # this makes sure we only turn 90 when speed is not limited
                        new_node = State(cell, new_pos, new_dir, spd)
                        moves.append((action, new_node, self.cost(type, node, action, new_node))) # move to the connected cell with each of the actions (except rotation)
            if node.pos == 0:
                # the center position
                for i, action in enumerate(actions[3:]):
                    dir_change = (i + 1) << 1 # (i +1) << 1 = change in direction
                    new_dir = (node.dir + dir_change) % 8
                    new_node = State(node.cell, node.pos, new_dir, spd)
                    moves.append((action, new_node, self.cost(type, node, action, new_node))) # move to the connected cell with each of the actions (except rotation)

        
        elif type == 'SPV': # smooth path, variable speed
            actions = ('LM', 'LS', 'LP', 'SM', 'SS', 'SP', 'RM', 'RS', 'RP', '180')
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
            pos, spd = node[2:3:]
            for cell in connected_cells:
                # move forward in dir to next cell if possible
                dir_to_cell = cell_delta_to_dir((node_y, node_x), cell) # returns a 0-3 direction
                #cy, cx = cell
                cell_exit_dir = [0, 1, 2, 3, 1, 1, 2, 0, 0, 2, 3, 3] # the dir (0-3) that the pos will exit the cell
                exit_dir = cell_exit_dir[pos]
                new_pos = {'L':(11,8,5,6), 'M':(0,1,2,3), 'R':(4,9,10,7)} # then next pos given the action and the entry dir
                if cell_exit_dir == dir_to_cell:
                    # the connected cell is in the direction we're heading
                    for action in actions[:3:]:
                        new_pos = next_pos[action][cell_dir]
                        new_node = (cy, cx, new_pos)
                        moves.append(action, new_node, self.cost(type, node, action, new_node)) # move to the connected cell with each of the actions (except rotation)
            if pos < 4:
                # the center position
                action = actions[3]
                new_pos = (pos + 4) % 8
                new_node = (cy, cx, new_pos)
                moves.append(action, new_node, self.cost(type, node, action, new_node)) # move to the connected cell with each of the actions (except rotation)
 
        else:
            raise ValueError('Unknown type:', type)

        return moves


    def connected_cells(self, node):
        """returns the cells (coordinates) of neighboring cells which are not separated by a wall
        """
        cells = []
        maze = self.__maze
        walls = maze.walls
        cy, cx = node.cell
        my, mx = cell_to_maze(maze.info, (cy, cx))
        if walls[my-1][mx  ] == 0: # look up (y is - on maze.walls, + on cells)
            cells.append((cy+1, cx  ))
        if walls[my+1][mx  ] == 0: # look down (y is + on maze.walls, - on cells)
            cells.append((cy-1, cx  ))
        if walls[my  ][mx-1] == 0: # look left
            cells.append((cy  , cx-1))
        if walls[my  ][mx+1] == 0: # look right
            cells.append((cy  , cx+1))
        return cells


    def cost(self, type, node, action, new_node):
        #            type:{(pos, spd): {action: cost, ...}}
        # costs need to be checked and updated !!!
        bend_90   = 0.179
        bend_45   = 0.228
        straight  = 0.383
        diagonal  = 0.2
        rotate_90 = 0.226
        rotate180 = 0.320
        all_costs = {'MRF': {('center', 0): {'F': straight, '90': rotate_90, '180': rotate180, '270': rotate_90}},
                     'MRV': {('center', 0): {'VS': straight, 'VP': 0.271, '90': rotate_90, '180': rotate180, '270': rotate_90},
                             ('center', 1): {'VM': 0.271, 'VS': 0.122, 'VP': 0.112},
                             ('center', 2): {'VM': 0.090, 'VS': 0.122}},
                     'SPF': {('center', 0): {'L': bend_45, 'M': straight, 'R': bend_45, '90': rotate_90, '180': rotate180, '270': rotate_90},
                             ('ccwise', 0): {'L': diagonal, 'M': bend_45, 'R': bend_90},
                             ('c_wise', 0): {'L': bend_90, 'M': bend_45, 'R': diagonal}}}
        type_costs = all_costs[type]
        if action in ('MRF', 'MRV'):
            costs = type_costs[('center', node.spd)]   
        else:
            if node.pos == 0:
                costs = type_costs[('center', node.spd)] 
            else:
                rotation = 'c_wise'
                if (node.pos, node.dir) in ((1, 7), (2, 1), (3, 3), (4, 5)):
                    # counter clockwise
                    rotation = 'ccwise'
                costs = type_costs[(rotation, node.spd)]
        cost = costs[action]     
        return cost


    def move_on_path(self, start_node, goals, path):
        """ find node on path of nodes/states, 
            return the move that gets us from node to next node
        """
        found_start = False
        for i in range(1, len(path)):
            if path[i] == start_node: 
                found_start = True
                try:
                    next_node = path[i+1]
                    break
                except:
                    a = 0
        if found_start:
            #start = path[1]
            #first_step = path[2]
            moves = self.moves(start_node)
            for move in moves:
                if move[1] == next_node: # return the move from the current node that takes us from the current node to the next_node
                    break
        else:
            raise Exception("error in move_on_path, didn't find start_node ")
        if not (move[1] == next_node):
            raise Exception("error in move_on_path, didn't find next_node ")
        return move


    def heuristic(self, goals, next):
        """returns an estimated cost based on goals and node
        """
        cell = next.cell
        # calculate straight line distance 
        min_dist = 1000
        for goal in goals:
            x_dist = abs(goal[1] - cell[1]) 
            y_dist = abs(goal[0] - cell[0])
            dist = min(y_dist, 1) + min(x_dist, 1) # if dist not zero, at least 1 turn is required
            if dist < min_dist: min_dist = dist
        # assuming cost is 1 per move/rotation
        cost_per_move = 0.3
        estimated_cost = min_dist * cost_per_move
        return estimated_cost
  
    #value_labels = ('Maze', 'Search Time', 'Avg Time', 'Max Time', 'Search Nodes', 'Avg Nodes', 'Max Nodes', 'Total Time', '1st Run', '2nd Run', '3rd Run', '4th Run')

    def astar_path_s(self, display, node, goals, with_markers):
        start= time.clock()
        #if node.cell == (4, 12):
        #    debug = 0
        frontier = Queue.PriorityQueue()
        node_cost = 0
        frontier.put((node_cost, node))
        parent = {}
        cost_so_far = {}
        parent[node] = None
        cost_so_far[node] = node_cost
        found_goal = False
        markers = []
        while not frontier.empty():
            update_value('Search Time', time.clock() - start)
            update_value('Search Nodes', len(cost_so_far))
            cost, current = frontier.get()
            if with_markers: markers.append(draw_marker(display, current, 'right', 3, 'red'))
            if current.cell in goals and current.spd == 0 and current.pos == 0:
                found_goal = True
                break
            moves = self.moves(current)
            for move in moves:
                next = move[1]
                cost_to_next = move[2]
                new_cost = cost_so_far[current] + cost_to_next
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    frontier.put((new_cost + self.heuristic(goals, next), next))
                    parent[next] = current
        # now trace back parents to None
        if found_goal:
            path = [current]
            while current != None:
                current = parent[current]
                path.append(current)
            path.reverse()
        else:
            path = None
        self.update_search_data(time.clock() - start, len(cost_so_far))
        if with_markers:
            for marker in markers:
                display.delete_id(marker)
        return path


    def dijkstra_path_s(self, display, node, goals, with_markers):
        start= time.clock()
        #if node.cell == (4, 12):
        #    debug=0
        frontier = Queue.PriorityQueue()
        node_cost = 0
        frontier.put((node_cost, node))
        parent = {}
        cost_so_far = {}
        parent[node] = None
        cost_so_far[node] = node_cost
        found_goal = False
        markers = []
        while not frontier.empty():
            #fl = frontier.qsize()
            #cl = len(cost_so_far)
            #pl = len(parent)
            update_value('Search Time', time.clock() - start)
            update_value('Search Nodes', len(cost_so_far))
            cost, current = frontier.get()
            if with_markers: markers.append(draw_marker(display, current, 'right', 3, 'red'))
            if current.cell in goals and current.spd == 0 and current.pos == 0:
                found_goal = True
                break
            moves = self.moves(current)
            for move in moves:
                next = move[1]
                cost_to_next = move[2]
                new_cost = cost_so_far[current] + cost_to_next
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    frontier.put((new_cost, next))
                    parent[next] = current
                    fl = frontier.qsize()
                    cl = len(cost_so_far)
                    pl = len(parent)
        # now trace back parents to None
        if found_goal:
            path = [current]
            while current != None:
                current = parent[current]
                path.append(current)
            path.reverse()
        else:
            path = None
        self.update_search_data(time.clock() - start, len(cost_so_far))
        if with_markers:
            for marker in markers:
                display.delete_id(marker)
        return path


    def update_search_data(self, time, nodes):
        self.__searchs += 1
        self.__time += time
        update_value('Avg Time', self.__time / self.__searchs)
        if time > self.__max_time:
            self.__max_time = time
            update_value('Max Time', self.__max_time)
        self.__nodes += nodes
        update_value('Avg Nodes', self.__nodes / self.__searchs)
        if nodes > self.__max_nodes:
            self.__max_nodes = nodes
            update_value('Max Nodes', self.__max_nodes)
        return

