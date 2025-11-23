import g2d
from boardgamegui import BoardGameGui
from boardgame import BoardGame

W, H = 40, 40

class TentsGame(BoardGame):
    def __init__(self, w: int = 5, h: int = 5):

        self._w, self._h = w, h

        self._board = [ # Tenda: 2, Albero: 1, Vuoto: 0
            0, 1, 0, 0, 0,
            0, 0, 0, 0, 1,
            0, 1, 0, 1, 0,
            0, 0, 0, 0, 1,
            0, 0, 0, 0, 0
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
        "Empty": " ",
        "Tree": "🌳",
        "Tent": "⛺",
        "Grass": "🌿",
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
        return self._check_equity() and self._check_all_trees() and self._check_all_tents()

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
        elif not self._check_all_tents():
            return "Not all tents have a tree"
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
        if self._check_out_of_bounds(x, y):
            return self._board[y * self._w + x]
        raise IndexError("Out of bounds")

    def _cell_state(self, x: int, y: int) -> str:
        """
        Restituisce lo stato della cella passata come parametro in forma di stringa, convertita dal corrispondente intero
        """
        number = self._cell_number(x, y)
        match number:
            case 0:
                return "Empty"
            case 1:
                return "Tree"
            case 2:
                return "Tent"
            case 3:
                return "Grass"
            case _:
                raise ValueError("Invalid number")

    def _cell_text(self, state: str):
        if state in self.TEXTS:
            return self.TEXTS[state]
        raise ValueError("Invalid state")

    # -- CHECK METHODS --
    def _check_equity(self) -> bool:
        """
        Verifica che il numero di tende sia uguale al numero di alberi
        """
        return self._count_trees() == self._count_tents()

    def _check_out_of_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self._w and 0 <= y < self._h

    def _check_tree_adjacency(self, x: int, y: int) -> bool:
        if self._cell_state(x, y) != "Tree":
            raise ValueError("Not a tree")

        for adj_x, adj_y in ((x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)):
            if self._check_out_of_bounds(adj_x, adj_y): # Se è fuori, siamo a bordo e si può ignorare
                if self._cell_state(adj_x, adj_y) == "Tent":
                    return True
        return False

    def _check_all_trees(self) -> bool:
        for i in range(self._h):
            for j in range(self._w):
                if self._cell_state(i, j) == "Tree" and not self._check_tree_adjacency(i, j):
                    return False
        return True

    def _check_tent_adjacency(self, x: int, y: int) -> bool:
        if self._cell_state(x, y) != "Tent":
            raise ValueError("Not a tent")

        for adj_x, adj_y in ((x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)):
            if self._check_out_of_bounds(adj_x, adj_y):  # Se è fuori, siamo a bordo e si può ignorare
                if self._cell_state(adj_x, adj_y) == "Tree":
                    return True
        return False

    def _check_all_tents(self) -> bool:
        for i in range(self._h):
            for j in range(self._w):
                if self._cell_state(i, j) == "Tent" and not self._check_tent_adjacency(i, j):
                    return False
        return True


def tents_gui_play(game_instance: TentsGame):
    g2d.init_canvas((game_instance.cols() * W, game_instance.rows() * H + H))
    ui = BoardGameGui(game_instance, game_instance.ACTIONS, game_instance.ANNOTS)
    g2d.main_loop(ui.tick)

if __name__ == "__main__":
    game = TentsGame()
    tents_gui_play(game)