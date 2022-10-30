from AutoPlayer import AutoPlayer
from Board import Board
from Game import Game
import os
from time import time
from functools import reduce

os.system('color')


game = Game()
game.createBoard(11,14,noWalls=9).createPlayers(playerX='auto', playerO='auto').play()

# board = Board()
# board.init(7,10,2)
# board = board.applyMove({'Player': ('X1', (2,5)), 'Wall': ('green', (1,3))})
# board = board.applyMove({'Player': ('O2', (6,6)), 'Wall': ('green', (2,7))})
# board.displayBoard()
# auto = AutoPlayer('X', board)
# board = auto.makeMove(board)
# board.displayBoard()