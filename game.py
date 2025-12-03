import g2d
from boardgamegui import BoardGameGui
from boardgame import BoardGame

W, H = 40, 40

def print_board(board: list[int], w: int, h: int) -> None:
    """
    (Function made with debug purposes)
    Prints the passed matrix on the console.
    """
    for y in range(h):
        for x in range(w):
            term = "\n" if x == w - 1 else ""
            i = x + y * w
            print(f"{board[i]:^5}", end= term)

def get_connected_board(board: list[int], width: int, height: int) -> list[int]:
    """
    Static function that takes a board with Trees and Tents (the rest will be ignored) and it returns the same list but
    with marked Tents and Trees that are unambiguously connected together.
    The numbers corresponding to a marked tent/tree is their corresponding number + 10.
    (So if 1 is the number for a tree, 10 + 1 = 11 is the number for a tree marked as connected)

    If there already are marked trees or tents, they will first be converted to normal trees/tents, so if they
    are no longer connected they will be reset.
    """
    # Creating a copy of the list
    board = board[:]

    # Resetting trees and tents already marked as connected
    for y in range(height):
        for x in range(width):
            i = y * width + x
            if board[i] == 11 or board[i] == 12: # 11: Tree, # 12: Tent
                board[i] -= 10

    # Marking actually connected trees and tents
    found = True
    while found:
        found = False
        # Found is used for repeating the connected check until there's nothing that can be done.
        # When a connection is found, the code will iterate once again.

        for y in range(1, height):
            for x in range(1, width):
                i = y * width + x
                if board[i] == 1: # This is a tree
                    # To be unambiguously connected, a tree must be adjacent to a single tent and there must not be
                    # any empty cells adjacent to it.
                    adjs = get_adjacencies(board, width, height, x, y)

                    tent_adjs = [pos for n, pos in adjs if n == 2]
                    empty_adjs = [pos for n, pos in adjs if n == 0]

                    if len(tent_adjs) == 1 and len(empty_adjs) == 0: # The connection is unambiguous if there's only 1 tent and no empty cells
                    # if len(tent_adjs) == 1:
                        found = True
                        board[i] = 11 # So the tree will be connected
                        tent = tent_adjs[0] # Get the tent (we know for a fact it's only one)

                        # Since it's only one tent, I extract it from the list
                        tent_x, tent_y = tent
                        tent_i = tent_y * width + tent_x
                        board[tent_i] = 12 # Mark the tent as connected

                elif board[i] == 2: # This is a tent
                    # To be unambiguously connected, a tent must be adjacent to only one three.
                    adjs = get_adjacencies(board, width, height, x, y)
                    tree_adjs = [pos for n, pos in adjs if n == 1]
                    if len(tree_adjs) == 1:
                        found = True
                        board[i] = 12
                        tree = tree_adjs[0] # The tree is only one
                        tree_x, tree_y = tree
                        tree_i = tree_y * width + tree_x
                        board[tree_i] = 11

    return board

def get_adjacencies(board: list[int], width: int, height: int, x: int, y: int) -> list[int, tuple[int, int]]:
    """
    Given a board, its width and height and a specific cell...
    it returns the list of all adjacent cells (not diagonal).
    Each returned element in the list is a pair: the state and the position of the cell. (While the method inside TentsGame only returns the values).
    """
    adj = []
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        ax, ay = x + dx, y + dy
        if 0 < ax < width and 0 < ay < height:
            i = ay * width + ax
            adj.append((board[i], (ax, ay)))
    return adj

class TentsGame(BoardGame):
    def __init__(self, file: str = None):

        self._w, self._h = 0, 0

        """
        The board will be represented by a matrix of integers.
        The matrix will be a flat list.
        Each number in a single cells has a meaning (which can also be seen in the static attributes):
        - 0: Empty cell
        - 1: Tree
        - 2: Tent
        - 3: Grass
        - 90-99: The numbers from 90 to 99 will represent their unit digit number (i.e. 97 -> 7). These are used for row/col constraints.
        - 11: Tree marked as connected to a tent
        - 12: Tent marked as connected to a tree
        - -1: Null (Used for the unused first cell, it will be drawn as a black square)
        """
        self._board = []

        if file is not None:
            self._read_file(file)

        if self._w == 0 or self._h == 0 or len(self._board) == 0:
            raise ValueError("Passed matrix is empty")

    # -- STATIC ATTRIBUTES --
    ACTIONS = {
        "LeftButton": "CycleRight",
        "RightButton": "CycleLeft",
        "g": "AutoGrass", "t": "AutoTent",
        "c": "CheckConnected"
    }
    ANNOTS = {
        " ": ((128, 128, 128), 0),
        "🌳": ((10, 100, 10), 0),
        "🌿": ((100, 200, 100), 0),
        "⛺": ((255, 117, 24), 0),
        "🌳✔": ((0, 200, 0), 0),
        "⛺✔": ((255, 200, 50), 0)
    }
    TEXTS = {
        "Null": "",
        "Empty": " ",
        "Tree": "🌳", "ConnectedTree": "🌳✔",
        "Tent": "⛺", "ConnectedTent": "⛺✔",
        "Grass": "🌿",
        "Number0": "0", "Number1": "1",
        "Number2": "2", "Number3": "3",
        "Number4": "4", "Number5": "5",
        "Number6": "6", "Number7": "7",
        "Number8": "8", "Number9": "9",
    }

    # The following two must be considered "two-way dictionaries", so they must be always edited together.
    NUMBER_STATES = {
        -1: "Null",
        0: "Empty",
        1: "Tree", 11: "ConnectedTree",
        2: "Tent", 12: "ConnectedTent",
        3: "Grass",
        90: "Number0",  91: "Number1",
        92: "Number2",  93: "Number3",
        94: "Number4",  95: "Number5",
        96: "Number6",  97: "Number7",
        98: "Number8",  99: "Number9"
    }
    STATE_NUMBERS = {
        "Null": -1,
        "Empty": 0,
        "Tree": 1, "ConnectedTree": 11,
        "Tent": 2, "ConnectedTent": 12,
        "Grass": 3,
        "Number0": 90,  "Number1": 91,
        "Number2": 92,  "Number3": 93,
        "Number4": 94,  "Number5": 95,
        "Number6": 96,  "Number7": 97,
        "Number8": 98, "Number9": 99
    }

    # -- INHERITED METHODS --
    def play(self, x: int, y: int, action: str):
        if self._check_out_of_bounds(x, y):
            i = self._w * y + x
            match action:
                case "CycleRight":
                    match self._board[i]:
                        case 0: self._board[i] = 2
                        case 2: self._board[i] = 3
                        case 3: self._board[i] = 0
                case "CycleLeft":
                    match self._board[i]:
                        case 0: self._board[i] = 3
                        case 2: self._board[i] = 0
                        case 3: self._board[i] = 2
                case "AutoGrass":
                    self._auto_grass()
                case "AutoTent":
                    self._auto_tent()
                case "CheckConnected": # Debug
                    print_board(self.connect_trees_tents(), self._w, self._h)

    def finished(self) -> bool:
        return self._check_equity() and \
            self._check_all_trees() and \
            self._check_all_tents_adj_trees() and \
            self._check_all_tents_vicinity() and \
            self._check_row_constraints() and \
            self._check_col_constraints()

    def cols(self) -> int:
        return self._w
    def rows(self) -> int:
        return self._h

    def read(self, x: int, y: int) -> str:
        return self._cell_text(self._cell_state(x, y))

    def status(self) -> str:
        print(f"{self.wrong(): = }")
        if self.finished():
            return "Puzzle solved"
        if not self._check_equity():
            return "# of tents != # of trees"
        elif not self._check_all_trees():
            return "Not all trees have a tent"
        elif not self._check_all_tents_adj_trees():
            return "Not all tents have a tree"
        elif not self._check_all_tents_vicinity():
            return "Tents must be distant"
        elif not self._check_row_constraints():
            return "Row constraints not satisfied"
        elif not self._check_col_constraints():
            return "Column constraints not satisfied"
        else:
            return "Huh? Even I'm confused!" # Not possible case

    # -- PLAY METHODS --
    def _auto_grass(self):
        # Clear near tent
        self._board = self.connect_trees_tents()
        for y in range(self._h):
            for x in range(self._w):
                if self._cell_state(x, y) == "Empty" and {self._get_state_number("Tent"), self._get_state_number("ConnectedTent")} & set(self.get_near_cells(x, y)):
                    i = y * self._w + x
                    self._board[i] = self._get_state_number("Grass")

        # Check for row constraints
        self._board = self.connect_trees_tents()
        for y in range(1, self._h):  # First row and column are skipped, as they contain the actual constraints.
            if self._check_row_constraint(y):
                for x in range(1, self._w):
                    if self._cell_state(x, y) == "Empty":
                        i = y * self._w + x
                        self._board[i] = self._get_state_number("Grass")

        # Check for column constraints
        self._board = self.connect_trees_tents()
        for x in range(1, self._w):
            if self._check_col_constraint(x):
                for y in range(1, self._h):
                    if self._cell_state(x, y) == "Empty":
                        i = y * self._w + x
                        self._board[i] = self._get_state_number("Grass")

        # Check if not near any tree
        self._board = self.connect_trees_tents()
        for x in range(1, self._w):
            for y in range(1, self._h):
                if self._cell_state(x, y) == "Empty":
                    adjs = self.get_adjacent_cells(x, y)
                    if self._get_state_number("Tree") not in adjs:
                        i = x + y * self._w
                        self._board[i] = self._get_state_number("Grass")

    def _auto_tent(self):
        # Check for row constraints
        self._board = self.connect_trees_tents()
        for y in range(1, self._h):
            tent_number, *cells = self._get_row(y)
            tent_number -= 90
            if tent_number == cells.count(self._get_state_number("Tent")) + cells.count(self._get_state_number("Empty")) + cells.count(self._get_state_number("ConnectedTent")):
                for x in range(1, self._w):
                    if self._cell_state(x, y) == "Empty":
                        i = y * self._w + x
                        self._board[i] = self._get_state_number("Tent")

        # Check for column constraints
        self._board = self.connect_trees_tents()
        for x in range(1, self._w):
            tent_number, *cells = self._get_column(x)
            tent_number -= 90
            if tent_number == cells.count(self._get_state_number("Tent")) + cells.count(self._get_state_number("Empty")) + cells.count(self._get_state_number("ConnectedTent")):
                for y in range(1, self._h):
                    if self._cell_state(x, y) == "Empty":
                        i = y * self._w + x
                        self._board[i] = self._get_state_number("Tent")


        # Check if there's a tree with exactly one empty adjacent cell
        self._board = self.connect_trees_tents()
        for x in range(1, self._w):
            for y in range(1, self._h):
                if self._cell_state(x, y) == "Tree":
                    adjs = get_adjacencies(self._board, self._w, self._h, x, y)
                    empty_adjs = [pos for state, pos in adjs if state == self._get_state_number("Empty")]
                    tent_adjs = [pos for state, pos in adjs if state == self._get_state_number("Tent")]
                    # TODO: Capire se ci vuole oppure no
                    # Pare di no
                    # tent_adjs += [pos for state, pos in adjs if state == self._get_state_number("ConnectedTent")]
                    if len(tent_adjs) == 0 and len(empty_adjs) == 1:
                        empty_cell = empty_adjs[0]
                        cell_x, cell_y = empty_cell
                        cell_i = cell_y * self._w + cell_x
                        self._board[cell_i] = self._get_state_number("Tent")

                        self._auto_grass() # When a tent is placed, grass will automatically be placed around it
                        # This prevents multiple tents being placed next to each other "at the same time".

    def connect_trees_tents(self) -> list[int]:
        return get_connected_board(self._board, self._w, self._h)

    # -- UTILITY METHODS --
    def _count_trees(self) -> int:
        """
        Returns total number of trees in the board
        """
        return self._board.count(self._get_state_number("Tree")) + self._board.count(self._get_state_number("ConnectedTree"))

    def _count_tents(self) -> int:
        """
        Returns total number of tents in the board
        """
        return self._board.count(self._get_state_number("Tent")) + self._board.count(self._get_state_number("ConnectedTent"))


    def _cell_number(self, x: int, y: int) -> int:
        """
        Returns the exact number that represents the state of the cell at (x, y).
        """
        if 0 <= x < self._w and 0 <= y < self._h: # Different from the method as it also includes row and column 0 (constraint column/row)
            return self._board[y * self._w + x]
        raise IndexError(f"Out of bounds: {(x, y)}")

    def _cell_state(self, x: int, y: int) -> str:
        """
        Returns the state of the cell at (x, y) as a string with a specific value.
        """
        number = self._cell_number(x, y)
        return self._get_number_state(number)

    def _get_number_state(self, number: int) -> str:
        """
        Returns the associated state to the number passed as an argument.
        """
        if number in self.NUMBER_STATES:
            return self.NUMBER_STATES[number]
        raise ValueError("Invalid state number")

    def _get_state_number(self, state: str) -> int:
        """
        Returns the associated number to the state passed as an argument.
        """
        if state in self.STATE_NUMBERS:
            return self.STATE_NUMBERS[state]
        raise ValueError("Invalid state")

    def _cell_text(self, state: str):
        """
        Returns the text that must be rendered to represent the state passed.
        """
        if state in self.TEXTS:
            return self.TEXTS[state]
        raise ValueError(f"Invalid state: {state}")

    def _get_column(self, x: int) -> list[int]:
        """
        Returns a list of all the cells in the specified column.
        """
        col = []
        i = x
        for _ in range(self._h):
            col.append(self._board[i])
            i += self._w
        return col

    def _get_row(self, y: int) -> list[int]:
        """
        Returns a list of all the cells in the specified row.
        """
        row = []
        i = y * self._w
        for _ in range(self._w):
            row.append(self._board[i])
            i += 1
        return row

    def get_near_cells(self, x: int, y: int) -> list[int]:
        """
        Returns an unordered list of all the cells near the cell at the passed coordinates.
        Diagonal cells are included.
        """
        adjs = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                adj_x, adj_y = x + dx, y + dy
                adj_i = adj_y * self._w + adj_x
                if self._check_out_of_bounds(adj_x, adj_y):
                    if dx != 0 or dy != 0:  # The center cell is not considered
                        adjs.append(self._board[adj_i])
        return adjs

    def get_adjacent_cells(self, x: int, y: int) -> list[int]:
        """
        Returns an unordered list of all the cells adjacent to the cell at the passed coordinates.
        Diagonal cells are excluded.
        """
        adjs = []
        for dx, dy in ((-1, 0), (0, -1), (1, 0), (0, 1)):
            adj_x, adj_y = x + dx, y + dy
            adj_i = adj_y * self._w + adj_x
            if self._check_out_of_bounds(adj_x, adj_y):
                adjs.append(self._board[adj_i])
        return adjs

    def _read_file(self, filename: str):
        """
        Method called on game initialization if a file has been passed as an argument.
        It will load a board based on the contents of the file.
        The file must contain a valid matrix of numbers (not separated by anything).
        It must contain only the matrix and nothing else.
        A matrix is valid if each row has the same length (if the rows are valid the columns will also be valid).
        The matrix doesn't have to be square to be considered valid.
        The very first cell will be ignored, as it doesn't contain anything useful in the game.
        The first row and first column MUST contain single digit numbers between 0 and the matrix height/width respectively.
        These numbers will be the column/row constraints.

        All the other cells may contain one of the following symbols:
        (.) - The dot, which means that the corresponding cell will be marked as empty.
        (T) - The letter T, which means that the corresponding cell will be marked as a tree.
        """
        self._w = 0
        self._h = 0
        self._board = []

        with open(filename, "r") as file:
            for line in file:
                line = line.strip()
                # Width / Height management
                if self._w == 0:
                    self._w = len(line)
                elif len(line) != self._w:
                    raise ValueError("The file does not contain a valid matrix")
                self._h += 1

                # Cell values
                for c in line:
                    match c:
                        case ".":
                            self._board.append(0)
                        case "T":
                            self._board.append(1)
                        case c if "0" <= c <= "9":
                            self._board.append(int(c) + 90) # Digits are represented as themselves + 90

            self._board[0] = -1 # Ignore first cell

    # -- CHECK METHODS --
    def _check_equity(self) -> bool:
        """
        Checks that the number of tents and trees are equal.
        """
        return self._count_trees() == self._count_tents()

    def _check_out_of_bounds(self, x: int, y: int) -> bool:
        """
        Checks that the cell at (x, y) is a valid cell.
        (Constraints cells, in first row and first column, are not included).
        """
        return 1 <= x < self._w and 1 <= y < self._h

    def _check_if_is_adjacent(self, x: int, y: int, state: str) -> bool:
        """
        Returns True if there is at least one adjacent (not diagonal) cell of type state.
        Otherwise, returns False.
        """
        for adj_x, adj_y in ((x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)):
            if self._check_out_of_bounds(adj_x, adj_y): # Se è fuori, siamo a bordo e si può ignorare
                if self._cell_state(adj_x, adj_y) == state:
                    return True
        return False

    def _check_if_is_near(self, x: int, y: int, state: str) -> bool:
        """
        Returns True if there is at least one cell of type "state" near the cell at position (x, y).
        Otherwise, returns False.
        Diagonal cells are included.
        """
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                near_x, near_y = x + dx, y + dy
                if (near_x, near_y) != (x, y) and self._check_out_of_bounds(near_x, near_y): # The central cell will not be checked
                    if self._cell_state(near_x, near_y) == state:
                        return True
        return False

    def _check_tree_adjacency(self, x: int, y: int) -> bool:
        """
        Checks if the passed tree at (x, y) has at least one adjacent (not diagonal) cell.
        """
        if self._cell_state(x, y) != "Tree" and self._cell_state(x, y) != "ConnectedTree":
            raise ValueError("Not a tree")

        return self._check_if_is_adjacent(x, y, "Tent") or self._check_if_is_adjacent(x, y, "ConnectedTent")

    def _check_all_trees(self) -> bool:
        """
        Checks if all trees have at least one adjacent (not diagonal) tent.
        """
        for i in range(self._h):
            for j in range(self._w):
                # If Tree is in the string of cell state, then it must be a Tree or a ConnectedTree
                if "Tree" in self._cell_state(i, j) and not self._check_tree_adjacency(i, j):
                    return False
        return True

    def _check_tent_adjacency(self, x: int, y: int) -> bool:
        """
        Checks if the passed tent has at least one adjacent (not diagonal) tree.
        """
        if self._cell_state(x, y) != "Tent" and self._cell_state(x, y) != "ConnectedTent":
            raise ValueError("Not a tent")

        return self._check_if_is_adjacent(x, y, "Tree") or self._check_if_is_adjacent(x, y, "ConnectedTree")

    def _check_tent_vicinity(self, x: int, y: int) -> bool:
        """
        Checks if the passed tent has at least one near (diagonal is valid) tent.
        """
        if self._cell_state(x, y) != "Tent" and self._cell_state(x, y) != "ConnectedTent":
            raise ValueError("Not a tent")
        return self._check_if_is_near(x, y, "Tent") or self._check_if_is_near(x, y, "ConnectedTent")

    def _check_all_tents_adj_trees(self) -> bool:
        """
        Checks if all tents have at least one adjacent (not diagonal) tree.
        """
        for i in range(self._h):
            for j in range(self._w):
                if "Tent" in self._cell_state(i, j) and not self._check_tent_adjacency(i, j):
                    return False
        return True

    def _check_all_tents_vicinity(self) -> bool:
        """
        Checks if all tents have no near (diagonal is valid) tent.
        """
        for i in range(self._h):
            for j in range(self._w):
                if "Tent" in self._cell_state(i, j) and self._check_tent_vicinity(i, j):
                    return False
        return True

    def _check_row_constraint(self, row: int):
        """
        Checks if the tent number constraint is satisfied for the specified row.
        It must not be called on the first row (as it is the row of the column constraints.
        """
        if row == 0:
            raise ValueError("You can't pass the constraint row.")

        tent_number, *cells = [c for c in self._get_row(row)]
        tent_number -= 90  # Because numbers are set as 90 + the actual number
        return tent_number == cells.count(self._get_state_number("Tent")) + cells.count(self._get_state_number("ConnectedTent"))

    def _check_row_constraints(self):
        """
        Checks if the tent number constraint is satisfied for every row.
        """
        for r in range(1, self._h): # First row is excluded because it's for constraints
            if not self._check_row_constraint(r):
                return False
        return True

    def _check_col_constraint(self, col: int):
        """
        Checks if the tent number constraint is satisfied for the specified column.
        """
        if col == 0:
            raise ValueError("You can't pass the constraint column.")

        tent_number, *cells = [r for r in self._get_column(col)]
        tent_number -= 90  # Because numbers are set as 90 + the actual number
        return tent_number == cells.count(self._get_state_number("Tent")) + cells.count(self._get_state_number("ConnectedTent"))

    def _check_col_constraints(self):
        """
        Checks if the tent number constraint is satisfied for every column.
        """
        for c in range(1, self._w): # First column is excluded because it's for constraints
            if not self._check_col_constraint(c):
                return False
        return True

    def _check_complete_rows(self) -> bool:
        """
        Checks if all complete (without empty spaces) rows have as many tents as said by the constraint.
        Returns True if so. If there's an invalid row, returns False.
        If this is false, at least a cell must be set to empty to solve the game.
        """
        for y in range(1, self._h):
            tent_number, *cells = self._get_row(y)
            empty_cells = [cell for cell in cells if cell == self._get_state_number("Empty")]
            if len(empty_cells) == 0:
                if self._check_row_constraint(y) == False:
                    return False
        return True

    def _check_complete_cols(self) -> bool:
        """
        Checks if all complete (without empty spaces) columns have as many tents as said by the constraint.
        Returns True if so. If there's an invalid row, returns False.
        If this is false, at least a cell must be set to empty to solve the game.
        """
        for x in range(1, self._w):
            tent_number, *cells = self._get_column(x)
            empty_cells = [cell for cell in cells if cell == self._get_state_number("Empty")]
            if len(empty_cells) == 0:
                if self._check_col_constraint(x) == False:
                    return False
        return True

    def _check_tents_below_constraint(self):
        """
        Checks if every row AND column has less tants than said by the constraint.
        This is because if there are more tents than what's written on the row/column,
        the board is surely in a wrong state.
        """
        # Rows
        for y in range(1, self._h):
            row = self._get_row(y)
            tent_number, *cells = row
            tents = [pos for state, pos in cells if state == self._get_state_number("Tent") or state == self._get_state_number("ConnectedTent")]

            if len(tents) > tent_number:
                return False

        for x in range(1, self._w):
            col = self._get_column(x)
            tent_number, *cells = col
            tents = [pos for state, pos in cells if state == self._get_state_number("Tent") or state == self._get_state_number("ConnectedTend")]

            if len(tents) > tent_number:
                return False

        return True

    def wrong(self):
        """
        Returns True if the board is in a state where at least one cell MUST be removed to be solved.
        """
        return not all((
            self._check_complete_rows(),
            self._check_complete_cols(),
            self._check_all_tents_vicinity(),
            # TODO: Inserire altre condizioni di errore
            self._check_tents_below_constraint()
            # - Albero senza tende e senza celle libere vicine

        ))

def tents_gui_play(game_instance: TentsGame):
    g2d.init_canvas((game_instance.cols() * W, game_instance.rows() * H + H))
    ui = BoardGameGui(game_instance, game_instance.ACTIONS, game_instance.ANNOTS)
    g2d.main_loop(ui.tick)

if __name__ == "__main__":
    game = TentsGame("levels/tents-2025-11-27-8x8-easy.txt")
    tents_gui_play(game)