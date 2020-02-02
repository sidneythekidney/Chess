import pygame
import GameBoard
import Player

# Make a pygame window:
#Import the various chess pieces:

red = (255,0,0)
blue = (0,0,255)

new_game_board = GameBoard.GameBoard(blue, red, 900, 600)
new_game_board.play_game()
