# This is where all the player functions and class will be implemented.
import copy
import pygame
import GameBoard

class Player():
    def __init__(self, order, tiles, gameDisplay):
        # Initiate CPU to go first or second.
        self.order = order
        self.tiles = tiles
        self.gameDisplay = gameDisplay
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
        while(len(self.pieces) > 0):
            del self.pieces[0]
        while(len(self.enemy_pieces) > 0):
            del self.enemy_pieces[0]

    # Checkmate function:
    def is_checkmate(self, piece, pieces, enemy_pieces):
        # Check to see if we can be checkmated
        # Check to see if we caused checkmate
        pass

    def gained_material(self, piece, pieces, enemy_pieces, curr_diff):
        move_diff = self.calc_diff(pieces, enemy_pieces)
        # Add in weight:
        weight = 10
        return weight * (move_diff - curr_diff)

    def is_supported(self, piece, pieces, enemy_pieces):
        # Check to see the support for each friendly piece
        pass

    def is_attacked(self, piece, pieces, enemy_pieces):
        # Check to see the attack options of each enemy piece
        pass

    def can_attack(self, piece, pieces, enemy_pieces):
        # Check to see if there are any pieces we can attack.
        pass

    def win_exchange(self, piece, pieces, enemy_pieces):
        # Check to see whether or not we win an exchange
        pass

    def square_concentration(self, piece, pieces, enemy_pieces):
        # Check to see if we can brute force our way onto a square.
        pass

    def calc_diff(self, pieces, enemy_pieces):
        adder = 0
        for piece in pieces:
            if piece.name == "Pawn":
                adder += 1
            if piece.name == "Bishop":
                adder += 3
            if piece.name == "Knight":
                adder += 3
            if piece.name == "Rook":
                adder += 5
            if piece.name == "Queen":
                adder += 9
        subtractor = 0
        for piece in enemy_pieces:
            if piece.name == "Pawn":
                subtractor += 1
            if piece.name == "Bishop":
                subtractor += 3
            if piece.name == "Knight":
                subtractor += 3
            if piece.name == "Rook":
                subtractor += 5
            if piece.name == "Queen":
                subtractor += 9
        return adder - subtractor

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
                # Reset the pieces after every move calculation:
                copy_pieces = copy.deepcopy(self.pieces)
                copy_enemy_pieces = copy.deepcopy(self.enemy_pieces)

                # Set a current diff measure to calculate diff score:
                current_diff = self.calc_diff(copy_pieces, copy_enemy_pieces) 

                # Make the move we need to evaluate:
                piece.move_piece(self.tiles[piece.potential_moves[move][0]*8+piece.potential_moves[move][1]],
                                self.tiles, copy_pieces, copy_enemy_pieces, self.gameDisplay, True, True)

                # Reset current move evaluation to 0.
                current_move = 0

                # Perform all evaluations here
                current_move += self.is_checkmate(piece, copy_pieces, copy_enemy_pieces)
                current_move += self.gained_material(piece, copy_pieces, copy_enemy_pieces, current_diff)
                current_move += self.is_supported(piece, copy_pieces, copy_enemy_pieces)
                current_move += self.is_attacked(piece, copy_pieces, copy_enemy_pieces)
                current_move += self.can_attack(piece, copy_pieces, copy_enemy_pieces)
                current_move += self.win_exchange(piece, copy_pieces, copy_enemy_pieces)
                current_move += self.square_concentration(piece, copy_pieces, copy_enemy_pieces)

                # Check to see if the evaluation is the best move:
                if current_move > best_move_value:
                    # If it is, then update our best move
                    best_move_pos = move
                    best_piece_index = counter

                # Destroy the current state of the pieces:
                while(len(copy_pieces) > 0):
                    del copy_pieces[0]
                while(len(copy_enemy_pieces) > 0):
                    del copy_enemy_pieces[0]

                if(len(copy_pieces) > 0 or len(copy_enemy_pieces) > 0):
                    print("Pieces not being deleted correctly!")
                    exit()
                
            counter += 1
            #After performing the given evaluation, we should delete all pieces:
            self.destroy_pieces()
        # Return best_piece_index and best_move_pos to allow CPU to make move
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