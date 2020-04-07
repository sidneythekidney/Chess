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
        self.cen_score = 0
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
        # Check to see if we caused checkmate
        if (piece.checkmate(self.tiles, pieces, enemy_pieces, 1, self.gameDisplay) == 1):
            # We know we have clutched a checkmate, RP +1000000
            checkmate_score = 1000000
            return checkmate_score

        # Check to see if we can be checkmated in the next opponent move:
        for enemy_piece in enemy_pieces:
            for move in enemy_piece.potential_moves:
                enemy_piece.move_piece(self.tiles[piece.potential_moves[move][0]*8+piece.potential_moves[move][1]],
                                self.tiles, pieces, enemy_pieces, self.gameDisplay, True, True)
                
                if (enemy_piece.checkmate(self.tiles, pieces, enemy_pieces, 2, self.gameDisplay) == 2):
                    # We know that the move we have made could lead to checkmate
                    checkmate_score = -1000000
                    return checkmate_score


        # If none of the above are True, just return 0.
        return 0

    # Calculates how much material you obtained.
    # This needs to be modified, since it plays to simplify.
    def gained_material(self, piece, pieces, enemy_pieces, curr_diff):
        move_diff = self.calc_diff(pieces, enemy_pieces)
        # Add in weight:
        weight = 10
        return weight * (move_diff - curr_diff)

    def is_supported(self, piece, pieces, enemy_pieces):
        # Check to see the support for each friendly piece
        # To do this we are giving pieces an attribute that tracks the pieces they support.
        # Create a variable to keep track of the supporting pieces:
        support_pieces = 0
        for support_piece in pieces:
            if piece.current_position in support_piece.supporting:
                support_pieces += 1
        weight = 50
        # We need to ba able to track how the move affects support for all pieces!
        return -weight * support_pieces

    def is_attacked(self, piece, pieces, enemy_pieces):
        # Check to see the attack options of each enemy piece
        attack_pieces = 0
        for piece in pieces:
            for enemy_piece in enemy_pieces:
                if piece.current_position in enemy_piece.potential_moves:
                    attack_pieces += 1
        weight = 50
        return -weight * attack_pieces

    def can_attack(self, piece, pieces, enemy_pieces):
        # Check to see if there are any pieces we can attack.
        can_attack = 0
        for good_piece in pieces:
            for enemy_piece in enemy_pieces:
                if enemy_piece.current_position in good_piece.potential_moves:
                    can_attack += 1
        weight = 10
        return weight * can_attack

    def calc_cen_score(self, pieces, enemy_pieces, copy):
        # Check to see how well our pieces are centered and
        # how well our opponents pieces are centered:

        if not copy:
            pieces = self.pieces
            enemy_pieces = self.enemy_pieces

        center_self = 0
        for piece in pieces:
            curr = piece.current_position
            for pos in curr:
                if pos < 3:
                    center_self += (pos-3)
                if pos > 4:
                    center_self += (4-pos)
        center_enemy = 0
        for piece in enemy_pieces:
            curr = piece.current_position
            for pos in curr:
                if pos < 3:
                    center_enemy += (3-pos)
                if pos > 4:
                    center_enemy += (pos-4)
        return center_self + center_enemy

    def centers_pieces(self, piece, pieces, enemy_pieces):
        # Check to see whether or not we center our pieces
        new_cen_score = self.calc_cen_score(pieces, enemy_pieces, True)
        weight = 20
        return weight * (new_cen_score - self.cen_score)

    def win_exchange(self, piece, pieces, enemy_pieces):
        # Check to see whether or not we win an exchange
        # Play out the move sequence attacking the square we just took and 
        # see if we win more material.
        can_attack = True
        turn_number = 0
        tile_coord = piece.current_position
        while can_attack:
            


    def square_concentration(self, piece, pieces, enemy_pieces):
        # Check to see if we can brute force our way onto a square.
        pass

    def calc_diff(self, pieces, enemy_pieces):
        good_pieces = 0
        for piece in pieces:
            good_pieces += piece.rank
        bad_pieces = 0
        for piece in enemy_pieces:
            bad_pieces += piece.rank
        return good_pieces - bad_pieces

    # Perform evaluations for each potential turn:
    def evaluation(self):
        # Set overall best move:
        best_move_value = -1000000
        # Keep track of the position of the best move
        best_move_pos = None
        # Keep track of the piece with the best move by index
        best_piece_index = None
        # Calculate the current center score for all pieces:
        self.cen_score = self.calc_cen_score(None, None, False)
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
                current_move += self.centers_pieces(piece, copy_pieces, copy_enemy_pieces)
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