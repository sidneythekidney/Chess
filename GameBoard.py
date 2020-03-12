# This is where all of the game board functions will go.
import pygame
import GameBoard
import Player
import Pieces
import time

blue = (0,30,255)

class Tile:
    def __init__(self, x_position, y_position, height, coordinate, color):
        self.x_position = x_position
        self.y_position = y_position
        self.height = height
        self.coordinate = coordinate
        self.color = color
        self.highlighted = False
        self.possible_move = False

class GameBoard:
    def __init__(self, color1, color2, display_width, display_height):
        self.display_width = display_width
        self.display_height = display_height
        self.color1 = color1
        self.color2 = color2
        self.tiles = []
        self.already_highlighted = False
        self.selected_tile = None
        pygame.init()
        self.gameDisplay = pygame.display.set_mode((self.display_width, self.display_height))
        self.winning_player = None
    
    def paint_corner(self, position):
        tile = self.tiles[position[0]*8+position[1]]
        if ((position[0]+position[1])%2 == 1):
            pygame.draw.rect(self.gameDisplay, self.color1, (tile.x_position,tile.y_position,
                                                             tile.height, tile.height))
        else:
            pygame.draw.rect(self.gameDisplay, self.color2, (tile.x_position,tile.y_position,
                                                             tile.height, tile.height))
        pygame.display.update()

    def make_game_board(self):
        pygame.display.set_caption("Chess")
        self.create_tiles()
        self.create_pieces()
        gray = (122, 122, 122)
        self.gameDisplay.fill(gray,
                              (self.display_height, 0,
                               self.display_width-self.display_height,
                               self.display_height))

    def create_tiles(self):
        # Create 64 different buttons to represent each tile:
        height = self.display_height/8
        x_val = 0
        y_val = 7 * height
        row = 0
        
        for i in range(64):
            #Start with color 2
            color = self.color1
            if(row % 2 == 0):
                if(i % 2 == 0):
                    pygame.draw.rect(self.gameDisplay, self.color2, (x_val, y_val, height, height))
                    color = self.color2
                if(i % 2 == 1):
                    pygame.draw.rect(self.gameDisplay, self.color1, (x_val, y_val, height, height))

            if(row % 2 == 1):
                if(i % 2 == 1):
                    pygame.draw.rect(self.gameDisplay, self.color2, (x_val, y_val, height, height))
                    color = self.color2
                if(i % 2 == 0):
                    pygame.draw.rect(self.gameDisplay, self.color1, (x_val, y_val, height, height))
            self.tiles.append(Tile(x_val, y_val, height, [i//8, i%8], color))
            x_val = x_val + height
            if(x_val == self.display_height):
                x_val = 0
                y_val = y_val - height
                row = row + 1


    def create_pieces(self):
        self.player_1_pieces = []
        self.player_2_pieces = []

        #Loop through creating all the pieces:
        for i in range(16):
            #Create pawns:
            if(i < 8):
                player_1_piece = Pieces.Piece("Pawn", [1,i], "White_Pawn.png", 1)
                player_1_piece.en_passant = False
                player_2_piece = Pieces.Piece("Pawn", [6,i], "Black_Pawn.png", 2)
                player_2_piece.en_passant = False
            #Create the rooks
            elif(i >= 8 and i < 10):
                player_1_piece = Pieces.Piece("Rook", [0,(i-8)*7], "White_Rook.png", 1)
                player_2_piece = Pieces.Piece("Rook", [7,(i-8)*7], "Black_Rook.png", 2)

            #Create the knights:
            elif(i >= 10 and i < 12):
                player_1_piece = Pieces.Piece("Knight", [0,(i-10)*5+1], "White_Knight.png", 1)
                player_2_piece = Pieces.Piece("Knight", [7,(i-10)*5+1], "Black_Knight.png", 2)

            #Create the bishops:
            elif(i >= 12 and i < 14):
                player_1_piece = Pieces.Piece("Bishop", [0,(i-12)*3+2], "White_Bishop.png", 1)
                player_2_piece = Pieces.Piece("Bishop", [7,(i-12)*3+2], "Black_Bishop.png", 2)

            #Create the kings:
            elif(i == 14):
                player_1_piece = Pieces.Piece("King", [0,3], "White_King.png", 1)
                player_2_piece = Pieces.Piece("King", [7,3], "Black_King.png", 2)

            #Create the queens:
            else:
                player_1_piece = Pieces.Piece("Queen", [0,4], "White_Queen.png", 1)
                player_2_piece = Pieces.Piece("Queen", [7,4], "Black_Queen.png", 2)

            #Add both pieces to the list:

            self.player_1_pieces.append(player_1_piece)
            self.player_2_pieces.append(player_2_piece)

            #Display piece to screen

    def display_pieces(self):
        for piece in self.player_1_pieces:
            piece.display_piece_to_screen(self.tiles,self.gameDisplay)
        for piece in self.player_2_pieces:
            piece.display_piece_to_screen(self.tiles,self.gameDisplay)
        pygame.display.update()

    def get_piece_on_tile(self, tile):
        for piece in self.player_1_pieces:
            if piece.current_position == tile.coordinate:
                return piece
        for piece in self.player_2_pieces:
            if piece.current_position == tile.coordinate:
                return piece
        

    def highlight_square(self, click_location):
        highlighted_number = [8,8]
        for tile in self.tiles:
            if(tile.highlighted):
                highlighted_number = tile.coordinate
        tile = self.determine_tile_click(click_location)
        #Highlight this tile:
        if(not tile.highlighted and not self.already_highlighted):
            pygame.draw.rect(self.gameDisplay, (229, 250, 5),
                             (tile.x_position, tile.y_position, tile.height, tile.height))
            tile.highlighted = True
            self.already_highlighted = True
            return tile
        else:                        
            pygame.draw.rect(self.gameDisplay, (229, 250, 5),
                             (tile.x_position, tile.y_position, tile.height, tile.height))
            tile.highlighted = True
            pygame.draw.rect(self.gameDisplay, self.tiles[highlighted_number[0]*8+highlighted_number[1]].color,
                             (self.tiles[highlighted_number[0]*8+highlighted_number[1]].x_position,
                              self.tiles[highlighted_number[0]*8+highlighted_number[1]].y_position,
                              tile.height, tile.height))
            self.tiles[highlighted_number[0]*8+highlighted_number[1]].highlighted = False
            if(not tile.highlighted):
                self.already_highlighted = False
            else:
                return tile
        # self.display_pieces()
        # pygame.display.update()

    def display_possible_moves(self, tile, player):
        possible_moves = []
        if player == 1:
            for piece in self.player_1_pieces:
                if tile.coordinate == piece.current_position:
                    possible_moves = piece.calculate_moves(self.tiles, self.player_1_pieces, self.player_2_pieces, self.gameDisplay)
                    possible_moves = piece.induces_check(self.tiles, self.player_1_pieces, self.player_2_pieces,
                                        self.gameDisplay)
                    if piece.name == "King":
                        print(possible_moves)
                        if ([piece.current_position[0], piece.current_position[1]-1] not in possible_moves) and ([piece.current_position[0], piece.current_position[1]-2] in possible_moves):
                            possible_moves.remove([piece.current_position[0], piece.current_position[1]-2])
                        if [piece.current_position[0], piece.current_position[1]+1] not in possible_moves and ([piece.current_position[0], piece.current_position[1]+2] in possible_moves):
                            possible_moves.remove([piece.current_position[0], piece.current_position[1]+2])
                    piece.possible_moves = possible_moves
                    break
        if player == 2:
            for piece in self.player_2_pieces:
                if tile.coordinate == piece.current_position:
                    possible_moves = piece.calculate_moves(self.tiles, self.player_1_pieces, self.player_2_pieces, self.gameDisplay)
                    possible_moves = piece.induces_check(self.tiles, self.player_1_pieces, self.player_2_pieces,
                                        self.gameDisplay)
                    if piece.name == "King":
                        if [piece.current_position[0], piece.current_position[1]-1] not in possible_moves and ([piece.current_position[0], piece.current_position[1]-2] in possible_moves):
                            possible_moves.remove([piece.current_position[0], piece.current_position[1]-2])
                        if [piece.current_position[0], piece.current_position[1]+1] not in possible_moves and ([piece.current_position[0], piece.current_position[1]+2] in possible_moves):
                            possible_moves.remove([piece.current_position[0], piece.current_position[1]+2])
                    piece.possible_moves = possible_moves
                    break
        for move in possible_moves:
            pygame.draw.circle(self.gameDisplay, (102, 255, 51),
                               (int(self.tiles[move[0]*8+move[1]].x_position) + int(tile.height/2),
                                int(self.tiles[move[0]*8+move[1]].y_position) + int(tile.height/2)), 18)
            self.tiles[move[0]*8+move[1]].possible_move = True

    def clear_possible_moves(self):
        for tile in self.tiles:
            if tile.possible_move:
                pygame.draw.rect(self.gameDisplay, tile.color,
                                (tile.x_position, tile.y_position, tile.height, tile.height))
                tile.possible_move = False
            if tile.highlighted:
                pygame.draw.rect(self.gameDisplay, tile.color,
                                (tile.x_position, tile.y_position, tile.height, tile.height))
                # tile.highlighted = False

    def make_move(self, click_location, selected_tile, player):
        tile = self.determine_tile_click(click_location)
        piece = self.get_piece_on_tile(selected_tile)
        if piece == None:
            return player
        return_player = player
        if tile.coordinate in piece.potential_moves:
            self.highlight_square(click_location)
            # print("Getting here")

            # for i in range(len(self.player_1_pieces)):
            #     print(self.player_1_pieces[i].color + " " +
            #           self.player_1_pieces[i].name + ": " + 
            #           str(self.player_1_pieces[i].current_position))
            # for i in range(len(self.player_2_pieces)):
            #     print(self.player_2_pieces[i].color + " " +
            #           self.player_2_pieces[i].name + ": " + 
            #           str(self.player_2_pieces[i].current_position))

            # ERROR OCCURING BEFORE THIS LINE, ERROR IN DISPLAYING PIECES. PIECE POSITIONS CORRECT
            # time.sleep(5)
            # Position of the piece is correct but piece not displaying:
            # self.display_pieces()
            # time.sleep(2)
            # pygame.display.update()
            # if player == 1:
            #     for piece in self.player_2_pieces:
            #         piece.potential_moves = []
            # if player == 2:
            #     for piece in self.player_1_pieces:
            #         piece.potential_moves = []
            painted_tile = None
            if piece.player == player:
                painted_tile = piece.move_piece(tile, self.tiles, self.player_1_pieces, self.player_2_pieces,
                                self.gameDisplay, True, True)
                return_player = 1
                if player == 1:
                    return_player = 2
            # for piece in self.player_1_pieces:
            #     print(piece.color + " " + piece.name + ": " + str(piece.current_position))
            # for piece in self.player_2_pieces:
            #     print(piece.color + " " + piece.name + ": " + str(piece.current_position))
            if painted_tile != None:
                self.paint_corner(painted_tile)
            if(piece.check(self.tiles, self.player_1_pieces, self.player_2_pieces, piece.player, self.gameDisplay)):
                self.winning_player = piece.checkmate(self.tiles, self.player_1_pieces, self.player_2_pieces, piece.player,
                                self.gameDisplay)
                print(self.winning_player)
                if self.winning_player == None:
                    print("None")
            piece.stalemate(self.tiles, self.player_1_pieces, self.player_2_pieces, self.gameDisplay)
        self.already_highlighted = False
        self.display_pieces()
        return return_player
        
    def determine_tile_click(self, click_location):
        for tile in self.tiles:
            if(click_location[0] > tile.x_position
               and click_location[0] < tile.x_position + tile.height):
                if(click_location[1] > tile.y_position
                   and click_location[1] < tile.y_position + tile.height):
                    return tile

    def write_text(self, text, color, center_pos):
        font = pygame.font.Font('freesansbold.ttf', 25)
        text = font.render(text, True, color)
        textRect = text.get_rect()
        textRect.center = center_pos
        self.gameDisplay.blit(text, textRect)

    def game_intro(self):
        started = False
        self.gameDisplay.fill((0,255,200))
        while not started:
            pygame.draw.rect(self.gameDisplay, (246,255,0), (150,200,200,100))
            pygame.draw.rect(self.gameDisplay, (246,255,0), (450,200,200,100))
            center = (400,200)
            self.write_text("Welcome to Chess!    Select Number of Players:" , blue, (400,100))
            self.write_text("1 - Coming Soon", blue, (250,250))
            self.write_text("2",blue, (550, 250))
            selected = False
            while not selected:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = event.pos
                        if pos[0] >= 450 and pos[0] <= 700 and pos[1] >= 200 and pos[1] <= 300:
                            selected = True
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                pygame.display.update()
            started = True

    def game_outro(self):
        self.gameDisplay.fill((0,255,200))
        pygame.draw.rect(self.gameDisplay, (246,255,0), (300,350,200,100))
        self.write_text("Restart" , blue, (400,400))
        win_string = "Player " + str(self.winning_player) + " wins"
        self.write_text(win_string, blue, (400, 200))
        selected = False
        while not selected:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if pos[0] >= 300 and pos[0] <= 500 and pos[1] >= 350 and pos[1] <= 450:
                        selected = True
                        self.delete_game_board()
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                pygame.display.update()
        self.play_game()

    def delete_game_board(self):
        counter = 0
        for i in range(len(self.player_1_pieces)):
            del self.player_1_pieces[0]
        for i in range(len(self.player_2_pieces)):
            del self.player_2_pieces[0]
        for i in range(len(self.tiles)):
            del self.tiles[0]

    def play_game(self):
        self.game_intro()
        self.make_game_board()
        won = False
        player = 1
        self.winning_player = None
        while not won:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.pos[0] < (self.tiles[0].height*8):
                    self.clear_possible_moves()
                    if(self.selected_tile == None):
                        if(event.pos) == None:
                            continue
                        #Clear any previously highlighted squares:
                        # Locate the tile where the click occured
                        tile = self.highlight_square(event.pos)
                        self.selected_tile = tile
                        if not tile == None:
                            self.display_possible_moves(tile, player)
                    else:
                        if(self.selected_tile != None):
                            player = self.make_move(event.pos, self.selected_tile, player)
                            self.selected_tile = None
                            self.clear_possible_moves()
                        if self.winning_player != None:
                            print("true")
                            self.game_outro()
                if event.type == pygame.QUIT:
                    won = True
                self.display_pieces()
                pygame.display.update()
        pygame.quit()
        exit()
