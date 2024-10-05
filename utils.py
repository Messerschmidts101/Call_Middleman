from datetime import datetime
import pandas as pd
def create_chat_history_table():
    dicAllChatHistory = {
        'strUser': [],
        'strMessage': [],
        'dtDate': [],
        'strRoom': [],
    }
    tblChatHistory = pd.DataFrame(dicAllChatHistory)
    return tblChatHistory

def create_context_table():
    dicContextDatabase = {
        "liststrUserId":[],
        "listobjLLM":[],
        "liststrUserKnowledgeBasePath":[]
    }
    tblContextDatabase = pd.DataFrame(dicContextDatabase)
    return tblContextDatabase

def add_message_to_chat_history_table(tblChatHistory,dicPayload):
    """
    [[Inputs]]
        1. tblChatHistory = the pandas table you want to modify
        2. dicPayload = the data you want to insert to table
    [[Process/Outputs]]
        This adds payload to chat history database.
    """
    new_row = pd.DataFrame([dicPayload]) 
    tblChatHistory = pd.concat([tblChatHistory, new_row], ignore_index=True)
    return tblChatHistory

def create_payload_to_room(strUsername,
                           strRoom = None,
                           boolPurpose = 0,
                           strMessage = None):
    """
    [[Inputs]]
        1. strUsername = the name of the user
        2. boolPurpose = purpose of the creation, this can be either of the following: [0] message of the user; [1] notif of joined the room; [2] notif of left the room
    [[Process/Outputs]]
        This formats payload to be sent to rooms. This outputs a dictionary with the format:
        ```
        {
            strUser : string,
            strMessage : string,
            strTime : string,
            strRoom : string
        }
        ```
    """
    if boolPurpose == 1:
        strMessage = f'{strUsername} has joined the room.' 
        strUsername = 'System'
    elif boolPurpose == 1:
        strMessage = f'{strUsername} has left the room.' 
        strUsername = 'System'
    # datetime object containing current date and time
    now = datetime.now()
    strTime = now.strftime("%d/%m/%Y %H:%M:%S")
    return {
                'strUser' : strUsername,
                'strMessage' : strMessage,
                'dtDate' : strTime,
                'strRoom': strRoom,
            }

def get_chat_history(tblChatHistory, strRoom):
    """
    [[Inputs]]
        1. tblChatHistory = the pandas table you want to retrieve chat history from
        2. strRoom = the room's chat history you want to return
    [[Process/Outputs]]
        This adds payload to chat history database.
    """
    tblChatHistoryFiltered = tblChatHistory[tblChatHistory['strRoom'] == strRoom]
    tblChatHistoryFiltered['dtDate'] = pd.to_datetime(tblChatHistoryFiltered['dtDate'], format="%d/%m/%Y %H:%M:%S")
    tblChatHistoryFilteredSorted = tblChatHistoryFiltered.sort_values(by='dtDate', ascending=True)
    tblChatHistoryFilteredSorted['dtDate'] = tblChatHistoryFilteredSorted['dtDate'].dt.strftime("%d/%m/%Y %H:%M:%S") # essential to convert to string as payload wont doesnt recognize this data type
    return tblChatHistoryFilteredSorted