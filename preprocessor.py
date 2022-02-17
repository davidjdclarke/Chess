"""
The idea of this file is that it is going to act as a pre-processor for the chess game data stored in .pgn formatt.
This file will need to have tools to convert Algebraic chess notation into something that the chess engine can understand.
It should also have tools built in to save attributes of games and then filter them accordingly.
"""
import chess.pgn
from pgn_parser import pgn, parser
import io
import engine as ce
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
        self.Date = match[-8].strip('Date ').strip('"')
        self.Time = match[-7].strip('Time ').strip('"')
        self.WhiteClock = match[-6].strip('WhiteClock ').strip('"')
        self.BlackClock = match[-5].strip('BlackClock ').strip('"')
        self.ECO = match[-4].strip('ECO ').strip('"')
        self.PlayCount = match[-3].strip('PlayCount ').strip('"')
        self.Result = match[-2].strip('Result ').strip('"')
        self.Type = findBetween(match[-1], '{', '}')
        self.Moves = self.processGame(match[-1])
    
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


def getGames(pgn_file="./games/ficsgamesdb_search_199458.pgn"):
    # Open the pgn file as a string
    with open(pgn_file) as f:
        pgn = [line.rstrip('\n').strip(']').strip('[') for line in f]
    games = []
    for i, line in enumerate(pgn):
        if line[0:5] == "Event":
            games.append([line])
        elif line == "":
            pass
        else:
            games[-1].append(line)
    return [Game(games[i]) for i in range(len(games))]

def createGameLabel(game):
    pass

def get_possible_endings(games):
    endings = []
    for i, game in enumerate(games):
        ending = game.Type
        if ending not in endings:
            endings.append(ending)
    return endings

def get_first_words(string_array):
    first_words = []
    for i, words in enumerate(string_array):
        first_word = words.split(" ")[0]
        if first_word not in first_words:
            first_words.append(first_word)
    return first_words

if __name__ == "__main__":
    games = getGames()
    endings = get_possible_endings(games)
    first_word = get_first_words(endings)
    print("Hello World!")
    

