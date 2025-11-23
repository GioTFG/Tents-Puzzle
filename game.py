import g2d
from boardgamegui import BoardGameGui
from boardgame import BoardGame

W, H = 40, 40

class TentsGame(BoardGame):
    def __init__(self, w: int = 6, h: int = 6):

        self._w, self._h = w, h

        self._board = [ # Tenda: 2, Albero: 1, Vuoto: 0
            # The next two lines are for column and row number rules
            # Numeri: 90 -> 0, 91 -> 1, 92 -> 2, 93 -> 3 ecc.
            # -1: Null (Do not draw)
            -1, 92, 90, 91, 90, 92,
            92, 0,  1,  0,  0,  0,
            90, 0,  0,  0,  0,  1,
            92, 0,  1,  0,  1,  0,
            90, 0,  0,  0,  0,  1,
            91, 0,  0,  0,  0,  0
        ]

    # Static attributes
    ACTIONS = {
        "LeftButton": "CycleRight",
        "RightButton": "CycleLeft",
    }
    ANNOTS = {
        " ": ((128, 128, 128), 0),
        "🌳": ((10, 100, 10), 0),
        "🌿": ((100, 200, 100), 0),
        "⛺": ((255, 117, 24), 0)
    }
    TEXTS = {
        "Null": "",
        "Empty": " ",
        "Tree": "🌳",
        "Tent": "⛺",
        "Grass": "🌿",
        "Number0": "0", "Number1": "1",
        "Number2": "2", "Number3": "3",
        "Number4": "4", "Number5": "5",
        "Number6": "6", "Number7": "7",
        "Number8": "8", "Number9": "9",
    }

    # Inherited methods
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
        if self.finished():
            return "Puzzle solved"
        if not self._check_equity():
            return "# of tents != # of trees"
        elif not self._check_all_trees():
            return "Not all trees have a tent"
        elif not self._check_all_tents_adj_trees():
            return "Not all tents have a tree"
        elif not self._check_all_tents_vicinity():
            return "There are at least two tents close to each other"
        elif not self._check_row_constraints():
            return "Row constraints not satisfied"
        elif not self._check_col_constraints():
            return "Column constraints not satisfied"
        else:
            return "Huh?" # Not possible case

    # -- UTILITY METHODS --
    def _count_trees(self) -> int:
        """
        Restituisce il numero totale di alberi presenti nel tabellone
        """
        return self._board.count(1)

    def _count_tents(self) -> int:
        """
        Restituisce il numero totale di tende presenti nel tabellone
        """
        return self._board.count(2)


    def _cell_number(self, x: int, y: int) -> int:
        """
        Restituisce il numero così com'è che equivale allo state della cella passata come parametro.
        """
        if 0 <= x < self._w and 0 <= y < self._h: # Different from the method as it also includes row and column 0 (constraint column/row)
            return self._board[y * self._w + x]
        raise IndexError("Out of bounds")

    def _cell_state(self, x: int, y: int) -> str:
        """
        Restituisce lo stato della cella passata come parametro in forma di stringa, convertita dal corrispondente intero
        """
        number = self._cell_number(x, y)
        match number:
            case -1:
                return "Null"
            case 0:
                return "Empty"
            case 1:
                return "Tree"
            case 2:
                return "Tent"
            case 3:
                return "Grass"
            case num if 90 <= num <= 99:
                return "Number" + str(num-90)
            case _:
                raise ValueError(f"Invalid number: {number}")

    def _cell_text(self, state: str):
        if state in self.TEXTS:
            return self.TEXTS[state]
        raise ValueError(f"Invalid state: {state}")

    def _get_column(self, x: int) -> list[int]:
        col = []
        i = x
        for _ in range(self._h):
            col.append(self._board[i])
            i += self._w
        return col

    def _get_row(self, y: int) -> list[int]:
        row = []
        i = y * self._w
        for _ in range(self._w):
            row.append(self._board[i])
            i += 1
        return row

    # -- CHECK METHODS --
    def _check_equity(self) -> bool:
        """
        Verifica che il numero di tende sia uguale al numero di alberi
        """
        return self._count_trees() == self._count_tents()

    def _check_out_of_bounds(self, x: int, y: int) -> bool:
        return 1 <= x < self._w and 1 <= y < self._h # From 1 as column and row 0 are for the constraint numbers

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
                if (near_x, near_y) != (x, y) and self._check_out_of_bounds(x, y): # The central cell will not be checked
                    if self._cell_state(near_x, near_y) == state:
                        return True
        return False

    def _check_tree_adjacency(self, x: int, y: int) -> bool:
        if self._cell_state(x, y) != "Tree":
            raise ValueError("Not a tree")

        return self._check_if_is_adjacent(x, y, "Tent")

    def _check_all_trees(self) -> bool:
        for i in range(self._h):
            for j in range(self._w):
                if self._cell_state(i, j) == "Tree" and not self._check_tree_adjacency(i, j):
                    return False
        return True

    def _check_tent_adjacency(self, x: int, y: int) -> bool:
        if self._cell_state(x, y) != "Tent":
            raise ValueError("Not a tent")

        return self._check_if_is_adjacent(x, y, "Tree")

    def _check_tent_vicinity(self, x: int, y: int) -> bool:
        if self._cell_state(x, y) != "Tent":
            raise ValueError("Not a tent")
        return self._check_if_is_near(x, y, "Tent")

    def _check_all_tents_adj_trees(self) -> bool:
        for i in range(self._h):
            for j in range(self._w):
                if self._cell_state(i, j) == "Tent" and not self._check_tent_adjacency(i, j):
                    return False
        return True

    def _check_all_tents_vicinity(self) -> bool:
        for i in range(self._h):
            for j in range(self._w):
                if self._cell_state(i, j) == "Tent" and self._check_tent_vicinity(i, j):
                    return False
        return True

    def _check_row_constraints(self):
        for r in range(1, self._h): # First row is excluded because it's for constraints
            tent_number, *cells = [c for c in self._get_row(r)]
            tent_number -= 90 # Because numbers are set as 90 + the actual number
            if tent_number != cells.count(2):
                return False
        return True

    def _check_col_constraints(self):
        for c in range(1, self._w): # First column is excluded because it's for constraints
            tent_number, *cells = [r for r in self._get_column(c)]
            tent_number -= 90 # Because numbers are set as 90 + the actual number
            if tent_number != cells.count(2):
                return False
        return True


def tents_gui_play(game_instance: TentsGame):
    g2d.init_canvas((game_instance.cols() * W, game_instance.rows() * H + H))
    ui = BoardGameGui(game_instance, game_instance.ACTIONS, game_instance.ANNOTS)
    g2d.main_loop(ui.tick)

if __name__ == "__main__":
    game = TentsGame()
    tents_gui_play(game)