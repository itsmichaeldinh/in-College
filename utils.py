from collections import namedtuple
import constants
import database as db
import settings


def validatePassword(password):
    if len(password) < 8 or len(password) > 12:     # out of length bounds
        return False
    elif not any(x.isupper() for x in password):    # no capital letter
        return False
    elif not any(x.isnumeric() for x in password):  # no digits
        return False
    elif not any(x.isalnum() for x in password):    # non alphanumeric
        return False
    else:
        return True


def printUserFriends(dbCursor, uname):
    friends = db.getUserFriendsByName(dbCursor, uname)
    if friends:
        count = 1
        for f in friends:
            name = db.getUserByName(dbCursor, f[0])
            print(f"{count}. {name[2]} {name[3]}")
            count += 1
        return friends
    else:
        return None


def printUsersFoundLastName(dbCursor, lastname):
    users = db.getUsersByLastName(dbCursor, lastname)
    if users:
        count = 1
        for u in users:
            print(f"{count}. {u[2]} {u[3]}")
            count += 1
        return users
    else:
        return None


def printUsersFoundParameter(dbCursor, param, param_type):  # Search by University or Major
    if param_type == 0:  # Search by University
        param_string = "UPPER(university)= '" + param.upper() + "'"
    elif param_type == 1:  # Search by Major
        param_string = "UPPER(major)= '" + param.upper() + "'"
    users = db.getUsersByParameter(dbCursor, param_string)
    if users:
        count = 1
        for u in users:
            name = db.getUserByName(dbCursor, u[0])
            print(f"{count}. {name[2]} {name[3]}")
            count += 1
        return users
    else:
        return None


def handleUserFriendRequests(dbCursor, dbConnection, receiver):
    requests = db.getUserFriendRequests(dbCursor, receiver)  # Check for pending request

    if len(requests) > 0: 
        for r in requests: 
            print("Request from: " + r[0] + "\n")
            response = input("Would you like to Accept (A), Ignore (I) or Return to Previous Menu (Z): ")
            while response.upper() != 'A' or response != 'I':
                if response.upper() == 'A':
                    # To accept will add friend relation to both users
                    db.insertUserFriend(dbCursor, settings.signedInUname, r[0])
                    db.insertUserFriend(dbCursor, r[0], settings.signedInUname)
                    # Delete existing request and commit changes
                    db.deleteFriendRequest(dbCursor, r[0], settings.signedInUname)
                    dbConnection.commit()
                    print(f"{r[0]} has been added!")
                    break
                elif response.upper() == 'I':
                    # Should also delete friend request
                    db.deleteFriendRequest(dbCursor, r[0], settings.signedInUname)
                    dbConnection.commit()
                    print(f"Request from {r[0]} ignored.")
                    break
                elif response.upper() == 'Z':
                    return None
                else: 
                    print(constants.INVALID_INPUT)
                    response = input("Would you like to Accept (A), Ignore (I) or Return to Previous Menu (Z): ")

        return requests
    else:
        print("You have no incoming friend requests.")
        return None


# Searches through existing friend requests to determine if the one you are attempting to send 
# has already been sent, to avoid duplicate records
def checkExistingFriendRequest(dbCursor, sender, receiver):
    requests = db.getUserFriendRequests(dbCursor, receiver)
    exists = False
    if len(requests) > 0:
        for r in requests:
            Request = namedtuple('Request', 'sender_uname reciever_uname')
            f = Request._make(r)
            # Found matching request, shouldn't create a duplicate
            if f.sender_uname == sender and f.reciever_uname == receiver:
                exists = True

    return exists 

