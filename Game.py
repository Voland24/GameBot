from Player import Player
from AutoPlayer import AutoPlayer
from Board import Board

class Game:
    def __init__(self) -> None:
        self.turn = True # true - X playes next, false - O plays next
    
    def createBoard(self, noRows: int = 11, noColumns: int = 14, noWalls = 9):
        self.board = Board()
        self.board.init(noRows, noColumns, noWalls)
        return self
    
    def createPlayers(self, playerX: str = "real", playerO: str = "real"):
        if playerX not in ["real", "auto"] or playerO not in ["real", "auto"]:
            raise RuntimeError
        if playerX == "real":
            self.playerX = Player('X', self.board)
        else:
            self.playerX = AutoPlayer('X', self.board)
        if playerO == "real":
            self.playerO = Player('O', self.board)
        else:
            self.playerO = AutoPlayer('O', self.board)
        return self

    def play(self) -> None:
        winner = None
        self.board.displayBoard()
        while winner is None:
            if (self.turn):
                self.board = self.playerX.makeMove(self.board)
            else:
                self.board = self.playerO.makeMove(self.board)
            self.board.displayBoard()
            print(self.board.pathX1B1.keys())
            print(self.board.pathX1B2.keys())
            print(self.board.pathX2B1.keys())
            print(self.board.pathX2B2.keys())
            winner = self.board.gameOver()
            self.turn = not self.turn
        print(f"Player {winner} won!")