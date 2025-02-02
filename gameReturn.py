"""
Game Return module - gameReturn.py

This module contains functions that allow a user to
return a rented copy of a game and collect feedback.

Functions:
- ReturnGame(gameID): Returns a copy of a game if it is
currently being rented.
- AddFeedback(gameID, rating, comment): Collects feedback about
a returned game and adds it to the Game Feedback database.
"""

# Last Updated: 11/12/2023

import database as db
import feedbackManager as fm
from datetime import date

# ----------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------

def ReturnGame(gameID):
    """
    Returns a currently rented copy of a game.

    Parameters:
    string gameID: The ID of the copy of the game being returned.
    
    Returns:
    string: An error message or a message indicating completion.
    """

    # Enforce valid game ID
    if (db.GetEntry(gameID) == None):
        return "Error: invalid game ID"

    # Ensure that the latest rental is not already completed
    rentalData = db.GetEntry(gameID)
    latestRental = rentalData[-1]
    if latestRental[1] != "":
        return f"Error: {gameID} is not currently being rented"
    
    # Add a return date to the corresponding Rental entry
    today = str(date.today())
    db.CompleteRental(gameID, today)
    return f"Returned {gameID} successfully"

# ----------------------------------------------------------------------

def AddFeedback(gameID, rating, comment):
    """
    This function collects feedback from a returned game
    and adds it to the Game Feedback database.

    Parameters:
    string gameID: The copy of the game to add feedback for.
    int rating: The rating from 1-5 of the game.
    string comment: The comment provided by the user.

    Returns:
    string: An error message or a message indicating completion.
    """

    # Enforce valid game ID
    # Return an empty string as this error will already be generated
    # by ReturnGame()
    if (db.GetEntry(gameID) == None):
        return "Error: invalid game ID"
    
    # Enforce valid rating
    if rating < 1 or rating > 5:
        return "Error: rating must be a number from 1-5"
    
    fm.add_feedback(gameID, rating, comment)
    return f"Added feedback for {gameID}"


# ----------------------------------------------------------------------
# MAIN CODE
# ----------------------------------------------------------------------

# SAVE COPIES OF THESE FILES BEFORE RUNNING: Rental.txt, Game_Feedback.txt
# TEST CODE WILL ALTER THESE DATABASES

if __name__ == "__main__":

    # Return a rented game
    print(ReturnGame("hk05"))

    # Attempt to return a game that isn't being rented
    print(ReturnGame("cod03"))

    # Add feedback for a game
    print(AddFeedback("fifa07", 4, "Great!"))