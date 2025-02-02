"""
Inventory Pruning module - inventoryPruning.py

This module contains functions that determine which games are
unpopular based on feedback criteria.

Functions:
- GetAverages(): Calculates the average number of times rented,
number of reviews and average review score across all games.
- FindUnpopular(averages): Calculates which games are 'unpopular' by
comparing to averages and returns a list of their IDs.
- UnpopularInfo(unpopularGames, averages): Gives a list of
advice on whether to remove an unpopular game based on
the game's stats.
- DrawBarChart(gameID, gameInfo, averages): Displays
a bar chart of the game's stats against the average stats.
- PruneGame(gameID, deleteRental): Deletes a copy of a game from
the database and optionally also deletes its rental history.
"""

# Last Updated: 12/12/2023

import database as db
import feedbackManager as fm
from datetime import date
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------

def GetAverages():
    """
    Calculates the average number of times rented, number of reviews
    and review score across all games.

    Parameters:
    None

    Returns:
    tuple: a 3-ary tuple containing the average number of rents,
    average number of reviews and average review score.
    """

    statsDict = {}
    avgList = [0,0,0]

    # Populate dictionary of stats for each game
    gameData = db.GetDatabase("Game_Info.txt")
    for game in gameData:
        statsDict.update({game[0] : [0,0,0]})
    
    # Count the number of times each game has been rented
    rentalData = db.GetDatabase("Rental.txt")
    for rental in rentalData:
        id = rental[0]
        if id not in statsDict.keys():
            continue
        statsDict[id][0] += 1

    # Count the number of reviews for each game
    # and calculate average review score for each game
    feedbackData = fm.load_feedback()
    for review in feedbackData:
        id = review["GameID"]
        if id not in statsDict.keys():
            continue
        if id == "GameID":
            continue
        statsDict[id][1] += 1
        statsDict[id][2] += review["Rating"] # Add score for mean

    total = 0
    nonZeroTotal = 0 # Total number of games that have reviews
    for s in statsDict:
        # Divide total score by number of reviews to find average score
        if statsDict[s][1] == 0:
            statsDict[s][2] = 0
        else:
            statsDict[s][2] = statsDict[s][2] / statsDict[s][1]

        # Add up the totals for number of rents and reviews, and review score
        for i in range(0,3):
            avgList[i] += statsDict[s][i]

        total += 1
        if statsDict[s][1] != 0:
            nonZeroTotal += 1

    # Divide each value by the number of entries in the dictionary
    avgList[0] = avgList[0] / total
    avgList[1] = avgList[1] / total
    avgList[2] = avgList[2] / nonZeroTotal

    avgTuple = (avgList[0],avgList[1],avgList[2])
    return avgTuple

# ----------------------------------------------------------------------

def FindUnpopular(averages):
    """
    This function determines which games are unpopular based on their
    average score and how long it has been since the game has been rented.

    Parameters:
    tuple averages: A 3-ary tuple containing average stats across
    games, as returned by GetAverages().

    Returns:
    dict: A dictionary of IDs as keys and then a sub-dictionary
    containing number of reviews, average review score and
    number of times rented for unpopular games.
    """

    unpopularGames = {}

    avgRents, _, avgScore = averages # average review number is not used here

    gameData = db.GetDatabase("Game_Info.txt")
    feedbackData = fm.load_feedback()
    for entry in gameData:
        id = entry[0]
        if id == "GameID":
            continue
        score = 0

        # Add score for low ratings
        revs = 0
        avgGameScore = 0.0
        for entry in feedbackData:
            if entry["GameID"] == id:
                revs += 1
                avgGameScore += entry["Rating"]
        if revs == 0:
            avgGameScore = 0.0
        else:
            avgGameScore = avgGameScore / revs

        if avgGameScore == 0:
            None # Don't add score for unreviewed games
        elif avgGameScore <= avgScore - 2:
            score += 2
        elif avgGameScore < avgScore:
            score += 1

        # Add score based on rental history
        gameInfo = db.GetEntry(id)
        rents = len(gameInfo) - 1
        # Don't add if game has never been rented as it's probably new
        if rents == 0:
            None
        elif rents < avgRents:
            score += 1
        lastRental = gameInfo[-1]
        dateList = lastRental[1].split("-")
        if dateList == [""]:
            daysSinceRented = 0
        elif rents == 0:
            daysSinceRented = "N/A"
        elif rents > 0:
            for i in range(0,3):
                dateList[i] = int(dateList[i])
            lastReturnDate = date(*dateList)
            daysSinceRented = (date.today() - lastReturnDate).days

            # Add score if game hasn't been rented in 30 or 14 days
            if daysSinceRented > 30:
                score += 2
            elif daysSinceRented > 14:
                score += 1

        # Get days since purchased
        dateStr = gameInfo[0][5]
        dateList = dateStr.split("-")
        for i in range(0,3):
            dateList[i] = int(dateList[i])
        purchaseDate = date(*dateList)
        daysOwned = (date.today() - purchaseDate).days

        # Add games with high score to the list of unpopular games
        if score >= 2:
            unpopularGames.update({id : {"Reviews":revs,
                                  "Avg. Score":avgGameScore,
                                  "Rents":rents,
                                  "Last Rent" : daysSinceRented,
                                  "Purchased" : daysOwned}})

    return unpopularGames      

# ----------------------------------------------------------------------

def UnpopularInfo(unpopularGames, averages):
    """
    Provides notes on unpopular games in order to help
    a user decide whether to remove a game or not.

    Parameters:
    unpopularGames: dictionary of unpopular games as retrieved from
    FindUnpopular().
    tuple averages: A tuple containing averages across games as
    returned by GetAverages().

    Returns:
    dict: Dictionary containing the game ID and a string of suggestions
    related to that game.
    """

    suggestions = {}

    _, avgRevs, avgScore = averages

    for gameCopy in unpopularGames:
        id = gameCopy
        info = unpopularGames[id]

        # Get days since purchased
        daysOwned = info["Purchased"]

        suggStr = ""

        rentInterval = info["Purchased"] / info["Rents"]

        # Warn based on how many times game has been rented.
        if rentInterval <= 14:
            suggStr = suggStr + f"Game is rented often, average every "
            suggStr = suggStr + f"{rentInterval:.1f} days: demand is high, "
            suggStr = suggStr + "removal not advised.\n"
        elif rentInterval > 30:
            suggStr = suggStr + "Game is not rented often, average every "
            suggStr = suggStr + f"{rentInterval:.1f} days: demand is low.\n"

        # Warn if fewer than average reviews have been left
        if info["Reviews"] < avgRevs - 1:
            suggStr = suggStr + "Game has not many reviews: average score "
            suggStr = suggStr + "may be an inaccurate representation.\n"
        else:
            # Advise based on average score
            if info["Avg. Score"] >= avgScore + 1:
                suggStr = suggStr + "Game has a good average score: "
                suggStr = suggStr + "removal not advised.\n"
            elif info["Avg. Score"] <= avgScore - 1:
                suggStr = suggStr + "Game has a below average score: "
                suggStr = suggStr + "removal advised.\n"

        # Warn if game has been owned for less than 30 days
        if daysOwned < 30:
            suggStr = suggStr + "Store has owned game for less than 30 days: "
            suggStr = suggStr + "allow more time for rentals."
        else:
            suggStr = suggStr + "Store has owned game for more than 30 days: "
            suggStr = suggStr + "if demand is low, consider removal."

        suggestions.update({id : suggStr})
    return suggestions

# ----------------------------------------------------------------------

def DrawBarChart(gameID, gameInfo, averages):
    """
    Displays a bar chart of game stats against average stats for
    number of times rented, number of times reviewed and
    average review score.

    Parameters:
    string gameID: The ID of the game to display a chart for.
    tuple averages: A 3-ary tuple containing the average
    dict gameInfo: A dictionary of game stats, i.e. a value
    from any key-value pair in the dictionary returned by
    UnpopularInfo().
    number of times rented, number of reviews and review score
    across games, as returned by GetAverages().

    Returns:
    None: Displays a bar chart of relevant data.
    """
 
    gameRents = gameInfo["Rents"]
    gameRevs = gameInfo["Reviews"]
    gameScore = gameInfo["Avg. Score"]
    gameStats = [gameRents, gameRevs, gameScore]

    avgRents, avgGameRevs, avgScore = averages
    avgStats = [avgRents, avgGameRevs, avgScore]

    stats = ["Times Rented", "Times Reviewed", "Avg. Score"]

    # Draw graph

    # Locations on x-axis for each set of bars, offset to avoid overlap
    statLocs = [0.85,1.85,2.85]
    avgLocs = [1.15,2.15,3.15]

    # Plot each set of bars
    plt.bar(statLocs, gameStats, 0.3, label="Game Stats")
    plt.bar(avgLocs, avgStats, 0.3, label="Averages", color="limegreen")

    # Add title showing game ID, days since purchase and days since last rent
    titleStr = f"Purchased: {gameInfo['Purchased']} days ago - "
    titleStr = titleStr + f"Last Rented: {gameInfo['Last Rent']} days ago"
    plt.title(titleStr)
    plt.suptitle(f"Game ID: {gameID}")

    plt.xticks([1,2,3], stats)
    plt.legend(loc="upper center")
    plt.show()

# ----------------------------------------------------------------------

def PruneGame(gameID, deleteRental):
    """
    Removes a game from the database provided it isn't currently
    being rented. Also optionally deletes the game's rental
    history.

    Parameters:
    string gameID: The ID of the game to remove.
    bool deleteRental: If true, also removes the game's
    rental history.

    Returns:
    string: An error or a status message indicating succesful pruning.
    """

    gameInfo = db.GetEntry(gameID)
    if gameInfo == None:
        return f"Error: {gameID} not found in database"
    latestRental = gameInfo[-1]
    if latestRental[1] == "":
        return f"Error: {gameID} is currently being rented"
    db.RemoveEntry("Game_Info.txt", gameID)
    status = f"Removed {gameID} from game list"
    if deleteRental:
        db.RemoveEntry("Rental.txt", gameID)
        status = status + f"\nRemoved rental history of {gameID}"
    return status

# ----------------------------------------------------------------------
# MAIN CODE
# ----------------------------------------------------------------------

# SAVE COPIES OF THESE FILES BEFORE RUNNING: Game_Info.txt, Rental.txt
# TEST CODE WILL ALTER THESE DATABASES

if __name__ == "__main__":

    # Delete an entry from game info and rental databases
    print(PruneGame("cod03", True))

    # Attempt to delete an entry currently being rented
    print(PruneGame("drg10", True))

    print("-"*100)

    # Get averages across games
    averages = GetAverages()
    print(averages)

    # Get list of unpopular games and generate advice for each
    unpopular = FindUnpopular(averages)
    info = UnpopularInfo(unpopular, averages)

    # Display bar chart for the last entry in the unpopular games list
    # and show advice for it
    id = list(unpopular.keys())[-1]
    print(info[id])
    DrawBarChart(id, unpopular[id], averages)