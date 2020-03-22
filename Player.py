# This is where all the player functions and class will be implemented.

import pygame
import GameBoard

class Player():
    def __init__(self, order):
        # Initiate CPU to go first or second.
        self.order = order
    # Create a function for every different evaluation performed and 
    # one to iterate through the given potential move.

    # Determines whose pieces are whose:
    def determine_pieces(self, player_1_pieces, player_2_pieces):
        if self.order == 1:
            self.pieces = player_1_pieces
            self.enemy_pieces = player_2_pieces
        else:
            self.pieces = player_2_pieces
            self.enemy_pieces = player_1_pieces

    # Destroys member variable pieces after turn is over:
    def destroy_pieces(self):
        for i in range(len(self.pieces)):
            del pieces[0]
        for i in range(len(self.enemy_pieces)):
            del enemy_pieces[0]

    # Checkmate function:
    def is_checkmate(self):
        pass


    # Perform evaluations for each potential turn:
    def evaluation(self):
        # Set overall best move:
        best_move_value = -1000000
        # Keep track of the position of the best move
        best_move_pos = None
        # Keep track of the piece with the best move by index
        best_piece_index = None
        # Iterate through all of the potential moves in CPU pieces:
        for piece in self.pieces:
            # Keep track of the piece index with counter
            counter = 0
            for move in piece.potential_moves:
                # Reset current move evaluation to 0.
                current_move = 0
                # Perform all evaluations
                current_move += self.is_checkmate()

                # Check to see if the evaluation is the best move:
                if current_move > best_move_value:
                    # If it is, then update our best move
                    best_move_pos = move
                    best_piece_index = counter
            counter += 1
        return best_piece_index, best_move_pos


"""
Documentation Section:

    1. Initialization:
        - Create the CPU in the gameboard initialization.
        - Determine order the CPU plays (1 or 2)
        - In the future, possibly add some sort of skill level
    2. Evaluation Strategy:
        - Evaluate linearly through all valid piece positions for ecah piece.
        - Total up the evaluation for a particular move and compare with previous highest
          using data from doc.
    3. The CPU Player Moves:
        - Pass the piece positions to the CPU to make a decision
        - Create copies of the pieces and assign them as member variables.
        - Perform evaluation strategy
        - Return the highest evaluated move as the move to make.
        - Delete the copies of pieces that we made.

"""