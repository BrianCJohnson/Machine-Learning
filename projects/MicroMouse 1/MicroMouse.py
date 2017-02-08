import numpy as np
import time

from common import *
from mouse import *
from maze import *
from display import *


def main():

    # create maze
    maze_names = ["Test 6x4",       # 0
                  "Test 6x6",       # 1
                  "Empty 6x6",      # 2
                  "2016 Taiwan",    # 3
                  "2016 APEC",      # 4
                  "2015 All Japan"] # 5
    maze_index = 3
    maze_name = maze_names[maze_index]
    maze = Maze(maze_name)

    display = Display()  # create display
    draw_maze(display, maze)    # draw maze

    # select move_strategy
    move_strategy_names = ('MCF', # 0: manhattan, cartesian, fixed speed
                           'MCV', # 1: manhattan, cartesian, variable speed
                           'MRF', # 2: manhattan, rotation, fixed speed
                           'MRV', # 3: manhattan, rotation, variable speed
                           'SPF', # 4: smooth path, fixed speed
                           'SPV') # 5: smooth, variable speed
    move_strategy_index = 4
    move_strategy = move_strategy_names[move_strategy_index]
           
    # select search algorithm
    algorithm_names = ('Dijkstra',  # 0: Dijkstra
                        'A*')    # 1: A*
    algorithm_index = 1  # define seach algorithm
    algorithm = algorithm_names[algorithm_index]

    mouse = Mouse(maze.info, display, move_strategy, algorithm)    # create mouse

    delay = 0
    mouse_id = None
    mouse_id = draw_mouse(display, mouse_id, mouse)

    start = (0, 0)
    phase = 'At Start'
    running = True
    run = 0
    run_time = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] # total, run 1, return 1, run 2, return 2, run 3

    #value_labels = ('Maze', 'Motion', 'Algorithm', 'Search Time', 'Avg Time', 'Max Time', 'Search Nodes', 'Avg Nodes', 'Max Nodes', 'Total Time', '1st Run', '2nd Run', '3rd Run', '4th Run')
    update_value('Maze', maze_name)
    update_value('Motion', move_strategy)
    update_value('Algorithm',algorithm)
    total_time_index = value_labels.index('Total Time')

    while running:
        sensor_data = maze.sensor(mouse.state)
        move = mouse.move(sensor_data)
        mouse.state = move[1]
        mouse_id = draw_mouse(display, mouse_id, mouse)

        cell = mouse.state.cell
        if phase == 'At Start' and cell != start:
            phase = 'Racing'
            run += 1
        elif phase == 'Returning' and cell == start:
            phase = 'At Start'

        run_time[0] += move[2] # update total time with cost of move
        update_value(value_labels[total_time_index], run_time[0])

        run_time[run] += move[2] # add move time to run time
        update_value(value_labels[run + total_time_index], run_time[run])

        if phase == 'Racing':
            if cell in maze.goals:
                if run == 5:
                    running = False
                else:
                    phase = 'Returning' # allows the mouse to return to start another speed_run
                    run += 1
        
        #for i, rt in enumerate(run_time):
        #    update_time(i, rt)

        delay = max(move[2] - 0.1, 0.0)
        #time.sleep(delay)

    root.mainloop()


if __name__ == '__main__':
    main()


