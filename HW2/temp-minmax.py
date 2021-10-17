'''
    Name: Armin Bazarjani
    Course: CSCI-561 Foundations of Artificial Intelligence
    Date: October 4, 2020
    
    Homework 2: Reinforcement Learning for the Game of "Little-GO"
'''
import os
import copy
import time
import random

class MyPlayer():
    # init the mini-max player
    def __init__(self, border_size, side=None):
        self.border_size = border_size
        self.input = 'input.txt'
        self.output = 'output.txt'
        self.state = []
        self.prev_state = []

    # read input file and store the data
    def read_input(self):
        index = 0
        with open(self.input, 'r') as f:
            for line in f.readlines():
                if index == 0:
                    self.side = int(line.strip())
                elif index < 6:
                    self.prev_state.append([])
                    for i in range(5):
                        self.prev_state[index-1].append(int(line.strip()[i]))
                else:
                    self.state.append([])
                    for i in range(5):
                        self.state[index-6].append(int(line.strip()[i]))
                index+=1
    
    # function that writes output file
    def write_output(self, move):
        with open(self.output, 'w') as f:
            if move == 'PASS':
                f.write(move)
            else:
                f.write(str(move[0])+','+str(move[1]))

    def heuristic(self, state, side):
        player, other = 0, 0
        sum = 0
        for i in range(self.border_size):
            for j in range(self.border_size):
                if state[i][j] == self.side:
                    player += 1
                    sum+=(player + self.count_liberty(state, i, j))
                elif state[i][j] == 3 - self.side:
                    other += 1
                    sum-=(other + self.count_liberty(state, i, j))
        return sum if side == self else -sum
        
    # find dead points as a list for a given side
    def find_dead(self, state, side):
        dead_points = []
        for i in range(self.border_size):
            for j in range(self.border_size):
                if state[i][j] == side:
                    if self.count_liberty(state, i, j) == 0:
                        dead_points.append((i, j))
        return dead_points


    # remove the dead_points of a given side
    def remove_dead(self, state, side):
        dead_points = self.find_dead(state, side)
        for point in dead_points:
            state[point[0]][point[1]] = 0
        return state

    # remove dead stones and returns adjacent stones in range
    def find_adjacent(self, state, row, col):
        state = self.remove_dead(state, (row, col))
        neighbors = []
        if row > 0: neighbors.append((row-1, col))
        if row < self.border_size - 1: neighbors.append((row+1, col))
        if col > 0: neighbors.append((row, col-1))
        if col < self.border_size - 1: neighbors.append((row, col+1))
        return neighbors

    # return the given point's allies as a list
    def find_adjacent_neighbors(self, state, row, col):
        allies = list()
        for point in self.find_adjacent(state, row, col):
            if state[point[0]][point[1]] == state[row][col]:
                allies.append(point)
        return allies

    # Using DFS to find all allies of a given point
    def find_ally_cluster(self, state, row, col):
        stack = [(row, col)]
        ally_members = list()

        while stack:
            point = stack.pop(0)
            ally_members.append(point)
            # if ally nieghbors not empty, add them to ally_members
            for neighbor in self.find_adjacent_neighbors(state, point[0], point[1]):
                if neighbor not in stack and neighbor not in ally_members:
                    stack.append(neighbor)
        return ally_members

    # return the count of a give point's liberty
    def count_liberty(self, state, row, col):
        count = 0
        # loop through each point in the cluster
        for point in self.find_ally_cluster(state, row, col):
            # if the point has an adjacent node with a value of 0, then the cluster has liberty
            for neighbor in self.find_adjacent(state,  point[0], point[1]):
                if state[neighbor[0]][neighbor[1]] == 0:
                    count += 1

        return count

    # check if KO or not
    def if_ko(self, prev_state, state):
        for i in range(self.border_size):
            for j in range(self.border_size):
                if state[i][j] != prev_state[i][j]:
                    return False
        return True

    def valid_check(self, state, prev_state, player, row, col):
        if state[row][col] != 0:
            return False
        test = copy.deepcopy(state)
        test[row][col] = player
        dead_pieces = self.find_dead(test, 3 - player)
        test = self.remove_dead(test, 3 - player)
        # find ally cluster of position
        # if cluster has liberty, add position to valid_moves list
        if self.count_liberty(test, row, col) >= 1 and not (dead_pieces and self.if_ko(prev_state, test)):
            # add point to valid moves list
            return True

    # return a list of valid moves given current gameboard position
    def valid_moves(self, state, prev_state, player):
        moves = []
        # loop through the entire gameboard
        for i in range(self.border_size):
            for j in range(self.border_size):
                # position that has a 0 is empty
                if self.valid_check(state, prev_state, player, i, j) == True:
                    moves.append((i, j))
        return moves

    # mini-max algorithm return the move or moves with the max heuristic value
    def minmax(self, max_depth, alpha, beta):
        # intialize helper variables
        moves = []
        best = 0
        curr_state_copy = copy.deepcopy(self.state)

        # check all nine states to get the max
        for move in self.valid_moves(self.state, self.prev_state, self.side):
            # update the next state board
            next_state = copy.deepcopy(self.state)
            next_state[move[0]][move[1]] = self.side
            next_state = self.remove_dead(next_state, 3-self.side)

            # get evaluation of each state
            curr_score = -self.minmax_iter(next_state, curr_state_copy, max_depth,
                                     alpha, beta, 3-self.side)
            
            # updating alpha cause it's a max level
            if curr_score > best or not moves:
                best = curr_score
                alpha = best
                moves = [move]
            # in case of more than one best moves
            elif curr_score == best:
                moves.append(move)
        return moves

    # the minimax function that iterates through the depth of branches
    def minmax_iter(self, curr_state, prev_state, max_depth, alpha, beta, side):
        heur_val = self.heuristic(curr_state, side)
        if max_depth == 0:
            return heur_val
        best = heur_val
        curr_state_copy = copy.deepcopy(curr_state)
        # iterate through all valid moves
        for move in self.valid_moves(curr_state, prev_state, side):
            # update the next board state
            next_state = copy.deepcopy(curr_state)
            next_state[move[0]][move[1]] = side
            next_state = self.remove_dead(next_state, 3-side)

            # get heuristic of next state
            curr_score = -self.minmax_iter(next_state, curr_state_copy, max_depth - 1,
                                     alpha, beta, 3-side)

            # check if new result is better than current best
            if curr_score > best:
                best = curr_score
            # update the score
            new_score = -1 * best

            # Alpha beta pruning
            # if we are looking at the minimizing player (opponent)
            if side == 3-self.side:
                player = new_score
                # check if prune
                if player < alpha:
                    return best
                # if we dont prune, update beta
                if best > beta:
                    beta = best
            # if we are looking at the maximizing player (ourselves)
            elif side == self.side:
                opponent = new_score
                # check prune
                if opponent < beta:
                    return best
                # if we dont prune, update alpha
                if best > alpha:
                    alpha = best

        return best


if __name__ == "__main__":
    start = time.time()
    my_player = MyPlayer(5)
    my_player.read_input()

    checker = 0
    checker_bool = False
    for i in range(5):
        for j in range(5):
            if my_player.state[i][j] != 0:
                if i == 2 and j == 2:
                    checker_bool = True
                checker += 1

    if (checker == 0 and my_player.side == 1) or (checker == 1 and my_player.side == 2 and checker_bool is False):
        action = [(2, 2)]
    else:
        action = my_player.minmax(2, -1000, -1000)
        print(action)
    # if empty list, then no action, choose to pass
    if action == []:
        rand_action = ['PASS']
    # else choose a random action from the list
    else:
        rand_action = random.choice(action)

    my_player.write_output(rand_action)
    end = time.time()
    print(f'total time of evaluation: {end-start}')
