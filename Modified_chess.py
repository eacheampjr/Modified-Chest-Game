class ImplementInSubClass(Exception):
    """To override parent class ChessPiece"""
    pass


class ChessVar:
    """
    ChessVar's main responsibility is to keep track of the current
    state of the game. Making sure to track player turn, when game is finihsed
    or when in suspension.

   ChessVar will need to maintain interactions with chessboard and game
    condition class in order to receive information of the state of the game.
    """

    def __init__(self):
        """
        Initialize data members such as state of game and player turn,
        white captured pieces and black captured pieces
        """

        self._get_game_state = 'UNFINISHED'  # UNFINISHED, WHITE_WON, BLACK_WON
        self._game_turn = 'WHITE'  # White is always the starting player
        self._chess_board = self.starting_board_layout()
        self._captured_counts = {'WHITE': {}, 'BLACK': {}}  # Tracks captured pieces

    def get_game_turn(self):
        """Returns game turn"""

        return self._game_turn
    
    def set_game_turn(self, players_turn):
        """sets item location"""

        self._game_turn = players_turn

    def set_game_state(self, game_condition):
        """sets state of game"""
        
        # UNFINISHED, WHITE_WON, BLACK_WON
        self._get_game_state = game_condition


    def starting_board_layout(self):
        """Starting board layout for modified chess game"""

        # Creating an 8 by 8 layout to set initial layout
        chessboard = [[None for _ in range(8)] for _ in range(8)]

        # Initial positioning for each chess piece
        # Place white pieces
        chessboard[0][0] = Rook('WHITE', 'a1')
        chessboard[0][1] = Knight('WHITE', 'b1')
        chessboard[0][2] = Bishop('WHITE', 'c1')
        chessboard[0][3] = Queen('WHITE', 'd1')
        chessboard[0][4] = King('WHITE', 'e1')
        chessboard[0][5] = Bishop('WHITE', 'f1')
        chessboard[0][6] = Knight('WHITE', 'g1')
        chessboard[0][7] = Rook('WHITE', 'h1')

        # Arranges pawn
        for i in range(8):
            chessboard[1][i] = Pawn('WHITE', chr(97 + i) + '2')

        # Place black pieces
        chessboard[7][0] = Rook('BLACK', 'a8')
        chessboard[7][1] = Knight('BLACK', 'b8')
        chessboard[7][2] = Bishop('BLACK', 'c8')
        chessboard[7][3] = Queen('BLACK', 'd8')
        chessboard[7][4] = King('BLACK', 'e8')
        chessboard[7][5] = Bishop('BLACK', 'f8')
        chessboard[7][6] = Knight('BLACK', 'g8')
        chessboard[7][7] = Rook('BLACK', 'h8')

        # Arranges pawn
        for i in range(8):
            chessboard[6][i] = Pawn('BLACK', chr(97 + i) + '7')

        return chessboard

    def print_chessboard(self):
        """Prints the current state of the chess board."""
        print(  "     a   b   c   d   e   f   g   h")
        print(" +-----------------------------------+")
        for i in range(8):
            # label rows by number
            print(str(i + 1) + ' |', end=' ')
            for j in range(8):
                piece = self._chess_board[i][j]
                if piece is None:
                    print('..', end='  ')  # Print two dots for empty squares
                else:
                    print(piece.get_icon(), end='  ')  # Print the piece's icon with spacing
            print('| ' + str(i + 1))
        print(" +-----------------------------------+")
        print(  "     a   b   c   d   e   f   g   h")


    def make_move(self, move_from, move_to):
        if not self.is_game_ongoing():
            return False

        if not self.is_valid_move(move_from, move_to):
            return False

        self.execute_move(move_from, move_to)
        self.switch_turn()
        return True

    def is_game_ongoing(self):
        return self._get_game_state == 'UNFINISHED'

    def is_valid_move(self, move_from, move_to):
        from_row, from_column = self.move_conversion(move_from)
        
        moving_piece = self._chess_board[from_row][from_column]
        if not moving_piece or moving_piece._color != self._game_turn:
            return False

        return moving_piece.allowable_move(move_to, self._chess_board)

    def execute_move(self, move_from, move_to):
        from_row, from_column = self.move_conversion(move_from)
        to_row, to_column = self.move_conversion(move_to)

        moving_piece = self._chess_board[from_row][from_column]
        target_square = self._chess_board[to_row][to_column]

        if target_square:
            self.capture_piece(to_row, to_column)

        self._chess_board[to_row][to_column] = moving_piece
        self._chess_board[from_row][from_column] = None
        moving_piece.update_position(move_to)

    def switch_turn(self):
        self._game_turn = 'BLACK' if self._game_turn == 'WHITE' else 'WHITE'

    def move_conversion(self, algebraic_notation):
        """
        Convert algebraic notation to board row and column indices to make logical move
        """
        column_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        column = column_map[algebraic_notation[0]]
        row = int(algebraic_notation[1]) - 1
        return row, column

    def capture_piece(self, row, column):
        """
        Captures a piece at the specified location, updates captured count,
        and removes the piece from the board.
        """
        captured_piece = self._chess_board[row][column]
        if captured_piece:
            # Update captured piece count
            color = captured_piece._color
            piece_type = captured_piece._piece_type
            self._captured_counts[color][piece_type] = self._captured_counts[color].get(piece_type, 0) + 1

            # Remove the captured piece from the board
            self._chess_board[row][column] = None

            # Check for victory condition
            if self.check_win(piece_type, color):
                if color == 'BLACK':
                    self.set_game_state('WHITE_WON')
                
                else:
                    self.set_game_state('BLACK_WON')

                # self._game_state = 'WHITE_WON' if color == 'BLACK' else 'BLACK_WON'

    def check_win(self, piece_type, opponent_color):
        """
        Validates if all types of a specific piece have been captured for a win.
        """

        # Total number of each piece to calculate from
        total_pieces = {'Pawn': 8, 'Knight': 2, 'Bishop': 2, 'Rook': 2, 'Queen': 1, 'King': 1}

        captured_count = self._captured_counts[opponent_color].get(piece_type, 0)

        # Check if all pieces of a type have been captured or if the Queen has been captured
        return captured_count == total_pieces[piece_type] or (piece_type == 'Queen' and captured_count == 1)

    def get_game_state(self):
        """
        Returns the current state of the game.
        """

        # Check if all of a certain type of piece for either player have been captured
        for color, captured in self._captured_counts.items():
            for piece_type, count in captured.items():
                if self.meet_win_condition(piece_type, count):
                    return 'WHITE_WON' if color == 'BLACK' else 'BLACK_WON'

        # If no victory condition is met, the game is still unfinished
        return 'UNFINISHED'

    def meet_win_condition(self, piece_type, count):
        """
        Check if win condition is met for a specific piece type.
        """
        total_pieces = {'Pawn': 8, 'Knight': 2, 'Bishop': 2, 'Rook': 2, 'Queen': 1, 'King': 1}
        return count == total_pieces[piece_type]


class ChessPiece:
    """
    Responsible for creating a template for multiple chess pieces and boundaries
    regarding legal moves for the chess. ChessPieces and it's inheritance will
    communicate with chessboard to optimize current chess status and positions

    data_members: chess piece name, allowed legal moves
    """

    def __init__(self, piece_type, color, position):
        """
        Initializing chess piece shared data members
        """
        self._piece_type = piece_type
        self._color = color
        self._position = position

    def update_position(self, new_position):
        """
        Updates the piece's position to the new position.
        """
        self._position = new_position

        return self._position

    def allowable_move(self, new_position, board):
        """
        Determine if a move to a new position is legal for this piece, given the current
        state of the board. This method will be overridden in subclasses for specific pieces.
        """
        raise ImplementInSubClass('Use method in subclass')


class Pawn(ChessPiece):
    """
    Class inherited from ChessPiece to help profile a unique
    move set for pawn
    """

    def __init__(self, color, position):
        """Initializing data members from parent class"""
        super().__init__('Pawn', color, position)

        self._icon = 'wP' if self._color == 'WHITE' else 'bP'  # wP for white pawn and bP for black pawn

    def get_icon(self):
        """returns representation of chess piece"""

        return self._icon

    def update_position(self, new_position):
        """
        Updates the piece's position to the new position.
        """
        self._position = new_position

        return self._position

    def allowable_move(self, new_position, board):
        """determines a valid move for pawn"""

        # Matching each colum to their respective letter
        assigned_column = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

        current_column = assigned_column[self._position[0]]
        new_column = assigned_column[new_position[0]]

        current_row = int(self._position[1])
        new_row = int(new_position[1])

        # Check if the move is a valid forward move
        if self._color == 'WHITE':
            # Standard movement for pawn
            if current_column == new_column and new_row == current_row + 1:
                return board[current_row][current_column] is None

            # Special piece move (only during initial move)
            elif current_row == 2 and current_column == new_column and new_row == 4:
                return board[3][current_column] is None and board[2][current_column] is None

            # elif current_row == 2 and current_column == new_column and new_row == 4:
            #     return board[2][current_column] is None and board[3][current_column] is None

            # Capturing diagonal move for pawn
            elif new_row == current_row + 1 and abs(new_column - current_column) == 1:
                return self.is_capture_move(new_column, new_row, board)

        elif self._color == 'BLACK':
            # Standard movement for pawn
            if current_column == new_column and new_row == current_row - 1:
                return board[current_row - 2][current_column] is None

            # Special piece move (only during initial move)
            elif current_row == 7 and current_column == new_column and new_row == 5:
                return board[4][current_column] is None and board[5][current_column] is None

            # Capturing diagonal move for pawn
            elif new_row == current_row - 1 and abs(new_column - current_column) == 1:
                return self.is_capture_move(new_column, new_row, board)

        return False  # Not a valid move

    def is_capture_move(self, new_column, new_row, board):
        """
        Check if the move is a capturing move.
        """
        # Adjusting due to zero based indexing
        row_index = new_row - 1

        # Setting capture boundary
        if 0 <= row_index < 8 and 0 <= new_column < 8:
            targeted_capture = board[row_index][new_column]

            # validate opponent's piece
            if targeted_capture is not None:
                opponent_piece = targeted_capture._color != self._color
                return opponent_piece

        return False  # Return False if the target square is out of bounds or empty


class Knight(ChessPiece):
    """
    Class inherited from ChessPiece to help profile a unique
    move set for knight. Knights can jump over other pieces and capture
    what they land on.
    """

    def __init__(self, color, position):
        """Initializing data members from parent class"""
        super().__init__('Knight', color, position)

        self._icon = 'wK' if self._color == 'WHITE' else 'bK'  # wK for white knight and bK for black knight

    def get_icon(self):
        """returns representation of chess peice"""

        return self._icon

    def update_position(self, new_position):
        """
        Updates the piece's position to the new position.
        """
        self._position = new_position

        return self._position

    def allowable_move(self, new_position, board):
        """
        Determines a valid move for knight.
        """
        # Matching each column to their respective letter
        assigned_column = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

        current_column = assigned_column[self._position[0]]
        new_column = assigned_column[new_position[0]]

        current_row = int(self._position[1])
        new_row = int(new_position[1])

        # Calculate the move's row and column differences
        row_diff = abs(new_row - current_row)
        column_diff = abs(new_column - current_column)

        # Check for valid L-shaped move (2 squares in one direction, 1 square in another)
        if (row_diff == 2 and column_diff == 1) or (row_diff == 1 and column_diff == 2):

            # Knights can jump over other pieces, no need to check path
            # Checks if landing on an opponent's piece or empty square
            target_square = board[new_row - 1][new_column]
            if target_square is None or target_square._color != self._color:
                return True

        return False  # Not a valid move


class Bishop(ChessPiece):
    """
    Class inherited from ChessPiece to represent a Bishop.
    """

    def __init__(self, color, position):
        """Initializing data members from parent class"""
        super().__init__('Bishop', color, position)

        self._icon = 'wB' if self._color == 'WHITE' else 'bB'  # wB for white bishop and bB for black bishop

    def get_icon(self):
        """returns representation of chess peice"""

        return self._icon

    def update_position(self, new_position):
        """
        Updates the piece's position to the new position.
        """
        self._position = new_position

        return self._position

    def allowable_move(self, new_position, board):
        """
        Determines a valid move for bishop based on diagonal movement.
        """
        assigned_column = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

        current_column = assigned_column[self._position[0]]
        new_column = assigned_column[new_position[0]]

        current_row = int(self._position[1])
        new_row = int(new_position[1])

        # Checks for diagonal movement
        if abs(new_column - current_column) == abs(new_row - current_row):

            # Ensure path is clear - bishops have no hops (can't jump)
            column_step = 1 if new_column > current_column else -1
            row_step = 1 if new_row > current_row else -1

            for step in range(1, abs(new_column - current_column)):
                if board[current_row + step * row_step - 1][current_column + step * column_step] is not None:
                    return False  # Path is blocked

            # Checks if the target square is either empty or has an opponent's piece
            target_square = board[new_row - 1][new_column]
            if target_square is None or target_square._color != self._color:
                return True

        return False  # Not a valid move


class Rook(ChessPiece):
    """
    Class inherited from ChessPiece to represent a Rook.
    Rooks can move horizontally or vertically any number of squares, as long as the path is not blocked.
    """

    def __init__(self, color, position):
        """Initializing data members from parent class"""
        super().__init__('Rook', color, position)

        self._icon = 'wR' if self._color == 'WHITE' else 'bR'  # wR for white rook and bR for black rook

    def get_icon(self):
        """returns representation of chess peice"""

        return self._icon

    def update_position(self, new_position):
        """
        Updates the piece's position to the new position.
        """
        self._position = new_position

        return self._position

    def allowable_move(self, new_position, board):
        """
        Determines a valid move for rook based on horizontal or vertical movement.
        """
        assigned_column = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

        current_column = assigned_column[self._position[0]]
        new_column = assigned_column[new_position[0]]

        current_row = int(self._position[1])
        new_row = int(new_position[1])

        # Check for horizontal or vertical movement
        if current_column == new_column or current_row == new_row:
            # Determine the direction of movement
            column_step = 0 if current_column == new_column else (1 if new_column > current_column else -1)
            row_step = 0 if current_row == new_row else (1 if new_row > current_row else -1)

            # This one is a straight shooter
            # Picks the none zero value since it is always going to move straight in one direction
            steps = max(abs(new_column - current_column), abs(new_row - current_row))
            for step in range(1, steps):
                if board[current_row + step * row_step - 1][current_column + step * column_step] is not None:
                    return False  # Path is blocked

            # Check if the target square is either empty or has an opponent's piece
            target_square = board[new_row - 1][new_column]
            if target_square is None or target_square._color != self._color:
                return True

        return False  # Not a valid move


class Queen(ChessPiece):
    """
    Class inherited from ChessPiece to represent a Queen.
    Queens have the combined movement of a rook and bishop
    """

    def __init__(self, color, position):
        """Initializing data members from parent class"""
        super().__init__('Queen', color, position)

        self._icon = 'wQ' if self._color == 'WHITE' else 'bQ'  # wQ for white queen and bQ for black queen

    def get_icon(self):
        """returns representation of chess peice"""

        return self._icon

    def update_position(self, new_position):
        """
        Updates the piece's position to the new position.
        """
        self._position = new_position

        return self._position

    def allowable_move(self, new_position, board):
        """
        Determines a valid move for queen based on horizontal, vertical, and diagonal movement.
        """
        assigned_column = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

        current_column = assigned_column[self._position[0]]
        new_column = assigned_column[new_position[0]]

        current_row = int(self._position[1])
        new_row = int(new_position[1])

        column_diff = abs(new_column - current_column)
        row_diff = abs(new_row - current_row)

        # Check for horizontal, vertical, or diagonal movement
        if current_column == new_column or current_row == new_row or column_diff == row_diff:
            column_step = 0 if current_column == new_column else (1 if new_column > current_column else -1)
            row_step = 0 if current_row == new_row else (1 if new_row > current_row else -1)

            steps = max(column_diff, row_diff)
            for step in range(1, steps):
                if board[current_row + step * row_step - 1][current_column + step * column_step] is not None:
                    return False  # Path is blocked

            # Check if the target square is either empty or has an opponent's piece
            target_square = board[new_row - 1][new_column]
            if target_square is None or target_square._color != self._color:
                return True

        return False  # Not a valid move


class King(ChessPiece):
    """
    Class inherited from ChessPiece to represent a King.
    """

    def __init__(self, color, position):
        """Initializing data members from parent class"""
        super().__init__('King', color, position)

        self._icon = 'wK' if self._color == 'WHITE' else 'bK'  # wK for white king and bP for black king

    def get_icon(self):
        """returns representation of chess peice"""

        return self._icon

    def update_position(self, new_position):
        """
        Updates the piece's position to the new position.
        """
        self._position = new_position

        return self._position

    def allowable_move(self, new_position, board):
        """
        Determines a valid move for king based on its movement capabilities.
        """
        assigned_column = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}

        current_column = assigned_column[self._position[0]]
        new_column = assigned_column[new_position[0]]

        current_row = int(self._position[1])
        new_row = int(new_position[1])

        # Check if the move is one square in any direction
        column_diff = abs(new_column - current_column)
        row_diff = abs(new_row - current_row)

        if column_diff <= 1 and row_diff <= 1:
            # Check if the target square is either empty or has an opponent's piece
            target_square = board[new_row - 1][new_column]
            if target_square is None or target_square._color != self._color:
                return True

        return False  # Not a valid move

def main():
    # Initialize the chess game
    game = ChessVar()

    # Print the final state of the game board
    game.print_chessboard()

    # Sequence of moves
    moves = [
        ('g1', 'f3'),  # White moves knight to f3
        ('b8', 'c6'),  # Black moves knight to c6
        ('d2', 'd4'),  # White moves pawn
        ('g8', 'f6'),  # Black moves other knight to f6
        ('c2', 'c4'),  # White moves pawn
        ('d7', 'd5'),  # Black moves pawn
        ('b1', 'c3'),  # White moves another knight to c3
        # Black makes a non-knight move
        ('e7', 'e6'),  # Example move, adjust based on the board state
        ('f3', 'e5'),  # White knight captures knight on c6
        # Black makes a non-knight move
        ('f8', 'e7'),  # Example move, adjust based on the board state
        ('c3', 'd5'),  # White knight captures knight on f6
        ('a7', 'a5'),
        ('e5', 'c6'),
        ('h7', 'h5'),
        ('d5', 'f6'),
             ]

    # Execute the moves
    for move_from, move_to in moves:
        result = game.make_move(move_from, move_to)
        print(f"Move from {move_from} to {move_to}: {'Successful' if result else 'Failed'}")

    # Print the final state of the game board
    game.print_chessboard()

    # Get the current state of the game
    print("Game State:", game.get_game_state())

if __name__ == '__main__':
    main()

