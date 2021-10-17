'''
Author: Yanpeng Zhuo
Github: https://github.com/zhuoyanpeng
Date: 2021-09-12 07:42:51
LastEditors: Yanpeng Zhuo
Description: file content
'''
import numpy as np
import time
import json
import ujson
import random
import sys
from read import readInput
from write import writeOutput
from host import GO

WIN_REWARD = 1.0
DRAW_REWARD = 0.5
LOSS_REWARD = 0.0

class MyPlayer():
    def __init__(self, alpha=0.7, gamma=0.9, initial_value=0.5, side=None):
        self.type = 'q-learner'
        self.side = side
        self.alpha = alpha
        self.gamma = gamma
        self.q_values = {}
        with open("learning.json", 'r') as f:
            self.q_values = ujson.load(f)
        self.history_states = []
        self.initial_value = initial_value

    def set_side(self, side):
        self.side = side

    def learn(self, result, alpha=.7, gamma=.9):
        #print("----------learning----------")
        if result == 0:
            #print('tie')
            reward = DRAW_REWARD
        elif result == self.side:
            #print("win")
            reward = WIN_REWARD
        else:
            #print("loose")
            reward = LOSS_REWARD

        self.history_states.reverse()
        max_q_value = -1.0
        for hist in self.history_states:
            state, move = hist
            q = self.getQ(state)
            if max_q_value < 0:
                q[move[0]][move[1]] = reward
            else:
                q[move[0]][move[1]] = round(q[move[0]][move[1]] * (1 - self.alpha) + self.alpha * (self.gamma * max_q_value), 4)
            max_q_value = np.max(q)
        self.history_states = []
        
    def save(self):
        with open('learning.json', 'w') as json_file:
            json.dump(self.q_values, json_file)

    def getQ(self, state):
        if state not in self.q_values:
            q_val = np.zeros((5, 5))
            q_val.fill(self.initial_value)
            self.q_values[state] = q_val.tolist()
        return self.q_values[state]

    def select_move(self, go, piece_type):
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check = True):
                    possible_placements.append((i,j))
        if not possible_placements:
            return "PASS"
        
        state = encode_state(go.board)
        q_values = self.getQ(state)
        row, col = 0, 0
        curr_max = -np.inf
        while True:
            #print("qqq")
            i, j = self._find_max(q_values)
            go.verbose = True
            if go.valid_place_check(i, j, piece_type, test_check = True):
                return (i, j)
            else:
                q_values[i][j] = -1.0

    def _find_max(self, q_values):
        curr_max = -np.inf
        row, col = 0, 0
        for i in range(0, 5):
            for j in range(0, 5):
                if q_values[i][j] > curr_max:
                    curr_max = q_values[i][j]
                    row, col = i, j
        return row, col
    
    def get_input(self, go, piece_type):
        #start = time.time()
        move = self.select_move(go, piece_type)
        if move == 'PASS':
            return move
        row, col = move
        self.history_states.append((encode_state(go.board), (row, col)))
        #print("q-learning step: ", time.time() - start)
        return (row, col)

def encode_state(state):
        """ Encode the current state of the board as a string
        """
        return ''.join([str(state[i][j]) for i in range(5) for j in range(5)])


if __name__ == "__main__":
	    # result_dic = json.load(j)
    # with open('result.txt', 'w') as json_file:
    #     json.dump(result_dic, json_file)
    N = 5
    piece_type, previous_board, board = readInput(N)
    # piece_type 1: 黑子  2: 白子
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = MyPlayer()
    # with open("learning.json", "r") as j:
	#     player.q_values = json.load(j)
    # with open('person.txt', 'w') as json_file:
    # json.dump(person_dict, json_file)
    action = player.get_input(go, piece_type)
    writeOutput(action)
