# This is where all the player functions and class will be implemented.
import copy
import pygame
import GameBoard

class Player():
    def __init__(self, order, tiles, gameDisplay, player_1_pieces, player_2_pieces):
        # Create a function for every different evaluation performed and 
        # one to iterate through the given potential move.
        self.gameDisplay = gameDisplay
        self.cen_score = 0
        self.material_gain_weight = 10
        self.support_weight = 20
        self.attack_weight = 20
        self.can_attack_weight = 10
        self.center_weight = 20
        self.exchange_weight = 50
        self.opens_moves_weight = 20
        self.defends_king_weight=  20
        self.remove_king_defense_weight = 20

        # Initiate CPU to go first or second.
        self.tiles = tiles
        self.order = order
        self.determine_pieces(copy.deepcopy(player_1_pieces), copy.deepcopy(player_2_pieces))

    # Determines whose pieces are whose:
    def determine_pieces(self, player_1_pieces, player_2_pieces):
        if self.order == 1:
            print("player 1")
            self.pieces = player_1_pieces
            self.enemy_pieces = player_2_pieces
        else:
            print("player 2")
            self.pieces = player_2_pieces
            self.enemy_pieces = player_1_pieces
        for piece in player_1_pieces:
            piece.calculate_moves(self.tiles, player_1_pieces, player_2_pieces, self.gameDisplay)
            piece.induces_check(self.tiles, player_1_pieces, player_2_pieces, self.gameDisplay)
        for piece in player_2_pieces:
            piece.calculate_moves(self.tiles, player_1_pieces, player_2_pieces, self.gameDisplay)
            piece.induces_check(self.tiles, player_1_pieces, player_2_pieces, self.gameDisplay)

    # Destroys member variable pieces after turn is over:
    def destroy_pieces(self):
        while (len(self.pieces) > 0):
            del self.pieces[0]
        while (len(self.enemy_pieces) > 0):
            del self.enemy_pieces[0]

    # Checkmate function:
    def is_checkmate(self, piece, pieces, enemy_pieces):
        # Check to see if we caused checkmate
        if ((self.order == 0 and piece.checkmate(self.tiles, pieces, enemy_pieces, 1, self.gameDisplay) == 1) or
            (self.order == 1 and piece.checkmate(self.tiles, enemy_pieces, pieces, 2, self.gameDisplay) == 2)):
            # We know we have clutched a checkmate, RP +1000000
            return 1000000
        # Check to see if we can be checkmated in the next opponent move:
        for enemy_piece in enemy_pieces:
            for move in enemy_piece.potential_moves:
                enemy_copy = copy.deepcopy(enemy_pieces)
                friendly_copy = copy.deepcopy(pieces)
                if self.order == 0:
                    enemy_piece.move_piece(self.tiles[move[0]*8 + move[1]],
                                    self.tiles, friendly_copy, enemy_copy, self.gameDisplay, True, True)
                else:
                    enemy_piece.move_piece(self.tiles[move[0]*8 + move[1]],
                                    self.tiles, enemy_copy, friendly_copy, self.gameDisplay, True, True)
                # See if opponent move induces checkmate
                if ((self.order == 0 and enemy_piece.checkmate(self.tiles, friendly_copy, enemy_copy, 2, self.gameDisplay) == 2) or
                    (self.order == 1 and enemy_piece.checkmate(self.tiles, enemy_copy, friendly_copy, 1, self.gameDisplay) == 1)):
                    # Now we know that the move we have made could lead to checkmate
                    return -1000000
                # Delete the piece copies we created:
                while (len(enemy_copy) > 0):
                    del enemy_copy[0]
                while (len(friendly_copy) > 0):
                    del friendly_copy[0]
        # If none of the above are True, just return 0.
        return 0

    # Calculates how much material you obtained.
    # This needs to be modified, since it plays to simplify.
    def gained_material(self, piece, pieces, enemy_pieces, curr_diff):
        # Simplifying is good when we are ahead, bad when losing.
        # Move diff is always positive
        move_diff = self.calc_diff(pieces, enemy_pieces)
        # Material difference will define sign of weighted value
        # Weighted value should be smaller than exchange weight
        material_diff = 0
        for friendly_piece in pieces:
            material_diff += friendly_piece.rank
        for enemy_piece in enemy_pieces:
            material_diff -= enemy_piece.rank
        # We also want to attack with a smaller piece if possible
        return self.material_gain_weight * (move_diff - curr_diff) * (material_diff) * (11 - piece.rank)

    def total_support(self, piece, pieces, enemy_pieces):
        # Check to see the support for each friendly piece
        # To do this we are giving pieces an attribute that tracks the pieces they support.
        # Create a variable to keep track of the supporting pieces:
        support_pieces = 0
        for support_piece in pieces:
            for piece in pieces:
                if piece.current_position in support_piece.supporting:
                    support_pieces += 1
        # We need to ba able to track how the move affects support for all pieces!
        return self.support_weight * support_pieces

    def is_attacked(self, piece, pieces, enemy_pieces):
        # Check to see the attack options of each enemy piece
        attacked_pieces = 0
        for piece in pieces:
            for enemy_piece in enemy_pieces:
                if piece.current_position in enemy_piece.potential_moves:
                    attacked_pieces += 1
        return -self.attack_weight * attacked_pieces

    def can_attack(self, piece, pieces, enemy_pieces):
        # Check to see if there are any pieces we can attack.
        can_attack = 0
        for good_piece in pieces:
            for enemy_piece in enemy_pieces:
                if enemy_piece.current_position in good_piece.potential_moves:
                    can_attack += 1
        return self.can_attack_weight * can_attack

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
                if pos <= 3:
                    center_self += pos
                if pos >= 4:
                    center_self += (7 - pos)
        center_enemy = 0
        for piece in enemy_pieces:
            curr = piece.current_position
            for pos in curr:
                if pos <= 3:
                    center_enemy += pos
                if pos >= 4:
                    center_enemy += (7-pos)
        return center_self - center_enemy

    def centers_pieces(self, piece, pieces, enemy_pieces):
        # Check to see whether or not we center our pieces
        new_cen_score = self.calc_cen_score(pieces, enemy_pieces, True)
        return self.center_weight * (new_cen_score - self.cen_score)

    def win_exchange(self, piece, pieces, enemy_pieces, prev_diff):
        # Check to see whether or not we win an exchange
        # Play out the move sequence attacking the square we just took and 
        # see if we win more material.
        # We will be using greedy approximation.
        net_gain = self.calc_diff(pieces, enemy_pieces) - prev_diff
        # Create copies of each pieces side:
        friendly_copy = copy.deepcopy(pieces)
        enemy_copy = copy.deepcopy(enemy_pieces)
        square = piece.current_position
        last_rank = piece.rank
        net_gain_arr = [net_gain]
        # Create the decision loop:
        while True:
            # Find all valid enemy pieces that can attack the square:
            smallest_enemy_piece = None
            for piece in enemy_copy:
                # Calculate valid enemy piece moves
                piece.calculate_moves(self.tiles, friendly_copy, enemy_copy, self.gameDisplay)
                # piece.induces_check(self.tiles, friendly_copy, enemy_copy, self.gameDisplay)   
                if square in piece.potential_moves:
                    if smallest_enemy_piece == None or piece.rank < smallest_enemy_piece.rank:
                        smallest_enemy_piece = piece
            # Attack the square with smallest enemy piece if possible.
            if smallest_enemy_piece != None:
                # Move piece according to whether CPU is black or white:
                if self.order == 0:
                    smallest_enemy_piece.move_piece(self.tiles[square[0]*8+square[1]],
                                self.tiles, friendly_copy, enemy_copy, self.gameDisplay, True, True)
                else:
                    smallest_enemy_piece.move_piece(self.tiles[square[0]*8+square[1]],
                                self.tiles, enemy_copy, friendly_copy, self.gameDisplay, True, True)
                # Update the net_gain
                net_gain -= last_rank
                last_rank = smallest_enemy_piece.rank
                net_gain_arr.append(net_gain)
            else:
                # Enemy can no longer attack and the exchange is over.
                break

            # Find all new valid friendly pieces that can attack the square.
            smallest_friendly_piece = None
            for piece in friendly_copy:
                # Calculate valid friendly piece moves:
                piece.calculate_moves(self.tiles, friendly_copy, enemy_copy, self.gameDisplay)
                # piece.induces_check(self.tiles, friendly_copy, enemy_copy, self.gameDisplay) 
                if square in piece.potential_moves:
                    if smallest_friendly_piece == None or piece.rank < smallest_friendly_piece.rank:
                        smallest_friendly_piece = piece
            if smallest_friendly_piece != None:
                # Move piece according to whether CPU is black or white:
                if self.order == 0:
                    smallest_friendly_piece.move_piece(self.tiles[square[0]*8+square[1]],
                                self.tiles, friendly_copy, enemy_copy, self.gameDisplay, True, True)
                else:
                    smallest_friendly_piece.move_piece(self.tiles[square[0]*8+square[1]],
                                self.tiles, enemy_copy, friendly_copy, self.gameDisplay, True, True)
                # Update the net_gain
                net_gain += last_rank
                last_rank = smallest_friendly_piece.rank
                net_gain_arr.append(net_gain)
            else:
                # Cpu can no longer attack and the game is over.
                break        

        # Delete friendly and enemy copies
        while (len(friendly_copy) > 0):
            del friendly_copy[0]
        while (len(enemy_copy) > 0):
            del enemy_copy[0]

        # Return exchange value as calculated by nash equilibrium and apply weight:
        return nash_equilib(net_gain_arr) * self.exchange_weight

    def opens_friendly_moves(self, pieces, enemy_pieces):
        num_moves = 0
        for piece in pieces:
            piece.calculate_moves(self.tiles, pieces, enemy_pieces, self.gameDisplay)
            # piece.induces_check(self.tiles, pieces, enemy_pieces, self.gameDisplay) 
            num_moves += len(piece.potential_moves)
        return self.opens_moves_weight * num_moves

    def closes_enemy_moves(self, pieces, enemy_pieces):
        num_moves = 0
        for enemy_piece in pieces:
            enemy_piece.calculate_moves(self.tiles, pieces, enemy_pieces, self.gameDisplay)
            # enemy_piece.induces_check(self.tiles, pieces, enemy_pieces, self.gameDisplay)
            num_moves += len(enemy_piece.potential_moves)
        return -self.opens_moves_weight * num_moves

    def defends_king(self, pieces, enemy_pieces):
        king_defenders = 0
        # Obtain king location:
        for friendly_piece in pieces:
            if friendly_piece.name == "King":
                king_loc = friendly_piece.current_position
        for friendly_piece in pieces:
            if (abs(friendly_piece.current_position[0] - king_loc[0]) == 1 and
                abs(friendly_piece.current_position[1] - king_loc[1]) == 1):
                # Piece defends friendly king
                king_defenders += 1
        return king_defenders * self.defends_king_weight

    def remove_king_defense(self, pieces, enemy_pieces):
        king_defenders = 0
        # Obtain king location:
        for enemy_piece in enemy_pieces:
            if enemy_piece.name == "King":
                king_loc = enemy_piece.current_position
        for enemy_piece in pieces:
            if (abs(enemy_piece.current_position[0] - king_loc[0]) == 1 and
                abs(enemy_piece.current_position[1] - king_loc[1]) == 1):
                # Piece defends the enemy king
                king_defenders += 1
        return -king_defenders * self.remove_king_defense_weight

    def calc_diff(self, pieces, enemy_pieces):
        good_pieces = 0
        for piece in pieces:
            good_pieces += piece.rank
        bad_pieces = 0
        for piece in enemy_pieces:
            bad_pieces += piece.rank
        return good_pieces - bad_pieces

    # Perform evaluations for each potential turn:
    def perform_evaluation(self):
        # Set overall best move:
        best_move_value = -1000000
        # Keep track of the position of the best move
        best_move_pos = None
        # Keep track of the piece with the best move by index
        best_piece_index = None
        # Calculate the current center score for all pieces:
        self.cen_score = self.calc_cen_score(None, None, False)
        # Set a current diff measure to calculate diff score:
        current_diff = self.calc_diff(self.pieces, self.enemy_pieces)
        # Iterate through all of the potential moves in CPU pieces:
        # Keep track of the piece index with counter
        counter = 0

        print("good pieces: ", len(self.pieces))
        print("bad pieces: ", len(self.enemy_pieces))

        for piece in self.pieces:
            # print("found a piece")
            for move in piece.potential_moves:
                # print("found a potential move")
                # Reset the pieces after every move calculation:
                copy_pieces = copy.deepcopy(self.pieces)
                copy_enemy_pieces = copy.deepcopy(self.enemy_pieces)

                # Make the move we need to evaluate based on whether or not CPU is player 1 or 2:
                if self.order == 2:
                    piece.move_piece(self.tiles[move[0]*8+move[1]],
                                self.tiles, copy_pieces, copy_enemy_pieces, self.gameDisplay, True, True)
                else:
                    piece.move_piece(self.tiles[move[0]*8+move[1]],
                                self.tiles, copy_enemy_pieces, copy_pieces, self.gameDisplay, True, True)

                # Reset current move evaluation to 0.
                current_move = 0

                # Perform all evaluations here
                current_move += self.is_checkmate(piece, copy_pieces, copy_enemy_pieces)
                current_move += self.gained_material(piece, copy_pieces, copy_enemy_pieces, current_diff)
                current_move += self.total_support(piece, copy_pieces, copy_enemy_pieces)
                current_move += self.is_attacked(piece, copy_pieces, copy_enemy_pieces)
                current_move += self.can_attack(piece, copy_pieces, copy_enemy_pieces)
                current_move += self.centers_pieces(piece, copy_pieces, copy_enemy_pieces)
                current_move += self.win_exchange(piece, copy_pieces, copy_enemy_pieces, current_diff)
                current_move += self.opens_friendly_moves(copy_pieces, copy_enemy_pieces)
                current_move += self.closes_enemy_moves(copy_pieces, copy_enemy_pieces)

                # Check to see if the evaluation is the best move:
                if current_move > best_move_value:
                    # If it is, then update our best move
                    best_move_pos = move
                    best_piece_index = counter
                    best_move_value = current_move

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

def nash_equilib(arr):
    exchange = arr[0]
    for i in range(len(arr)):
        if (i + 2 >= len(arr)):
            if (i % 2 == 0):
                if (arr[-1] > exchange):
                    exchange = arr[-1]
                    break
            else:
                if (arr[-1] < exchange):
                    exchange = arr[-1]
                    break
        elif (i % 2 == 0 and arr[i+2] >= arr[i]):
            exchange = arr[i]
            break
        elif (i % 2 and arr[i+2] <= arr[i]):
            exchange = arr[i]
            break
    return exchange

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
            - Piece objects hold a supporting array which lists the tiles they attack/defend
        - Return the highest evaluated move as the move to make.
        - Delete the copies of pieces that we made.

"""