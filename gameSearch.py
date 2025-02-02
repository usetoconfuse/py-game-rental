"""
Game Search module - gameSearch.py

This module provides functions allowing a user to search for
games by title, genre or platform.

Functions:
- searchGames(column, item): Returns a list of lists, each 
list contains the game info and rental history of one game with
the matching item in title, genre or platform.
"""

# Last Updated: 12/12/2023

import database as db

# ----------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------

def searchGames(column, item):
    """
    This function returns the game info and rental info of all games
    with the given item in the given column.

    Parameters:
    string column: One of the following columns to search:
    'Title','Genre','Platform'
    string item: What to search for in the column.

    Returns:
    list: A list of all entries fitting the search request, including
    their complete rental history.
    None: If an error occurs during operation.
    """

    if column == "Platform":
        i = 1
    elif column == "Genre":
        i = 2
    elif column == "Title":
        i = 3

    gameData = db.GetDatabase("Game_Info.txt")

    # Get a list of info for all found entries
    gameList = []
    for entry in gameData:
        gameInfo = entry
        if not item.lower() in gameInfo[i].lower():
            continue # Ignore unmatching entries
        lastRent = db.GetEntry(entry[0])[-1][1]
        if lastRent == "":
            available = "Not available to rent"
        else:
            available = "Avaiable to rent"
        gameInfo.append(available)
        gameList.append(gameInfo)

    # Check that search returns entries
    if gameList == []:
        return

    return gameList

# ----------------------------------------------------------------------
# MAIN CODE
# ----------------------------------------------------------------------

if __name__ == "__main__":

    # Search for results using a vague keyword
    results = searchGames("Title","deep")
    for entry in results:
        print(entry[0])