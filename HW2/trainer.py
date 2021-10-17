'''
Author: Yanpeng Zhuo
Github: https://github.com/zhuoyanpeng
Date: 2021-10-14 08:58:52
LastEditors: Yanpeng Zhuo
Description: file content
'''
import sys
import time
from pathlib import Path
from host import GO
from random_player import RandomPlayer
from my_player3 import MyPlayer

PLAYER_X = 1
PLAYER_O = 2

def battle(player1, player2, iter):
    win = 0
    lose = 0
    tie = 0
    player1.set_side(PLAYER_X)
    start = time.time()
    for i in range(0, iter):
        if(i % 100 == 0):
            print(time.time() - start)
            start = time.time()
            print("---battle ", i, "---", i/iter*100, '%')
        go = GO(5)
        #go.verbose = True
        result = go.play(player1, player2, True)
        if result == 0:
            tie+=1
        elif result == 1:
            win+=1
        else:
            lose+=1
        player1.learn(result)
    
    player1.save()
    print("win: ", win)
    print("lose: ", lose)
    print("tie: ", tie)

if __name__ == "__main__":

    # Example Usage
    # battle(Board(show_board=True, show_result=True), RandomPlayer(), RandomPlayer(), 1, learn=False, show_result=True)
    # battle(Board(), RandomPlayer(), RandomPlayer(), 100, learn=False, show_result=True)
    # battle(Board(), RandomPlayer(), SmartPlayer(), 100, learn=False, show_result=True)
    # battle(Board(), RandomPlayer(), PerfectPlayer(), 100, learn=False, show_result=True)
    # battle(Board(), SmartPlayer(), PerfectPlayer(), 100, learn=False, show_result=True)
    start = time.time()
    print("开始创建")
    my_player = MyPlayer()
    player_two = RandomPlayer()
    print(time.time() - start)
    print("玩家创建完毕")
    NUM = 500000
    battle(my_player, player_two, NUM)
    #battle(player_two, my_player, NUM)
    
    
