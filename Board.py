from inspect import getargspec
from itertools import product
from cprint import cprint
from copy import copy
from queue import PriorityQueue
class Board:
    valIndex = None
    def __init__(self, original = None) -> None:
        if original is None:
            return
        self.height = original.height
        self.width = original.width
        self.pX = []
        self.pX.append(copy(original.pX[0]))
        self.pX.append(copy(original.pX[1]))
        self.pO = []
        self.pO.append(copy(original.pO[0]))
        self.pO.append(copy(original.pO[1]))
        self.xBase = copy(original.xBase)
        self.oBase = copy(original.oBase)
        self.walls = {'blue': [], 'green': []}
        self.walls['blue'] = copy(original.walls['blue'])
        self.walls['green'] = copy(original.walls['green'])
        self.wallCount = original.wallCount
        self.xRemainingWalls = {'blue': original.xRemainingWalls['blue'], 'green': original.xRemainingWalls['green']}
        self.pathX1B1 = copy(original.pathX1B1)
        self.pathX1B2 = copy(original.pathX1B2)
        self.pathX2B1 = copy(original.pathX2B1)
        self.pathX2B2 = copy(original.pathX2B2)
        self.pathO1B1 = copy(original.pathO1B1)
        self.pathO1B2 = copy(original.pathO1B2)
        self.pathO2B1 = copy(original.pathO2B1)
        self.pathO2B2 = copy(original.pathO2B2)
        
    def init(self, rowNo, columnNo, wallNo) -> None:
        self.height = rowNo # dimens
        self.width = columnNo
        wOffset, hOffset = (self.width-2)//4, (self.height-2)//3 # auxilary variables
        self.pX = [(1+hOffset, 1+wOffset), (self.height - hOffset, 1+wOffset)] # initial positions
        self.pO = [(1+hOffset, self.width - wOffset), ( self.height - hOffset, self.width - wOffset)]
        self.xBase = list(self.pX)
        self.oBase = list(self.pO)
        self.walls = {}
        self.walls['green'] = []
        self.walls['blue'] = []
        if Board.valIndex == None:
            Board.__initValidationIndex()
        self.__initPaths()
        self.wallCount = wallNo
        self.xRemainingWalls = { 'green': wallNo, 'blue': wallNo} # for player X

    def applyMove(self, move: dict): # move = { 'Player': ('X1', (x,y)), 'Wall': ('green', (x,y))}
        newBoard = self.pawnUpdate(move['Player'])
        if newBoard is None:
            return None
        if 'Wall' not in move:
            return newBoard
        newBoard = newBoard.wallUpdate(move['Player'][0][0], move['Wall'])
        if newBoard is None:
            return None
        return newBoard

    def pawnUpdate(self, move: tuple):
        newBoard = Board(self)
        if not newBoard.validPawnMove(move):
            return None
        ind = int(move[0][1])-1
        if move[0][0] == 'X':
            newBoard.pX[ind] = move[1]
            newBoard.__updatePath(newBoard.pathX1B1 if ind == 0 else newBoard.pathX2B1, move[1])
            newBoard.__updatePath(newBoard.pathX1B2 if ind == 0 else newBoard.pathX2B2, move[1])
        else:
            newBoard.pO[ind] = move[1]
            newBoard.__updatePath(newBoard.pathO1B1 if ind == 0 else newBoard.pathO2B1, move[1])
            newBoard.__updatePath(newBoard.pathO1B2 if ind == 0 else newBoard.pathO2B2, move[1])
        return newBoard

    def wallUpdate(self, role:str, move: tuple):
        newBoard = Board(self)
        if not newBoard.validWallMove(move):
            return None
        newBoard.walls[move[0]].append(move[1])
        if role == 'X':
            newBoard.xRemainingWalls[move[0]] -= 1
        return newBoard

    def validMove(self, move: dict) -> bool:
        if not self.validPawnMove(move['Player']):
            return False
        if move.get('Wall') != None and not self.validWallMove(move['Wall']):
            return False
        return True
    
    def validPawnMove(self, pawnMove: tuple) -> bool:
        nextPos = pawnMove[1]
        if self.__outOfBounds(nextPos):
            return False # out of bounds
        currPos = None
        if pawnMove[0][0] == 'X':
            currPos = self.pX[int(pawnMove[0][1])-1]
        else:
            currPos = self.pO[int(pawnMove[0][1])-1]
        delta = tuple(map(lambda x, y: x-y, nextPos, currPos))
        if delta == (0,0):
            return False
        if abs(delta[0]) + abs(delta[1]) > 2:
            return False # out of reach
        if not self.__valIndexLookup(currPos, nextPos):
            return False # walls preventing
        if abs(delta[0]) + abs(delta[1]) == 1:
            if nextPos in (self.oBase if pawnMove[0][0] == 'X' else self.xBase):
                return True
            testPos = tuple(map(lambda x, y: x+2*y, currPos, delta))
            if not self.__valIndexLookup(currPos, testPos) or testPos not in self.pX and testPos not in self.pO:
                return False
        return True

    def validWallMove(self, wallMove: tuple) -> bool:
        if (wallMove[1][0] < 1 or wallMove[1][0]) >= self.height or wallMove[1][1] < 1 or wallMove[1][1] >= self.width:
            return False
        if wallMove[1] in self.walls['green'] or wallMove[1] in self.walls['blue']:
            return False
        if wallMove[0] == 'green':
            if (wallMove[1][0]+1, wallMove[1][1]) in self.walls['green'] or (wallMove[1][0]-1, wallMove[1][1]) in self.walls['green']:
                return False
        else:
            if (wallMove[1][0], wallMove[1][1]+1) in self.walls['blue'] or (wallMove[1][0], wallMove[1][1]-1) in self.walls['blue']:
                return False
        self.walls[wallMove[0]].append(wallMove[1])
        exist = self.__existPaths(wallMove)
        self.walls[wallMove[0]].remove(wallMove[1])
        return exist

    def __wallTouching(self, wallMove: tuple):
        pos = wallMove[1]
        cnt = 0
        blueTouch = greenTouch = None
        if wallMove[0] == 'green':
            greenTouch = [(pos[0]-2, pos[1]), (pos[0]+2, pos[1])]
            blueTouch = [(pos[0]-1, pos[1]-1), (pos[0]-1, pos[1]), (pos[0]-1, pos[1]+1), (pos[0], pos[1]-1), (pos[0], pos[1]+1), (pos[0]+1, pos[1]-1), (pos[0]+1, pos[1]), (pos[0]+1, pos[1]+1)]
            if pos[0] == 1 or pos[0] == self.height-1:
                if cnt==1:
                    return True
                else:
                    cnt+=1
        else:
            blueTouch = [(pos[0], pos[1]-2), (pos[0], pos[1]+2)]
            greenTouch = [(pos[0]-1, pos[1]-1), (pos[0], pos[1]-1), (pos[0]+1, pos[1]-1), (pos[0]-1, pos[1]), (pos[0]+1, pos[1]), (pos[0]-1, pos[1]+1), (pos[0], pos[1]+1), (pos[0]+1, pos[1]+1)]
            if pos[0] == 1 or pos[0] == self.width-1:
                if cnt==1:
                    return True
                else:
                    cnt+=1
        for touch in greenTouch:
            if touch in self.walls['green']:
                cnt+=1
                if cnt == 2:
                    return True
        for touch in blueTouch:
            if touch in self.walls['blue']:
                cnt+=1
                if cnt == 2:
                    return True
        return False  

    def __valIndexLookup(self, currPos: tuple, targetPos: tuple):
        delta = (targetPos[0]-currPos[0], targetPos[1]-currPos[1])    #tuple(map(lambda x, y: x-y, targetPos, currPos))
        if (delta[0] == 0 or delta[1] == 0):
            for wall in self.valIndex[delta]:
                if (currPos[0]+wall[1], currPos[1]+wall[2]) in self.walls[wall[0]]:
                    return False
            return True
        elif abs(delta[0]) == 1 or abs(delta[1]) == 1:
            midPos = (currPos[0], targetPos[1])
            if (self.__valIndexLookup(currPos, midPos) and self.__valIndexLookup(midPos, targetPos)):
                return True
            else:
                midPos = (targetPos[0], currPos[1])
                return self.__valIndexLookup(currPos, midPos) and self.__valIndexLookup(midPos, targetPos)
        else:
            return False

    def __existPaths(self, wallMove: tuple):
        x1b1, x2b2, x1b2, x2b1 = self.__pathIntersection(self.pathX1B1, wallMove), self.__pathIntersection(self.pathX2B2, wallMove), self.__pathIntersection(self.pathX1B2, wallMove), self.__pathIntersection(self.pathX2B1, wallMove)
        o1b1, o2b2, o1b2, o2b1 = self.__pathIntersection(self.pathO1B1, wallMove), self.__pathIntersection(self.pathO2B2, wallMove), self.__pathIntersection(self.pathO1B2, wallMove), self.__pathIntersection(self.pathO2B1, wallMove)
        return x1b1 and x2b1 and x1b2 and x2b2 and o1b1 and o2b2 and o1b2 and o2b1
        
    def __pathIntersection(self, path, wallMove) -> bool:
        wall = wallMove[1]
        color = wallMove[0]
        if color == 'blue':
            if (wall not in path or (wall[0]+1,wall[1]) not in path) and ((wall[0], wall[1]+1) not in path or (wall[0]+1, wall[1]+1) not in path):
                return True
        elif color == 'green':
            if (wall not in path or (wall[0],wall[1]+1) not in path) and ((wall[0]+1, wall[1]) not in path or (wall[0]+1, wall[1]+1) not in path):
                return True
        else:
            raise RuntimeError
        return self.__assignPath(path)
            
    def __assignPath(self, oldPath) -> bool:
        if oldPath == self.pathX1B1:
            path = self.findPath(self.pX[0], self.oBase[0])
            if path is None:
                return False
            else:
                self.pathX1B1 = path
                return True
        elif oldPath == self.pathX2B2:
            path = self.findPath(self.pX[1], self.oBase[1])
            if path is None:
                return False
            else:
                self.pathX2B2 = path
                return True
        elif oldPath == self.pathX1B2:
            path = self.findPath(self.pX[0], self.oBase[1])
            if path is None:
                return False
            else:
                self.pathX1B2 = path
                return True
        elif oldPath == self.pathX2B1:
            path = self.findPath(self.pX[1], self.oBase[0])
            if path is None:
                return False
            else:
                self.pathX2B1 = path
                return True
        elif oldPath == self.pathO1B1:
            path = self.findPath(self.pO[0], self.xBase[0])
            if path is None:
                return False
            else:
                self.pathO1B1 = path
                return True
        elif oldPath == self.pathO2B2:
            path = self.findPath(self.pO[1], self.xBase[1])
            if path is None:
                return False
            else:
                self.pathO2B2 = path
                return True
        elif oldPath == self.pathO1B2:
            path = self.findPath(self.pO[0], self.xBase[1])
            if path is None:
                return False
            else:
                self.pathO1B2 = path
                return True
        elif oldPath == self.pathO2B1:
            path = self.findPath(self.pO[1], self.xBase[0])
            if path is None:
                return False
            else:
                self.pathO2B1 = path
                return True
                
    def findPath(self, startSpot, endSpot) -> dict:
        previous = dict()
        processed = set()
        heap = PriorityQueue()
        gscores = {}
        heap.put((Board.manhattan(startSpot, endSpot), startSpot))
        gscores[startSpot] = 0
        previous[startSpot] = None
        found = False
        while not heap.empty():
            currSpot = heap.get()[1]
            processed.add(currSpot)
            if currSpot == endSpot:
                found = True
                break
            for nextSpot in self.__neighboors(currSpot):
                if nextSpot in processed:
                    continue
                if nextSpot not in gscores or gscores[nextSpot] > gscores[currSpot] + 1:
                    gscores[nextSpot] = gscores[currSpot] + 1
                    heap.put((Board.manhattan(nextSpot, endSpot) + gscores[nextSpot], nextSpot))
                    previous[nextSpot] = currSpot

        if not found:
            return None
        path = dict()
        spot = endSpot
        while True:
            path[spot] = previous[spot]
            spot = path[spot]
            if spot is None:
                break
        return path
    
    def __initPaths(self):
        self.pathX1B1 = self.findPath(self.pX[0], self.oBase[0])
        self.pathX1B2 = self.findPath(self.pX[0], self.oBase[1])
        self.pathX2B1 = self.findPath(self.pX[1], self.oBase[0])
        self.pathX2B2 = self.findPath(self.pX[1], self.oBase[1])
        self.pathO1B1 = self.findPath(self.pO[0], self.xBase[0])
        self.pathO1B2 = self.findPath(self.pO[0], self.xBase[1])
        self.pathO2B1 = self.findPath(self.pO[1], self.xBase[0])
        self.pathO2B2 = self.findPath(self.pO[1], self.xBase[1])

    def __updatePath(self, path: dict, spot: tuple):
        if spot in path: # move along the established path
            curr = path[spot]
            while curr is not None:
                curr = path.pop(curr)
            path[spot] = None
        else:
            # fields = list(path.keys())
            # if Board.manhattan(fields[0], fields[-1]) < Board.manhattan(fields[0], spot):
            #     first = fields[-1]
            #     dif = (spot[0]-first[0], spot[1]-first[1])
            #     if abs(dif[0]) + abs(dif[1]) == 1: # one-move
            #         path[first] = spot
            #         path[spot] = None
            #     elif abs(dif[0]) == abs(dif[1]): # diagonal two-move
            #         mid = (first[0], spot[1])
            #         if not self.__valIndexLookup(first, mid) or not self.__valIndexLookup(mid, spot):
            #             mid = (spot[0], first[1])
            #         if mid in path:
            #             path.pop(first)
            #         else:
            #             path[first] = mid
            #         path[mid] = spot
            #         path[spot] = None
            #     else: # straight two-move
            #         mid = (first[0]+dif[0]/2, first[1]+dif[1]/2)
            #         path[first] = mid
            #         path[mid] = spot
            #         path[spot] = None
            # else:
            self.__assignPath(path)
            
    def __neighboors(self, currSpot):
        neighboors = [(currSpot[0]-1, currSpot[1]), (currSpot[0]+1, currSpot[1]), (currSpot[0], currSpot[1]-1), (currSpot[0], currSpot[1]+1)]
        return [n for n in neighboors if not self.__outOfBounds(n) and self.__valIndexLookup(currSpot, n)]

    def __outOfBounds(self, pos: tuple) -> bool:
        return pos[0] < 1 or pos[0] > self.height or pos[1] < 1 or pos[1] > self.width

    @staticmethod
    def manhattan(begin, end) -> int:
        return abs(begin[0] - end[0]) + abs(begin[1] - end[1])

    def __initValidationIndex():
        Board.valIndex = {}
        # straight 1
        Board.valIndex[(-1,0)] = [('blue',-1,-1), ('blue',-1,0)]
        Board.valIndex[(1,0)] = [('blue',0,-1), ('blue',0,0)]
        Board.valIndex[(0,-1)] = [('green',-1,-1), ('green',0,-1)]
        Board.valIndex[(0,1)] = [('green',-1,0), ('green',0,0)]
        # straight 2
        Board.valIndex[(-2,0)] = Board.valIndex[(-1,0)] + [('blue',-2,-1), ('blue',-2,0)]
        Board.valIndex[(2,0)] = Board.valIndex[(1,0)] + [('blue',1,-1), ('blue',1,0)]
        Board.valIndex[(0,-2)] = Board.valIndex[(0,-1)] + [('green',-1,-2), ('green',0,-2)]
        Board.valIndex[(0,2)] = Board.valIndex[(0,1)] + [('green',-1,1), ('green',0,1)]
    
    def remainingWalls(self, role: str) -> dict:
        if role == 'X':
            return self.xRemainingWalls
        elif role == 'O':
            return {'blue': 2 * self.wallCount - len(self.walls['blue']) - self.xRemainingWalls['blue'], 'green': 2 * self.wallCount - len(self.walls['green']) - self.xRemainingWalls['green']}
        else:
            raise RuntimeError

    def gameOver(self) -> str:
        if self.pX[0] in self.oBase or self.pX[1] in self.oBase:
            return 'X'
        if self.pO[0] in self.xBase or self.pO[1] in self.xBase:
            return 'O'
        return None
    
    def displayBoard(self) -> None:
        # display board here
        for i in range(1, self.width+1):
            print('  ' + (chr(ord('0')+i) if i < 10 else chr(ord('A')+i-10)), end=' ') # column indices
        print()
        for i in range(1, self.height+1):
            print(chr(ord('0')+i) if i < 10 else chr(ord('A')+i-10), end='') # row index
            for j in range(1, self.width+1): # cells and vertical walls
                if  (i, j) in self.pX:
                    cprint(' X ', c='y', end='')
                elif (i,j) in self.pO:
                    cprint(' O ', c='r', end='')
                elif (i,j) in self.xBase:
                    cprint(' B ', c='y',end='')
                elif (i,j) in self.oBase:
                    cprint(' B ', c='r',end='')
                else:
                    print('   ', end='')
                if (j == self.width):
                    print()
                elif (i, j) in self.walls['green'] or (i-1,j) in self.walls['green']:
                    cprint('\u2016', c='g', end='')
                else:
                    print('|',end='')
            for j in range(1,self.width+1): # horizontal walls
                if (i,j) in self.walls['blue'] or (i,j-1) in self.walls['blue']:
                    cprint(' ===', c='b', end='')
                else:
                    print(' ---', end='')
            print()
        print('Walls remaining:')
        walls = self.remainingWalls(role='X')
        print(str('X : green - {green}, blue : {blue}').format(green=walls['green'], blue=walls['blue']))
        walls = self.remainingWalls(role='O')
        print(str('O : green - {green}, blue : {blue}').format(green=walls['green'], blue=walls['blue']))
        return