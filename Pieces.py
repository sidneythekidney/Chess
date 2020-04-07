# This is where all of the piece functions will go.

import pygame
import GameBoard
import Player
import copy
import time

white = (255,255,255)


class Piece:
    def __init__(self, name, starting_position, image, player):
        self.name = name
        self.starting_position = starting_position
        self.player = player
        self.current_position = starting_position
        self.potential_moves = []
        self.supporting = []
        if name == "Pawn":
            self.rank = 1
        if name == "Bishop" or name == "Knight":
            self.rank = 3
        if name == "Rook":
            if starting_position[1] == 0:
                self.sub_name = "KS"
            else:
                self.sub_name = "QS"
            self.rank = 5
        if name == "Queen":
            self.rank = 9
        if name == "King":
            self.castle_QS = True
            self.castle_KS = True
            self.rank = 10
        self.image = image
        for i in range(len(image)):
            if (image[i] == "_"):
                end = i
                self.color = image[0:end]
                break


    def display_piece_to_screen(self, tiles, gameDisplay):
        # Takes in an array of tiles
        for tile in tiles:
            if(tile.coordinate == self.current_position):
                #display the image to the screen

                #Need to change self.image to be a surface rather than a string
                image_to_draw = pygame.image.load(self.image)
                image_rect = image_to_draw.get_rect()
                image_rect.center = (tile.x_position + tile.height/2, tile.y_position + tile.height/2)
                gameDisplay.blit(image_to_draw, image_rect)

    def get_piece_on_tile(self,coordinate, player_1_pieces, player_2_pieces):
        for piece in player_1_pieces:
            if piece.current_position == coordinate:
                return piece
        for piece in player_2_pieces:
            if piece.current_position == coordinate:
                return piece
        return None

    def crop_potential_moves(self, tiles, player_1_pieces, player_2_pieces):
        final_moves = []
        for move in self.potential_moves:
            if(move[0] >= 0 and move[0] < 8 and move[1] >= 0 and move[1] < 8):
                final_moves.append(move)
        #Create two deep copies for each of the player pieces
        #copy_1 = copy.deepcopy(player_1_pieces)
        #copy_2 = copy.deepcopy(player_2_pieces)
        self.potential_moves = final_moves
        return final_moves

    def induces_check(self, tiles, player_1_pieces, player_2_pieces, gameDisplay):
        #Change this so we are working with copies
        copy_1 = copy.deepcopy(player_1_pieces)
        copy_2 = copy.deepcopy(player_2_pieces)
        for piece in copy_1:
            if piece.current_position == self.current_position:
                copy_self = piece
                break
        for piece in copy_2:
            if piece.current_position == self.current_position:
                copy_self = piece
                break
        # induces check calls itself in a recursive loop
        # Could be a potential bug in this loop:
        final_moves = copy_self.potential_moves
        delete_list = []
        for i in range(len(copy_self.potential_moves)):
            #print(str(self.potential_moves[i][0])+", "+str(self.potential_moves[i][1]))
            copy_self.move_piece(tiles[copy_self.potential_moves[i][0]*8+copy_self.potential_moves[i][1]],
                       tiles, copy_1, copy_2, gameDisplay, False, False)
            if copy_self.player == 1:
                if(copy_self.check(tiles, copy_1, copy_2, 2, gameDisplay)):
                    delete_list.append(i)
            if copy_self.player == 2:
                if(self.check(tiles, copy_1, copy_2, 1, gameDisplay)):
                    delete_list.append(i)
        counter = 0
        for i in range(len(delete_list)):
            del final_moves[delete_list[i]-counter]
            counter = counter + 1
        self.potential_moves = final_moves
        return self.potential_moves

    def empty_square(self, tile, player_1_pieces, player_2_pieces, i, max_i):
        name = self.name
        if name == "Queen" or name == "Bishop" or name == "Rook":
            for piece in player_1_pieces:
                if piece.current_position == tile and piece.player == self.player:
                    self.supporting.append(tile)
                    return max_i
                if piece.current_position == tile and piece.player != self.player:
                    return max_i-1
                    
            for piece in player_2_pieces:
                if piece.current_position == tile and piece.player == self.player:
                    self.supporting.append(tile)
                    return max_i
                if piece.current_position == tile and piece.player != self.player:
                    return max_i-1
            # If we get here just return the previous i
            return i
        if name == "King" or name == "Knight":
            for piece in player_1_pieces:
                if piece.current_position == tile and piece.player == self.player:
                    self.supporting.append(tile)
                    return False
            for piece in player_2_pieces:
                if piece.current_position == tile and piece.player == self.player:
                    self.supporting.append(tile)
                    return False
            return True

    def check(self,tiles, player_1_pieces, player_2_pieces, player, gameDisplay):
        #Get the position of the two kings on the gameboard:
        for piece in player_1_pieces:
            if piece.name == "King":
                king_1_pos = piece.current_position
        for piece in player_2_pieces:
            if piece.name == "King":
                king_2_pos = piece.current_position

        #Iterate through all of the pieces moves to see if the king is in check.
        if player == 1:
            for piece in player_1_pieces:
                if king_2_pos in piece.calculate_moves(tiles, player_1_pieces, player_2_pieces, gameDisplay):
                    return True
        if player == 2:
            for piece in player_2_pieces:
                if king_1_pos in piece.calculate_moves(tiles, player_1_pieces, player_2_pieces, gameDisplay):
                    return True
        return False

    def checkmate(self, tiles, player_1_pieces, player_2_pieces, player, gameDisplay):
        #A king is in checkmate if it does not have any moves that will move it safety
        # and no other pieces can block the piece or pieces inducing check.

        #Another way of thinking... If i calculate potential moves for every move i can make and my
        #king is still in danger, checkmate applies.
        #Player is the game player that induced check:
        copy_1 = copy.deepcopy(player_1_pieces)
        copy_2 = copy.deepcopy(player_2_pieces)
        if player == 1:
           for piece in copy_2:
               piece.calculate_moves(tiles, copy_1, copy_2, gameDisplay)
               original_position = piece.current_position
               for move in range(len(piece.potential_moves)):
                   piece.move_piece(tiles[piece.potential_moves[move][0]*8+piece.potential_moves[move][1]],
                                    tiles,copy_1, copy_2, gameDisplay, False, False)
                   if(not self.check(tiles, copy_1, copy_2, 1, gameDisplay)):
                    #    print(piece.name)
                    #    print(piece.current_position)
                    #    print("not checkmate")
                        return None
                   piece.current_position = original_position
                   del copy_1
                   copy_1 = copy.deepcopy(player_1_pieces)
                   
        if player == 2:
           for piece in copy_1:
               piece.calculate_moves(tiles, copy_1, copy_2, gameDisplay)
               original_position = piece.current_position
               for move in range(len(piece.potential_moves)):
                   piece.move_piece(tiles[piece.potential_moves[move][0]*8+piece.potential_moves[move][1]],
                                    tiles,copy_1, copy_2, gameDisplay, False, False)
                   if(not self.check(tiles, copy_1, copy_2, 2, gameDisplay)):
                    #    print(piece.name)
                    #    print(piece.current_position)
                        print("not checkmate")
                        return None
                   piece.current_position = original_position
                   del copy_2
                   copy_2 = copy.deepcopy(player_2_pieces)
        print("checkmate")
        return player

    def stalemate(self, tiles, player_1_pieces, player_2_pieces, gameDisplay):
        copy_1 = copy.deepcopy(player_1_pieces)
        copy_2 = copy.deepcopy(player_2_pieces)

        counter = 0

        if self.player == 1:
            for piece in copy_2:
                piece.calculate_moves(tiles, copy_1, copy_2, gameDisplay)
                counter += len(piece.potential_moves)
        if self.player == 2:
            for piece in copy_1:
                piece.calculate_moves(tiles, copy_1, copy_2, gameDisplay)
                counter += len(piece.potential_moves)
        if counter == 0:
            print("stalemate")
                          
    def calculate_moves(self, tiles, player_1_pieces, player_2_pieces, gameDisplay):
        potential_moves = []
        cur = self.current_position
        if self.name == "Pawn":
            if self.player == 1:
                if cur == self.starting_position:
                    if self.get_piece_on_tile(adder(cur,[1,0]), player_1_pieces, player_2_pieces) == None:
                        potential_moves.append(adder(cur,[1,0]))
                    if self.get_piece_on_tile(adder(cur,[2,0]), player_1_pieces, player_2_pieces) == None:
                        potential_moves.append(adder(cur,[2,0]))
                else:
                    if self.get_piece_on_tile(adder(cur,[1,0]), player_1_pieces, player_2_pieces) == None:
                        potential_moves.append(adder(cur,[1,0]))
                            
                #Check for possible en passants:
                    right_piece = self.get_piece_on_tile(adder(cur, [0,1]), player_1_pieces, player_2_pieces)
                    if right_piece != None:
                        print(str(right_piece.name) +" " +  str(right_piece.player))
                        if((right_piece.player == 2) and (right_piece.name == "Pawn") and self.player == 1):
                            print("en_passant" + str(right_piece.en_passant) + " " + str(right_piece.current_position))
                            if right_piece.en_passant == True:
                                # Bug: Piece is not being declared 
                                potential_moves.append(adder(cur,[1,1]))                             
                    left_piece = self.get_piece_on_tile(adder(cur, [0,-1]), player_1_pieces, player_2_pieces)
                    if left_piece != None:
                        if((left_piece.player == 2) and (left_piece.name == "Pawn") and self.player == 1):
                            if left_piece.en_passant == True:
                                potential_moves.append(adder(cur,[1,-1]))   
                if self.get_piece_on_tile(adder(cur, [1,1]), player_1_pieces, player_2_pieces) != None:
                    if(self.get_piece_on_tile(adder(cur, [1,1]), player_1_pieces, player_2_pieces).player == 2):
                        potential_moves.append(adder(cur,[1,1]))
                    else:
                        self.supporting.append(adder(cur,[1,1]))
                if self.get_piece_on_tile(adder(cur, [1,-1]), player_1_pieces, player_2_pieces) != None:
                    if(self.get_piece_on_tile(adder(cur, [1,-1]), player_1_pieces, player_2_pieces).player == 2):
                        potential_moves.append(adder(cur,[1,-1]))
                    else:
                        self.supporting.append(adder(cur,[1,-1]))                       
                    
            if self.player == 2:
                if cur == self.starting_position:
                    if self.get_piece_on_tile(adder(cur,[-1,0]), player_1_pieces, player_2_pieces) == None:
                        potential_moves.append(adder(cur,[-1,0]))
                    if self.get_piece_on_tile(adder(cur,[-2,0]), player_1_pieces, player_2_pieces) == None:
                        potential_moves.append(adder(cur,[-2,0]))
                else:
                    if self.get_piece_on_tile(adder(cur,[-1,0]), player_1_pieces, player_2_pieces) == None:
                        potential_moves.append(adder(cur,[-1,0]))

                #Check for possible en passants:
                    right_piece = self.get_piece_on_tile(adder(cur, [0,-1]), player_1_pieces, player_2_pieces)
                    if right_piece != None:
                        if((right_piece.player == 1) and (right_piece.name == "Pawn")):
                            if right_piece.en_passant == True:
                                potential_moves.append(adder(cur,[-1,-1]))
                                
                    left_piece = self.get_piece_on_tile(adder(cur, [0,1]), player_1_pieces, player_2_pieces)
                    if left_piece != None:
                        if((left_piece.player == 1) and (left_piece.name == "Pawn")):
                            if left_piece.en_passant == True:
                                potential_moves.append(adder(cur,[-1,1]))
                if self.get_piece_on_tile(adder(cur, [-1,1]), player_1_pieces, player_2_pieces) != None:
                    if(self.get_piece_on_tile(adder(cur, [-1,1]), player_1_pieces, player_2_pieces).player == 1):
                        potential_moves.append(adder(cur,[-1,1]))
                    else:
                        self.supporting.append(adder(cur,[-1,1]))
                if self.get_piece_on_tile(adder(cur, [-1,-1]), player_1_pieces, player_2_pieces) != None:
                    if(self.get_piece_on_tile(adder(cur, [-1,-1]), player_1_pieces, player_2_pieces).player == 1):
                        potential_moves.append(adder(cur,[-1,-1]))
                    else:
                        self.supporting.append(adder(cur,[-1,-1]))
                
        if self.name == "Knight":
                moves_to_check = [adder(cur,[1,-2]),adder(cur,[2,-1]),adder(cur,[2,1]),
                                  adder(cur,[1,2]),adder(cur,[-1,2]),adder(cur,[-2,1]),
                                  adder(cur,[-2,-1]),adder(cur,[-1,-2])]
                for move in moves_to_check:
                    if(move[1] <= (move[1] + 2) and (move[1] >= (move[1] - 2))):
                        if (self.empty_square(move, player_1_pieces, player_2_pieces, 0, 0)):
                            potential_moves.append(move)

        if self.name == "Bishop":
            for i in range(cur[1]):
                opensquares = self.empty_square(adder(cur,[-(i+1),-(i+1)]), player_1_pieces, player_2_pieces, i, cur[1])
                if(opensquares == cur[1]):
                    break
                if(opensquares == cur[1]-1):
                    potential_moves.append(adder(cur,[-(i+1),-(i+1)]))
                    break
                potential_moves.append(adder(cur,[-(i+1),-(i+1)]))
            for i in range(cur[1]):
                opensquares = self.empty_square(adder(cur,[(i+1),-(i+1)]), player_1_pieces, player_2_pieces, i, cur[1])
                if(opensquares == cur[1]):
                    break
                if(opensquares == cur[1]-1):
                    potential_moves.append(adder(cur,[(i+1),-(i+1)]))
                    break
                potential_moves.append(adder(cur,[(i+1),-(i+1)]))
            for i in range(7-cur[1]):
                opensquares = self.empty_square(adder(cur,[(i+1),(i+1)]), player_1_pieces, player_2_pieces, i, 7-cur[1])
                if(opensquares == 7-cur[1]):
                    break
                if(opensquares == 7-cur[1]-1):
                    potential_moves.append(adder(cur,[(i+1),(i+1)]))
                    break
                potential_moves.append(adder(cur,[(i+1),(i+1)]))
            for i in range(7-cur[1]):
                opensquares = self.empty_square(adder(cur,[-(i+1),(i+1)]), player_1_pieces, player_2_pieces, i, 7-cur[1])
                if(opensquares == 7-cur[1]):
                    break
                if(opensquares == 7-cur[1]-1):
                    potential_moves.append(adder(cur,[-(i+1),(i+1)]))
                    break
                potential_moves.append(adder(cur,[-(i+1),(i+1)]))

        if self.name == "Rook":
            for i in range(cur[1]):
                opensquares = self.empty_square(adder(cur,[0,-(i+1)]), player_1_pieces, player_2_pieces, i, cur[1])
                if(opensquares == cur[1]-1):
                    potential_moves.append(adder(cur,[0,-(i+1)]))
                    break
                if(opensquares == cur[1]):
                    break
                potential_moves.append(adder(cur,[0,-(i+1)]))
            for i in range(7 - cur[1]):
                opensquares = self.empty_square(adder(cur,[0,(i+1)]), player_1_pieces, player_2_pieces, i, 7 - cur[1])
                if(opensquares == 7 - cur[1]):
                    break
                if(opensquares == 7-cur[1]-1):
                    potential_moves.append(adder(cur,[0,(i+1)]))
                    break
                potential_moves.append(adder(cur,[0,(i+1)]))
            for i in range(cur[0]):
                opensquares = self.empty_square(adder(cur,[-(i+1),0]), player_1_pieces, player_2_pieces, i, cur[0])
                if(opensquares == cur[0]):
                    break
                if(opensquares == cur[0]-1):
                    potential_moves.append(adder(cur,[-(i+1),0]))
                    break
                potential_moves.append(adder(cur,[-(i+1),0]))
            for i in range(7 - cur[0]):
                opensquares = self.empty_square(adder(cur,[(i+1),0]), player_1_pieces, player_2_pieces, i, 7 - cur[0])
                if(opensquares == 7 - cur[0]):
                    break
                if(opensquares == 7-cur[0]-1):
                    potential_moves.append(adder(cur,[(i+1),0]))
                    break
                potential_moves.append(adder(cur,[(i+1),0]))

        if self.name == "Queen":
            for i in range(cur[1]):
                opensquares = self.empty_square(adder(cur,[-(i+1),-(i+1)]), player_1_pieces, player_2_pieces, i, cur[1])
                if(opensquares == cur[1]):
                    break
                if(opensquares == cur[1]-1):
                    potential_moves.append(adder(cur,[-(i+1),-(i+1)]))
                    break
                potential_moves.append(adder(cur,[-(i+1),-(i+1)]))
            for i in range(cur[1]):
                opensquares = self.empty_square(adder(cur,[(i+1),-(i+1)]), player_1_pieces, player_2_pieces, i, cur[1])
                if(opensquares == cur[1]):
                    break
                if(opensquares == cur[1]-1):
                    potential_moves.append(adder(cur,[(i+1),-(i+1)]))
                    break
                potential_moves.append(adder(cur,[(i+1),-(i+1)]))
            for i in range(7-cur[1]):
                opensquares = self.empty_square(adder(cur,[(i+1),(i+1)]), player_1_pieces, player_2_pieces, i, 7-cur[1])
                if(opensquares == 7-cur[1]):
                    break
                if(opensquares == 7-cur[1]-1):
                    potential_moves.append(adder(cur,[(i+1),(i+1)]))
                    break
                potential_moves.append(adder(cur,[(i+1),(i+1)]))
            for i in range(7-cur[1]):
                opensquares = self.empty_square(adder(cur,[-(i+1),(i+1)]), player_1_pieces, player_2_pieces, i, 7-cur[1])
                if(opensquares == 7-cur[1]):
                    break
                if(opensquares == 7-cur[1]-1):
                    potential_moves.append(adder(cur,[-(i+1),(i+1)]))
                    break
                potential_moves.append(adder(cur,[-(i+1),(i+1)]))


            for i in range(cur[1]):
                opensquares = self.empty_square(adder(cur,[0,-(i+1)]), player_1_pieces, player_2_pieces, i, cur[1])
                if(opensquares == cur[1]-1):
                    potential_moves.append(adder(cur,[0,-(i+1)]))
                    break
                if(opensquares == cur[1]):
                    break
                potential_moves.append(adder(cur,[0,-(i+1)]))
            for i in range(7 - cur[1]):
                opensquares = self.empty_square(adder(cur,[0,(i+1)]), player_1_pieces, player_2_pieces, i, 7 - cur[1])
                if(opensquares == 7 - cur[1]):
                    break
                if(opensquares == 7-cur[1]-1):
                    potential_moves.append(adder(cur,[0,(i+1)]))
                    break
                potential_moves.append(adder(cur,[0,(i+1)]))
            for i in range(cur[0]):
                opensquares = self.empty_square(adder(cur,[-(i+1),0]), player_1_pieces, player_2_pieces, i, cur[0])
                if(opensquares == cur[0]):
                    break
                if(opensquares == cur[0]-1):
                    potential_moves.append(adder(cur,[-(i+1),0]))
                    break
                potential_moves.append(adder(cur,[-(i+1),0]))
            for i in range(7 - cur[0]):
                opensquares = self.empty_square(adder(cur,[(i+1),0]), player_1_pieces, player_2_pieces, i, 7 - cur[0])
                if(opensquares == 7 - cur[0]):
                    break
                if(opensquares == 7-cur[0]-1):
                    potential_moves.append(adder(cur,[(i+1),0]))
                    break
                potential_moves.append(adder(cur,[(i+1),0]))

                
        if self.name == "King":
            if self.empty_square(adder(cur,[1,0]), player_1_pieces, player_2_pieces, 0, 0):
                potential_moves.append(adder(cur,[1,0]))
            if self.empty_square(adder(cur,[-1,0]), player_1_pieces, player_2_pieces, 0, 0):
                potential_moves.append(adder(cur,[-1,0]))
            if(cur[1] != 7):
                if self.empty_square(adder(cur,[0,1]), player_1_pieces, player_2_pieces, 0, 0):
                    potential_moves.append(adder(cur,[0,1]))
                if self.empty_square(adder(cur,[1,1]), player_1_pieces, player_2_pieces, 0, 0):
                    potential_moves.append(adder(cur,[1,1]))
                if self.empty_square(adder(cur,[-1,1]), player_1_pieces, player_2_pieces, 0, 0):
                    potential_moves.append(adder(cur,[-1,1]))
            if(cur[1] != 0):
                if self.empty_square(adder(cur,[0,-1]), player_1_pieces, player_2_pieces, 0, 0):
                    potential_moves.append(adder(cur,[0,-1]))
                if self.empty_square(adder(cur,[-1,-1]), player_1_pieces, player_2_pieces, 0, 0):
                    potential_moves.append(adder(cur,[-1,-1]))
                if self.empty_square(adder(cur,[1,-1]), player_1_pieces, player_2_pieces, 0, 0):
                    potential_moves.append(adder(cur,[1,-1]))
            # Check to see if king can be allowed to castle.

            # if self.starting_position == self.current_position:
            #     king_side, queen_side = self.induces_check_castle(tiles, player_1_pieces, player_2_pieces, gameDisplay)

            if (self.castle_QS == True and
                self.empty_square(adder(cur,[0,1]), player_1_pieces, player_2_pieces, 0, 0) and
                self.empty_square(adder(cur,[0,2]), player_1_pieces, player_2_pieces, 0, 0) and
                self.empty_square(adder(cur,[0,3]), player_1_pieces, player_2_pieces, 0, 0) and
                not self.get_piece_on_tile(adder(cur, [0, 4]), player_1_pieces, player_2_pieces) == None and
                self.get_piece_on_tile(adder(cur, [0, 4]), player_1_pieces, player_2_pieces).name == "Rook" and
                self.get_piece_on_tile(adder(cur, [0, 4]), player_1_pieces, player_2_pieces).player == self.player):
 
                potential_moves.append(adder(cur, [0, 2]))
                
            if (self.castle_KS == True and
                self.empty_square(adder(cur,[0,-1]), player_1_pieces, player_2_pieces, 0, 0) and
                self.empty_square(adder(cur,[0,-2]), player_1_pieces, player_2_pieces, 0, 0) and
                not self.get_piece_on_tile(adder(cur, [0, -3]), player_1_pieces, player_2_pieces) == None and
                self.get_piece_on_tile(adder(cur, [0, -3]), player_1_pieces, player_2_pieces).name == "Rook" and
                self.get_piece_on_tile(adder(cur, [0, -3]), player_1_pieces, player_2_pieces).player == self.player):
                potential_moves.append(adder(cur, [0, -2]))
                 

        #This calls check which in turn calls calculate_moves so we have a recursive infinite loop
        self.potential_moves = potential_moves
        potential_moves = self.crop_potential_moves(tiles, player_1_pieces, player_2_pieces)
        return self.potential_moves


    def move_piece(self, tile, tiles, player_1_pieces, player_2_pieces, gameDisplay, promote, en_passant):
        painted_tile = None
        delete_coord = None

        if self.name == "King":
            
            self.castle_QS = False
            self.castle_KS = False

            if(tile.coordinate[1]-self.current_position[1] < -1):
                #Kingside castle
                piece = self.get_piece_on_tile([tile.coordinate[0], tile.coordinate[1]-1],
                                        player_1_pieces, player_2_pieces)
                if piece != None:
                    self.get_piece_on_tile([tile.coordinate[0], tile.coordinate[1]-1],
                                        player_1_pieces, player_2_pieces).current_position = [tile.coordinate[0], tile.coordinate[1]+1]
                    #GameBoard.paint_corner([tile.coordinate[0],0])
                    painted_tile = [tile.coordinate[0],0]
                    
            if(self.current_position[1] - tile.coordinate[1] < -1):
                #Queenside castle
                piece = self.get_piece_on_tile([tile.coordinate[0], tile.coordinate[1]+2],
                                        player_1_pieces, player_2_pieces)
                if piece != None:
                    self.get_piece_on_tile([tile.coordinate[0], tile.coordinate[1]+2],
                                        player_1_pieces, player_2_pieces).current_position = [tile.coordinate[0], tile.coordinate[1]-1]
                    #GameBoard.paint_corner([tile.coordinate[0],7])
                    painted_tile = [tile.coordinate[0],7]        
        if self.name == "Pawn":
            if ((self.current_position[0] == 6 and self.player == 1)
                                     or (self.current_position[0] == 1 and self.player == 2)):
                painted_tile = self.promote_pawn(tile, tiles, player_1_pieces, player_2_pieces, gameDisplay, promote)
            # Allow the pawn to be en passanted:
            # If the pawn gets moved up two spaces it can be immediately en-passanted
            if(self.current_position[0] == 1 and self.player == 1 and tile.coordinate[0] == 3):
                self.en_passant = True
            if(self.current_position[0] == 6 and self.player == 2 and tile.coordinate[0] == 4):
                self.en_passant = True
            #Capture the piece on the correct tile when en passant occurs
            if(tile.coordinate[0] != self.current_position[0] and 
                tile.coordinate[1] != self.current_position[1] and 
                self.get_piece_on_tile([tile.coordinate[0],tile.coordinate[1]], player_1_pieces, player_2_pieces) == None):
                if self.player == 1:
                    delete_coord = [tile.coordinate[0]-1, tile.coordinate[1]]
                else:
                    delete_coord = [tile.coordinate[0]+1, tile.coordinate[1]]

        if self.name == "Rook":
            if self.sub_name == "QS":
                for i in range(len(player_1_pieces)):
                    if (player_1_pieces[i].name == "King" and
                        player_1_pieces[i].player == self.player):
                        player_1_pieces[i].castle_QS = False
                        break
                for i in range(len(player_2_pieces)):
                    if (player_2_pieces[i].name == "King" and
                        player_2_pieces[i].player == self.player):
                        player_2_pieces[i].castle_QS = False
                        break
            if self.sub_name == "KS":
                for i in range(len(player_1_pieces)):
                    if (player_1_pieces[i].name == "King" and
                        player_1_pieces[i].player == self.player):
                        player_1_pieces[i].castle_KS = False
                        break
                for i in range(len(player_2_pieces)):
                    if (player_2_pieces[i].name == "King" and
                        player_2_pieces[i].player == self.player):
                        player_2_pieces[i].castle_KS = False
                        break
        for i in range(len(player_1_pieces)):
            if player_1_pieces[i].current_position == tile.coordinate or player_1_pieces[i].current_position == delete_coord:
                print(player_1_pieces[i].current_position)
                del player_1_pieces[i]
                if delete_coord != None:
                    painted_tile = delete_coord
                break
        for i in range(len(player_2_pieces)):
            if player_2_pieces[i].current_position == tile.coordinate or player_2_pieces[i].current_position == delete_coord:
                del player_2_pieces[i]
                if delete_coord != None:
                    painted_tile = delete_coord
                break

        # Piece still staying around when it gets deleted.

        self.current_position = tile.coordinate
        
        if self.player == 1:
            for piece in player_1_pieces:
                if piece.name == "Pawn" and (piece.current_position != tile.coordinate or piece.current_position[0] != 3):
                    piece.en_passant = False
        if self.player == 2:
            for piece in player_2_pieces:
                if piece.name == "Pawn" and (piece.current_position != tile.coordinate or piece.current_position[0] != 4):
                    piece.en_passant = False
        # if en_passant:
        #     for piece in player_1_pieces:
        #         if piece.name == "Pawn":
        #             print(str(piece.player) + " " + str(piece.current_position) + str(piece.en_passant))
        #     for piece in player_2_pieces:
        #         if piece.name == "Pawn":
        #             print(str(piece.player) + " " + str(piece.current_position) + str(piece.en_passant))
        # pygame.display.update()
        # self.check(player_1_pieces, player_2_pieces)
        # print(painted_tile)
        return painted_tile


    def promote_pawn(self, tile, tiles, player_1_pieces, player_2_pieces, gameDisplay, possible):
        #Display piece options on screen to right of gameboard:
        #piece options include bishop, knight, rook and queen
        #We just need to change the image and name of the piece
        # print("promoting pawn")
        print(len(player_1_pieces))
        painted_tile = self.current_position
        if possible:
            piece_list = ["Queen", "Rook", "Bishop", "Knight"]
            font = pygame.font.Font('freesansbold.ttf', 18)

            title = "Select a piece to upgrade pawn"
            
            selected = False

            while not selected:
                # print(str(self.current_position[0]) + " "+ str(self.current_position[1]))
                # pygame.draw.rect(gameDisplay, (229, 250, 5),
                # (self.current_position[1]*75, (7-self.current_position[0])*75, 75, 75))
                for i in range(2):
                    pygame.draw.rect(gameDisplay, white, (650+125*i,100,75,75))
                    display_text(gameDisplay, piece_list[i], (69, 241, 247),(650+125*i+37,190))
                    image_name = self.color + "_" + piece_list[i] + ".png"
                    display_image(gameDisplay, image_name, (657+125*i, 108))

                for i in range(2):
                    pygame.draw.rect(gameDisplay, white,(650+125*i,250,75,75))
                    display_text(gameDisplay, piece_list[i+2], (69, 241, 247),(650+125*i+37,340))
                    image_name = self.color + "_" + piece_list[i+2] + ".png"
                    display_image(gameDisplay, image_name, (657+125*i, 258))

                for piece in player_1_pieces:
                    piece.display_piece_to_screen(tiles, gameDisplay)
                for piece in player_2_pieces:
                    piece.display_piece_to_screen(tiles, gameDisplay)

                pygame.display.update()

                for event in pygame.event.get():
                    display_text(gameDisplay, title, (69, 241, 247), (750,25))
                    #Highlight the squares if the user hovers over them:
                    if event.pos != None:
                        if event.pos[0] > 650 and event.pos[0] < 725:
                            if event.pos[1] > 100 and event.pos[1] < 175:
                                pygame.draw.rect(gameDisplay, (36, 201, 39) ,(650,100,75,75))
                                display_image(gameDisplay, self.color+"_Queen.png", (657, 108))
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    selected = True
                                    selected_piece = "Queen"

                        if event.pos[0] > 775 and event.pos[0] < 850:
                            if event.pos[1] > 100 and event.pos[1] < 175:
                                pygame.draw.rect(gameDisplay, (36, 201, 39) ,(650+125,100,75,75))
                                display_image(gameDisplay, self.color+"_Rook.png", (657+125, 108))
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    selected = True
                                    selected_piece = "Rook"

                        if event.pos[0] > 650 and event.pos[0] < 725:
                            if event.pos[1] > 250 and event.pos[1] < 325:
                                pygame.draw.rect(gameDisplay, (36, 201, 39) ,(650,250,75,75))
                                display_image(gameDisplay, self.color+"_Bishop.png", (657, 258))
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    selected = True
                                    selected_piece = "Bishop"

                        if event.pos[0] > 775 and event.pos[0] < 850:
                            if event.pos[1] > 250 and event.pos[1] < 325:
                                pygame.draw.rect(gameDisplay, (36, 201, 39) ,(650+125,250,75,75))
                                display_image(gameDisplay, self.color+"_Knight.png", (657+125, 258))
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    selected = True
                                    selected_piece = "Knight"
            self.name = selected_piece
            # if selected_piece == "Rook":
                # self.sub_name = "promoted"
            # print(len(player_1_pieces))
            self.image = self.color + "_" + selected_piece + ".png"
            pygame.draw.rect(gameDisplay, (122,122,122),(600,0,300,600))
            for piece in player_1_pieces:
                piece.display_piece_to_screen(tiles, gameDisplay)
            for piece in player_2_pieces:
                piece.display_piece_to_screen(tiles, gameDisplay)
            pygame.display.update()
            return painted_tile
            
# Helper function for adding two arrays:
def adder(array1, array2):
    return_array = []
    for i in range(min(len(array1), len(array2))):
        return_array.append(array1[i] + array2[i])
    return return_array

def display_text(gameDisplay, text, color, center_pos):
    font = pygame.font.Font('freesansbold.ttf', 18)
    text = font.render(text, True, color)
    textRect = text.get_rect()
    textRect.center = center_pos
    gameDisplay.blit(text, textRect)

def display_image(gameDisplay, image_name, pos):
    figure = pygame.image.load(image_name)
    gameDisplay.blit(figure, pos)