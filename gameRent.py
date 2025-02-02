"""
Game Rent module - gameRent.py

This module contains functions that allow a user to
add a new rental of a game copy.

Functions:
- RentGame(renterID, gameID): Attempts to allow the given renter
to rent the given copy of a game.
"""

# Last Updated: 11/12/2023

import database as db
import subscriptionManager as sm
from datetime import date

# ----------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------

def RentGame(renterID, gameID):
    """
    Accepts a customer ID and the copy of the game to rent.
    Validates the customer ID and ensures that the game can
    be rented based on rental status and customer subscription.
    Prints an error message if the rental could not proceed.

    Parameters:
    renterID: The 4-letter ID of the customer to rent the game.
    gameID: The ID of the copy of the game to rent.

    Returns:
    string: An error message or a message indicating completion.
    """

    subscriptions = sm.load_subscriptions("Subscription_Info.txt")
    returnMsg = ""

    # Enforce valid game ID
    if (db.GetEntry(gameID) == None):
        return "Error: invalid game ID"

    # Enforce valid renter ID
    if not sm.check_subscription(renterID, subscriptions):
        return "Error: customer does not have a valid subscription"

    # Get subscription limit
    subType = subscriptions[renterID]["SubscriptionType"]
    limit = sm.get_rental_limit(subType)

    # Check that the game is not already being rented and
    # check that the customer is not renting the maximum number of games
    rentalData = db.GetEntry(gameID)
    activeRents = len(rentalData) - 1
    if rentalData[-1][1] == "":
        return f"Error: {gameID} is already being rented"

    elif activeRents >= limit:
        return "Error: customer is renting maximum number of games"
    
    # Add new rental entry with current date
    today = str(date.today())
    db.AddRentalEntry(gameID, today, renterID)
    return f"Rented {gameID} to {renterID} successfully"

# ----------------------------------------------------------------------
# MAIN CODE
# ----------------------------------------------------------------------

# SAVE COPIES OF THESE FILES BEFORE RUNNING: Rental.txt
# TEST CODE WILL ALTER THESE DATABASES

if __name__ == "__main__":

    # Add a new rental entry
    print(RentGame("bigi","drg03"))

    # Attempt to rent a game already being rented
    print(RentGame("bigi", "drg03"))