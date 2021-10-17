'''
Author: Yanpeng Zhuo
Github: https://github.com/zhuoyanpeng
Date: 2021-09-01 09:57:17
LastEditors: Yanpeng Zhuo
Description: file content
'''
import time
import math
from queue import PriorityQueue
# the function to read the input file
# stores all the channels in the form of a list
# stores initial state and final state as tuple
grid_info = {}
path_info = {}
solution = 0
solved = False
def read_input_file():
    with open("input.txt") as file:
        # Instruction of which algorithm to use,as a string: BFS, UCS or A
        algorithm = file.readline().strip()
        size = list(map(int, file.readline().strip().split(' ')))
        entrance = tuple(list(map(int, file.readline().strip().split(' '))))
        exit = tuple(list(map(int, file.readline().strip().split(' '))))
        grid_number = file.readline().strip()

        grid_info['algorithm'] = algorithm
        grid_info['size'] = size
        grid_info['entrance'] = entrance
        grid_info['exit'] = exit
        direction_map = [(0,0,0),(1,0,0),(-1,0,0),(0,1,0),
                         (0,-1,0),(0,0,1),(0,0,-1),
                         (1,1,0),(1,-1,0),(-1,1,0),
                         (-1,-1,0),(1,0,1),(1,0,-1),
                         (-1,0,1),(-1,0,-1),(0,1,1),
                         (0,1,-1),(0,-1,1),(0,-1,-1)]
        for item in file.readlines():
            line = item.strip().split()
            point = (int(line[0]),int(line[1]),int(line[2]))
            path_info[point] = [0, (-1,-1,-1)]
            for j in range(3, len(line)):
                add = direction_map[int(line[j])]
                if int(line[j]) < 7:
                    path_info[point].append([(point[0]+add[0],point[1]+add[1],point[2]+add[2]),10])
                else:
                    path_info[point].append([(point[0]+add[0],point[1]+add[1],point[2]+add[2]),14])
            
def write_output_file():
    file = open("output.txt", "w")
    if solved == False:
        file.write("FAIL")
        return

    initPoint = grid_info['entrance']
    exitPoint = grid_info['exit']
    algorithm = grid_info['algorithm']
    point = exitPoint
    path = []
    while initPoint != point:
        cost = path_info[point][1][1]
        path.insert(0, (point, cost))
        point = path_info[point][1][0]
    path.insert(0, (point,0))

    if algorithm == "BFS":
        file.write(str(len(path) - 1) + '\n')
    else:
        file.write(str(solution) + '\n')
    
    file.write(str(len(path)) + '\n')
    for step in path:
        vertex, cost = step
        file.write(str(vertex[0]) + ' ' + str(vertex[1]) + ' ' + str(vertex[2]) + ' ' +  str(cost) + '\n')
    file.close()

def pick_algorithm():
    algorithm = grid_info['algorithm']
    if algorithm == "BFS":
        bfs_search()
    elif algorithm == "UCS":
        ucs_search()
    elif algorithm == "A*":
        a_search()

def distance(start, end):
    x = abs(start[0] - end[0]) * 10
    y = abs(start[1] - end[1]) * 10
    z = abs(start[2] - end[2]) * 10
    return math.sqrt(x*x + y*y + z*z)
    
def boundaryTest(point):
    x,y,z = grid_info['size']
    a,b,c = point
    return a>=x or b>=y or c>=z or a<0 or b<0 or c<0
    
def bfs_search():
    initPoint = grid_info['entrance']
    exitPoint = grid_info['exit']
    queue = []
    if boundaryTest(initPoint) == False:
        queue.append(initPoint)
        path_info[initPoint][0] = 1 ##store the visited status
    while queue:
        point = queue.pop(0)
        for x in range(2, len(path_info[point])):
            node = path_info[point][x][0]
            if boundaryTest(node):
                continue
            if node == exitPoint:
                path_info[node][1] = (point, 1)
                global solved
                solved = True
                return
            elif path_info[node][0] == 0:
                path_info[node][0] = 1
                path_info[node][1] = (point, 1)
                queue.append(node)
    ## if queue is empty means all node is visited but no result found 
    ## global solved default value is false nothing needs to do

def ucs_search():
    initPoint = grid_info['entrance']
    exitPoint = grid_info['exit']
    global solution
    global solved
    queue = PriorityQueue()
    
    if boundaryTest(initPoint) == False:
        queue.put((0, initPoint))
        path_info[initPoint][0] = 1 ##store the visited status
    while queue.empty() == False:
        pop = queue.get()
        oldCost = pop[0]
        point = pop[1]
        for x in range(2, len(path_info[point])):
            node = path_info[point][x][0]
            cost = path_info[point][x][1]
            if boundaryTest(node) or path_info[node][0] == 1:
                continue
            elif node == exitPoint:
                if solution == 0:
                    solution = oldCost + cost
                    path_info[node][1] = (point,cost)
                else:
                    if oldCost + cost < solution:
                        solution = oldCost + cost
                        path_info[node][1] = (point,cost)
                solved = True
            else:
                path_info[node][0] = 1
                queue.put((oldCost + cost, node))
                path_info[node][1] = (point, cost)
    ## if queue is empty means all node is visited but no result found 
    ## global solved default value is false nothing needs to do
    
def a_search():
    initPoint = grid_info['entrance']
    exitPoint = grid_info['exit']
    global solution
    global solved
    queue = PriorityQueue()
    if boundaryTest(initPoint) == False:
        queue.put((0 + distance(initPoint, exitPoint), 0, initPoint))
        path_info[initPoint][0] = 1 ##store the visited status
    while queue.empty() == False:
        pop = queue.get()
        oldCost = pop[1]
        point = pop[2]
        for x in range(2, len(path_info[point])):
            node = path_info[point][x][0]
            cost = path_info[point][x][1]
            if boundaryTest(node):
                continue
            if node == exitPoint:
                if solution == 0:
                    solution = oldCost + cost
                    path_info[node][1] = (point, cost)
                else:
                    if oldCost + cost < solution:
                        solution = oldCost + cost
                        path_info[node][1] = (point, cost)
                solved = True
            elif path_info[node][0] == 0:
                path_info[node][0] = 1
                queue.put((oldCost + cost + distance(node, exitPoint), oldCost + cost, node))
                path_info[node][1] = (point, cost)

start_time = time.time()
read_input_file()
print('readTime: ', time.time() - start_time)
# print(grid_info)
# for i in path_info:
#     print(i, ': ', path_info[i])

pick_algorithm()
print('algorithm: ', time.time() - start_time)
# for i in path_info:
#     print(i, ': ', path_info[i])
write_output_file()
end_time = time.time()
print('writeTime: ', end_time - start_time)
