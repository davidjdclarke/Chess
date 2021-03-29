"""
The idea of this file is that it is going to act as a pre-processor for the chess game data stored in .pgn formatt.
This file will need to have tools to convert Algebraic chess notation into something that the chess engine can understand.
It should also have tools built in to save attributes of games and then filter them accordingly.
"""
import chess.pgn
from pgn_parser import pgn, parser
import io
import ChessEngine as ce
import time

SQUARES = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6,
           'h': 7, '1': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7}


def findBetween(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""



class Game:
    def __init__(self, match):
        self.Event = match[0].strip('Event ').strip('"')
        self.Site = match[1].strip('Site ').strip('"')
        self.FICSGamesDBGameNo = match[2].strip('FICSGamesDBGameNo ').strip('"')
        self.White = match[3].strip('White ').strip('"')
        self.Black = match[4].strip('Black ').strip('"')
        self.WhiteElo = match[5].strip('WhiteElo ').strip('"')
        self.BlackElo = match[6].strip('BlackElo ').strip('"')
        self.WhiteIsComp = match[-12].strip('WhiteIsComp ').strip('"')
        self.TimeControl = match[-11].strip('TimeControl ').strip('"')
        self.Date = match[-10].strip('Date ').strip('"')
        self.Time = match[-9].strip('Time ').strip('"')
        self.WhiteClock = match[-8].strip('WhiteClock ').strip('"')
        self.BlackClock = match[-7].strip('BlackClock ').strip('"')
        self.ECO = match[-6].strip('ECO ').strip('"')
        self.PlayCount = match[-5].strip('PlayCount ').strip('"')
        self.Result = match[-4].strip('Result ').strip('"')
        self.Type = findBetween(match[-2], '{', '}')
        self.Moves = self.processGame(match[-2])
    
    def processGame(self, match):
        moves = self.getMovesFromString(match)
        return moves

    def getMovesFromString(self, match):
        moves = match.split('{')[0]
        moves = moves.split(' ')
        for i in range(len(moves)):
            if i >= len(moves):
                break
            if len(moves[i]) == 0:
                del moves[i]
            elif moves[i][-1] == '.':
                del moves[i]
        return moves

if __name__ == "__main__":
    with open("./games/ficsgamesdb_202101_standard2000_nomovetimes_196479.pgn") as f:
        pgn = [line.rstrip('\n').strip(']').strip('[') for line in f]

    games = []
    numLines = len(pgn)
    i = 0
    while i < numLines:
        gameOver = False
        j = 0
        game = []
        while not gameOver and i < numLines:
            game.append(pgn[i])
            if game[-1] == "":
                j += 1
            if j == 2:
                gameOver = True
            i += 1
        games.append(game)
    del games[-1]

    start = time.time()
    obj = []
    for i in range(len(games)):
        obj.append(Game(games[i]))
    end = time.time()
    print(str(end - start) + " seconds")
    x = 0
    

