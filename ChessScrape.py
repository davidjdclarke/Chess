"""
Author: David Clarke
Date: July 15, 2021

Provide a set of tools to download pgn format chess games from the FCIS Games Database.

Part of the ChessNet ML Project...
"""
import requests
import json
import bz2
from time import sleep


class ChessDownloader:
    def __init__(self, base_url='http://www.ficsgames.org'):
        self.base_url = base_url

    def request_games(self, month, year):
        """
        Query the chess database for games from a given month and year

        Args:
            month -- int (1 - 12)
            year -- int
        Returns:
            r -- request
        """
        url = self.base_url + "/cgi-bin/download.cgi?download=Download&gametype=12&month=" + \
              str(month) +"&year=" + str(year) + "&movetimes=0"
        r = requests.post(url)
        return r

    def find_download_url(self, r):
        """
        Find the url to download the .png file as a .bz2 file

        Args:
            r -- request
        Returns
            url -- string
        """
        url = str(r.content).split("href=")[-1].split('">fics')[0][1:]
        return url

    def download_pgn(self, arg):
        """
        Download a set of pgn games

        Args:
            arg -- either string or request object
        Returns:
            data -- request
        """
        if type(arg) is not str:
            arg = self.find_download_url(arg)
        url = self.base_url + arg
        data = requests.get(url)
        return data

    def save_as_bz2(self, data, url='xxxxxxxxxxxx.pgn.bz2', file_path='./db/bz2/', file_name=None):
        """
        Save the bz2 data file

        Args:
            data -- request
            url -- string
            file_path -- string
            file_name -- string or None (optional)
        Return:
            None
        """
        if file_name is None:
            file_name = url[4:]
        try:
            with open(file_path + file_name, 'wb') as f:
                f.write(data.content)
        except:
            print("Error saving file: " + file_name)

    def save_as_pgn(self, data, url, file_path="./db/", file_name=None):
        """
        Save the bz2 data file as a decompressed .pgn file

        Saves the contents of the data request after extracting using the bz2 library.  The file is saved in the
        directory described by the 'file_path' variable, and with the file name described by the url passed.  The
        file extension is to be .pgn.

        Args:
            data -- request
            url -- string
            file_path -- string
            file_name -- string or None (optional)
        Return:
            None
        """
        if file_name is None:
            file_name = url[4:-4]
        try:
            with open(file_path + file_name, 'wb') as f:
                temp = bz2.decompress(data.content)
                f.write(temp)
                f.close()
        except:
            print("Error saving file: " + file_name)


def download_games():
    """
    Script to download games from chess.db.org

    Args:
        None
    Returns:
        None
    """
    obj = ChessDownloader()
    months = [None, 'Jan', 'Feb', 'Mar', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    for year in range(2021, 2022):
        for month in range(1, 4):
            x = obj.request_games(month, year)
            url = obj.find_download_url(x)
            data = obj.download_pgn(url)
            obj.save_as_pgn(data, url=url)
            print("Downloaded Games from: " + str(month) + ", " + str(year))


if __name__ == "__main__":
    download_games()
