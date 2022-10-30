import time
from Player import Player, Board
from itertools import product
from random import randint

class AutoPlayer(Player):
    cnt = 0
    t = 0
    def __init__(self, role: str, board: Board) -> None:
        super().__init__(role, board)
        self.__initSingleMoveLookup()

    def makeMove(self, board: Board) -> Board:
        # implement strategy here
        print("Player " + self.role + " is pondering...")
        self.board = board
        AutoPlayer.cnt = 0
        start = time.time()
        remainingWalls = board.remainingWalls(self.role)
        if remainingWalls['blue'] + remainingWalls['green'] == 0:
            res = self.finalPlay(board, self.role)
        else:
            res =  self.__alphabeta_v2(board, 2, float('-inf'), float('inf'), True, True)[2]
            #res = self.__alphabeta(board, 2, float('-inf'), float('inf'), True)[1]
        print(time.time()-start)
        print(AutoPlayer.cnt, AutoPlayer.t)
        return res
    
    def finalPlay(self, board: Board, role: str):
        paths = [board.pathO1B1, board.pathO1B2, board.pathO2B1, board.pathO2B2] if role == 'O' else [board.pathX1B1, board.pathX1B2, board.pathX2B1, board.pathX2B2]
        max = 0
        for i in range(1,4):
            if len(paths[i]) < len(paths[max]):
                max = i
        spots = list(paths[max].keys())[-3:-1]
        move = (role + str(max // 2 + 1), spots[0])
        generated = board.pawnUpdate(move)
        if generated is not None:
            return generated
        return board.pawnUpdate((role + str(max // 2 + 1), spots[1]))
        
    def generatePossibleStates(self, board: Board = None, role: str = None) -> list:
        if board == None:
            board = self.board
        if role == None:
            role = self.role
        currPos = board.pX if role == 'X' else board.pO
        colors = self.__wallColorsLeft(board, role)
        for pawn in range(0,2):
            for newPos in map(lambda delta: (currPos[pawn][0]+delta[0], currPos[pawn][1]+delta[1]), self.pawnMoveLookup):
                for wall in AutoPlayer.__optimalWalls(board, role, 'blue' in colors, 'green' in colors):
                    move = {'Player': (role + str(pawn+1), newPos), 'Wall': wall}
                    generated = board.applyMove(move)
                    if generated is not None:
                        yield generated
                # moves = [{'Player': (role + str(pawn+1), newPos)}] if len(colors) == 0 else map(lambda other: {'Player': (role + str(pawn+1), newPos), 'Wall': (other[0], other[1])}, product(colors, self.wallMoveLookup))
                # for move in moves:
                #     if board.validMove(move):
                #         yield board.updateState(move)

    def generatePossibleStates_v2(self, board = None, role = None, pawnMove = True):
        if board == None:
            board = self.board
        if role == None:
            role = self.role
        if pawnMove:
            currPos = board.pX if role == 'X' else board.pO
            for pawn in range(0,2):
                for newPos in map(lambda delta: (currPos[pawn][0]+delta[0], currPos[pawn][1]+delta[1]), self.pawnMoveLookup):
                    move = (role + str(pawn+1), newPos)
                    generated = board.pawnUpdate(move)
                    if generated is not None:
                        yield generated
        else:
            colors = self.__wallColorsLeft(board, role)
            for move in AutoPlayer.__optimalWalls(board, role, 'blue' in colors, 'green' in colors):
                generated = board.wallUpdate(role, move)
                if generated is not None:
                    yield generated
        
    def __wallColorsLeft(self, board: Board, role: str) -> list:
        colors = []
        remainingWalls = board.remainingWalls(role)
        if remainingWalls['blue'] > 0:
            colors.append('blue')
        if remainingWalls['green'] > 0:
            colors.append('green')
        return colors

    @staticmethod
    def __optimalWalls(board:Board, role:str, blue:bool, green:bool):
        paths = [board.pathO1B1, board.pathO1B2, board.pathO2B1, board.pathO2B2] if role == 'X' else [board.pathX1B1, board.pathX1B2, board.pathX2B1, board.pathX2B2]
        moves = set()
        for path in paths:
            for spot in path:
                next = path[spot]
                if next is None:
                    continue
                if next[0] == spot[0] and green:
                    lefter = next if next[1] < spot[1] else spot
                    moves.add(('green', lefter))
                    moves.add(('green', (lefter[0]-1, lefter[1])))
                elif next[1] == spot[1] and blue:
                    upper = next if next[0] < spot[0] else spot
                    moves.add(('blue', upper))
                    moves.add(('blue', (upper[0], upper[1]-1)))
        return moves 
                    
                
    def __initSingleMoveLookup(self):
        self.pawnMoveLookup = list(filter(lambda tup: 1 <= abs(tup[0]) + abs(tup[1]) <= 2, product(range(-2,3),range(-2,3))))
        #self.wallMoveLookup = list(product(range(1,self.board.height), range(1, self.board.width)))

    def __heuristic(self, state: Board) -> float:
        # TODO
        start = time.time()
        w1, w2, w3, w4 = 10000, 100, 1, 0.01
        coordsX = (min(len(state.pathX1B1), len(state.pathX1B2)), min(len(state.pathX2B1), len(state.pathX2B2)))
        coordsO = (min(len(state.pathO1B1), len(state.pathO1B2)), min(len(state.pathO2B1), len(state.pathO2B2)))
        minX = min(coordsX[0], coordsX[1])
        minO = min(coordsO[0], coordsO[1])
        wallsRem = 4*state.wallCount - len(state.walls['green']) - len(state.walls['blue'])
        manhX, manhO = 0, 0
        for i in range(2):
            for j in range(2):
                manhX += Board.manhattan(state.pX[i], state.oBase[j])
                manhO += Board.manhattan(state.pO[i], state.xBase[j])
        
        badnessX = w1*(coordsX[0] + coordsX[1])/2 + w2*max(coordsX[0], coordsX[1]) + w4*manhX
        badnessO = w1*(coordsO[0] + coordsO[1])/2 + w2*max(coordsO[0], coordsO[1]) + w4*manhO
        badnessO += (w3*minX if minX > 6 and wallsRem > 12 else w1*minX)
        badnessX += (w3*minO if minO > 6 and wallsRem > 12 else w1*minO)
        AutoPlayer.t += time.time()-start
        return badnessO - badnessX if self.role == 'X' else badnessX - badnessO

    def __alphabeta(self, state: Board, depth: int, alpha:float, beta:float, maxPlayer: bool):
        if depth == 0 or state.gameOver():
            AutoPlayer.cnt+=1
            return self.__heuristic(state), state
        bestState = None
        if maxPlayer:
            maxScore = float('-inf')
            for s in self.generatePossibleStates(state, self.role):
                currScore = self.__alphabeta(s, depth-1, alpha, beta, False)[0] # smallest score possible
                if currScore > maxScore: # if still bigger than biggest so far
                    maxScore = currScore
                    bestState = s
                if maxScore >= beta: #if equal or bigger than what min can guarentee to achieve, quit
                    break
                alpha = max(alpha, maxScore)
            return maxScore, bestState
        else:
            minScore = float('inf')
            for s in self.generatePossibleStates(state, 'X' if self.role == 'O' else 'O'):
                currScore = self.__alphabeta(s, depth-1, alpha, beta, True)[0] # biggest score possible
                if currScore < minScore: # if still smaller than smallest so far
                    minScore = currScore
                    bestState = s
                if minScore <= alpha: # if equal or smaller than what max can guarantee to achieve, quit
                    break
                beta = min(beta, minScore)
            return minScore, bestState

    def __alphabeta_v2(self, state: Board, depth: int, alpha: float, beta:float, maxPlayer: bool, pawnMove: bool, comparisonScore = None):
        winner = state.gameOver()
        if winner is not None:
            return float('inf') if winner == self.role else float('-inf'), 0, state
        if len(state.walls['green']) == 2*state.wallCount and len(state.walls['blue']) == 2*state.wallCount:
            minX = min(len(state.pathX1B1), len(state.pathX1B2), len(state.pathX2B1), len(state.pathX2B2))
            minO = min(len(state.pathO1B1), len(state.pathO1B2), len(state.pathO2B1), len(state.pathO2B2))
            if minX < minO:
                return float('inf'),0,state if self.role == 'X' else float('-inf'),0,state
            elif minX > minO:
                if self.role == 'O':
                    return float('inf'),0,state
                else:
                    return float('-inf'),0,state
                #return float('inf'),0,state if self.role == 'O' else float('-inf'),0,state
            else:
                return (float('inf'),0,state) if maxPlayer else (float('-inf'),0,state)
        if depth == 0:
            return self.__heuristic(state), 0, state
        bestState = None
        if maxPlayer:
            maxScore = float('-inf')
            if pawnMove:
                comparisonScore = None
                remainingWalls = state.remainingWalls(self.role)
                for s in self.generatePossibleStates_v2(state, self.role, pawnMove=True):
                    currState, currScore = s, 0
                    if remainingWalls['blue'] + remainingWalls['green'] > 0:
                        currScore, aux, currState = self.__alphabeta_v2(s, depth, alpha, beta, True, False, comparisonScore)
                        if comparisonScore is None:
                            comparisonScore = aux
                            bestState = currState
                        if aux > comparisonScore:
                            comparisonScore = aux
                    else:
                        currScore = self.__alphabeta_v2(s, depth-1, alpha, beta, False, True)[0]
                    if currScore > maxScore:
                        maxScore = currScore
                        bestState = currState
                        if maxScore == float('inf'): # win
                            break
                    if maxScore >= beta:
                        break
                    alpha = max(alpha, maxScore)
                return maxScore, 0, bestState
            else:
                first = True
                for s in self.generatePossibleStates_v2(state, self.role, pawnMove=False):
                    #AutoPlayer.cnt +=1
                    currScore = self.__alphabeta_v2(s, depth-1, alpha, beta, False, True)[0]
                    if first:
                        bestState = s
                        if comparisonScore is None or currScore > comparisonScore:
                            comparisonScore = currScore
                        elif currScore < comparisonScore:
                            break
                        first = False
                    if currScore > maxScore:
                        maxScore = currScore
                        bestState = s
                    if maxScore >= beta:
                        break
                    alpha = max(alpha, maxScore)
                return maxScore, comparisonScore, bestState
        else:
            minScore = float('inf')
            if pawnMove:
                comparisonScore = None
                remainingWalls = state.remainingWalls('X' if self.role == 'O' else 'O')
                for s in self.generatePossibleStates_v2(state, 'X' if self.role == 'O' else 'O', pawnMove=True):
                    currState, currScore = s, 0
                    if remainingWalls['blue'] + remainingWalls['green'] > 0:
                        currScore, aux, currState = self.__alphabeta_v2(s, depth, alpha, beta, False, False, comparisonScore)
                        if comparisonScore is None:
                            comparisonScore = aux
                            bestState = currState
                        if aux < comparisonScore:
                            comparisonScore = aux
                    else:
                        currScore = self.__alphabeta_v2(s, depth-1, alpha, beta, True, True)[0]
                    if currScore < minScore:
                        minScore = currScore
                        bestState = currState
                        if minScore == float('-inf'): # win
                            break
                    if minScore <= alpha:
                        break
                    beta = min(beta, minScore)
                return minScore, 0, bestState
            else:
                first = True
                for s in self.generatePossibleStates_v2(state, 'X' if self.role == 'O' else 'O', pawnMove=False):
                    currScore = self.__alphabeta_v2(s, depth-1, alpha, beta, True, True)[0]
                    if first:
                        bestState = s
                        if comparisonScore is None or currScore < comparisonScore:
                            comparisonScore = currScore
                        elif currScore > comparisonScore:
                            break
                        first = False
                    if currScore < minScore:
                        minScore = currScore
                        bestState = s
                    if minScore <= alpha:
                        break
                    beta = min(beta, minScore)
                return minScore, comparisonScore, bestState