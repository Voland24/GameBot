from Board import Board
from cprint import cprint

class Player:
    def __init__(self, role: str, board: Board) -> None:
        self.role = role # X or O
        self.board = board
    
    def makeMove(self, board: Board) -> Board:
        self.board = board
        newBoard = None
        while True:
            move = self.__generateMove()
            if move == None:
                cprint("Invalid move! Try again.", c='r')
                continue
            newBoard = self.board.applyMove(move)
            if newBoard is not None:
                self.board = newBoard
                break
            else:
                cprint("Invalid move! Try again.", c='r')
        return newBoard

    def __generateMove(self) -> dict:
        #implement strategy here
        print("Player " + self.role + " - enter your next move in the following form:\n\t<#pawn>|<x,y>|<green/blue>|<x,y>\n[Type 'exit' to exit the game]")
        inSeq = input()
        if inSeq == 'exit':
            exit()
        moveInput = inSeq.split('|')
        if len(moveInput) != 4 and len(moveInput) != 2:
            return None
        move = {}
        move['Player'] = (self.role + moveInput[0], Player.__positionToDecimal(moveInput[1]))
        remainingWalls = self.board.remainingWalls(self.role)
        if len(moveInput) == 4:
            if moveInput[2] != 'green' and moveInput[2] != 'blue':
                cprint("Invalid wall color!", c='r')
                return None
            if remainingWalls[moveInput[2]] == 0:
                cprint(f"No more {moveInput[2]} walls remaining!", c='r')
                return None
            move['Wall'] = (moveInput[2], Player.__positionToDecimal(moveInput[3]))
        elif remainingWalls['green'] > 0 or remainingWalls['blue'] > 0:
            return None
        return move
    
    @staticmethod
    def __positionToDecimal(pos: str) -> tuple:
        x, y = None, None
        coords = pos.split(',')
        if coords[0] in [chr(i+ord('0')) for i in range(1,10)]:
            x = int(coords[0])
        else:
            x = 10 + ord(coords[0]) - ord('A')
        if coords[1] in [chr(i+ord('0')) for i in range(1,10)]:
            y = int(coords[1])
        else:
            y = 10 + ord(coords[1]) - ord('A')
        return (x, y)