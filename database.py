"""
Database module - database.py

This module contains functions to interface with the Game Info
and Rental databases.
This includes functions to retrieve all entries or a specific entry
in a database, and a function to add entries to a database.

Functions:
- GetDatabase(database): Accepts a database name and returns all entries
from that database.

- GetEntry(gameID): Accepts  the ID of a copy of a game, then returns
the game info and rental history of that game.

- RemoveEntry(database, gameID): Accepts the ID of a copy
of a game, then removes it from the database if present.

- AddRentalEntry(gameID, rentDate, renterID): Accepts a list of information
for a database entry, then adds that entry to Rental.

- CompleteRental(gameID, returnDate): Adds a return date to the latest rental of
a copy of a game.
"""

# Last Updated: 11/12/2023

# ----------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------
def GetDatabase(database):
    """
    Returns all entries in the Game Info database.

    Parameters:
    string database: The file name of the database to access.

    Returns:
    list: A list of entries in the database.
    None: if an error occurs during operation.
    """

    gameInfoList = [] # Initialize the list to hold entries
    try:
        f = open(database, "r")
        for entry in f:
            cleanInfo = entry.strip()
            cleanInfoList = cleanInfo.split(",")
            if cleanInfoList[0] == "GameID":
                continue
            gameInfoList.append(cleanInfoList)
        f.close()
        return gameInfoList # Return the populated game info list
    except Exception as e:
        f.close()
        print(f"An error occurred: {e}")
        return # Return nothing if any error occurs.

# ----------------------------------------------------------------------

def GetEntry(gameID):
    """
    Gets the info of a specific entry from a database.

    Parameters:
    string gameID: The id of the copy of the game to get info from.
    
    Returns:
    list: A list containing lists, where the first list is the entry
    in Game Info and the following lists contain the rent date,
    return date and customer ID of each time the game was rented.
    None: if an error occurs during operation.
    """

    databases = ["Game_Info.txt", "Rental.txt"]
    returnList = []

    
    try:
        for database in databases:
            f = open(database, "r")
            for entry in f:
                entryLine = entry.strip()
                entryList = entryLine.split(",")
                if entryList[0] == gameID:
                    if database == "Rental.txt":
                        entryList.pop(0) # Remove game ID from rentals
                    returnList.append(entryList) # Add info to list
            f.close()
            if returnList == []:
                return # Return nothing if an entry is not found
    except Exception as e:
        f.close()
        print(f"An error occurred: {e}")
        return # Return nothing if an error occurs
    return returnList

# ----------------------------------------------------------------------

def RemoveEntry(database, gameID):
    """
    Remove all entries from the given database with the
    given ID.

    Parameters:
    string database: The name of the database to remove the game from.
    string gameID: The ID of the game to remove.

    Returns: 
    None
    """

    # List of database names
    try:
        fileStr = ""

        # Iterate over entries in the database
        f = open(database, "r")
        for entry in f:
            entryLine = entry.strip()
            entryList = entryLine.split(",")
                
            # Build a string of all entries except the removed one
            if entryList[0] != gameID:
                fileStr = fileStr + entry
        f.close()

        # Write the database minus the removed entry to file
        f = open(database, "w")
        f.write(fileStr)
        f.close()

    except Exception as e:
        f.close()
        print(f"An error occurred: {e}")

# ----------------------------------------------------------------------

def AddRentalEntry(gameID, rentDate, renterID):
    """
    Adds a new entry to Rental.

    Parameters:
    string gameID: ID of the game to rent
    string rentDate: Date of rental
    string renterID: ID of customer to rent to

    Returns:
    None
    """

    try:
        # Build new entry to write
        entryString = f"{gameID},{rentDate},,{renterID}\n"

        f = open("Rental.txt", "a") # Write to Rental
        f.write(entryString)
        f.close()
    except Exception as e:
        f.close()
        print(f"An error occurred: {e}")

# ----------------------------------------------------------------------

def CompleteRental(gameID, returnDate):
    """
    Completes the rental of a returned game by adding a return
    date to the corresponding entry in the Rental database.

    Parameters:
    string gameID: the ID of the copy of the game being returned.
    string returnDate: the return date of the copy.

    Returns:
    None
    """

    try:
        f = open("Rental.txt", "r")

        # Build a string containing the database
        fileStr = ""
        for entry in f:
            entryLine = entry.strip()
            entryList = entryLine.split(",")

            # Add a return date to the corresponding entry
            if entryList[0] == gameID and entryList[2] == "":
                returnedEntry = entry.replace(",,",f",{returnDate},")
                fileStr = fileStr + returnedEntry
            else:
                fileStr = fileStr + entry
        f.close()

        # Write to the database with the added return date
        f = open("Rental.txt", "w")
        f.write(fileStr)
        f.close()
    except Exception as e:
        f.close()
        print(f"An error occurred: {e}")

# ----------------------------------------------------------------------
# MAIN CODE
# ----------------------------------------------------------------------

# SAVE COPIES OF THESE FILES BEFORE RUNNING: Rental.txt
# TEST CODE WILL ALTER THESE DATABASES

if __name__ == "__main__":

    # Demonstrating the database retrieval functions
    gameInfo = GetDatabase("Game_Info.txt")
    rentalInfo = GetDatabase("Rental.txt")

    # Print the first 5 entries in each database
    print("GAMES")
    for i in range(0,5):
        print(gameInfo[i])
    print("RENTALS")
    for i in range(0,5):
        print(rentalInfo[i])

    
    print("-"*100)

    # Print info for an entry
    game = GetEntry("cod01")
    for info in game:
        print(info)

    print("-"*100)

    # Add a new entry to rental
    AddRentalEntry("cod09", "2023-12-12", "test")
    print(GetEntry("cod09"))

    # Add a return date to new entry
    CompleteRental("cod09", "2023-12-13")
    print(GetEntry("cod09"))

    # Remove new entry from rental
    RemoveEntry("Rental.txt", "cod09")