from datetime import datetime
import Large_Language_Model.LLM_Component as LLM_Component
import Large_Language_Model.Personas as Personas
import pandas as pd
import os,shutil
strPromptTemplate = Personas.strPersonaUWU + Personas.strTemplateDefaultConversation 

def create_knowledge_base_path(boolMode = 0):
    if boolMode == 0:
        strPath = os.path.join(os.getcwd(), 'Website', 'Database', 'User_Knowledge_Base')
    elif boolMode == 1:
        strPath = os.path.join(os.getcwd(), 'Website', 'Database', 'Main_Knowledge_Base')
    return strPath
    
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
        "strRoom":[],
        "objLLM":[],
        "strKnowledgePath":[]
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

def create_llm_to_room(tblContextDatabase,
                       strRoom,
                       strPathKnowledgeBaseUser,
                       strPathKnowledgeBaseMain):
    """
    [[Inputs]]
        1. tblContextDatabase = the pandas table you want to modify
        2. strRoom = the room that needs to have the LLM
        3. strPathKnowledgeBaseUser = the directory path containing specific contexts
        4. strPathKnowledgeBaseMain = the directory path containing general contexts
    [[Process/Outputs]]
        This creates LLM for a room, it is added as a new row to the table
    """
    def include_main_knowledge_base(strRoom):
        Path_Target_Directory =  os.path.join(strPathKnowledgeBaseUser, strRoom)
        shutil.copytree(strPathKnowledgeBaseMain, Path_Target_Directory,dirs_exist_ok=True)

    # Create a directory based on strRoom
    strUserFolderPath = os.path.join(strPathKnowledgeBaseUser, strRoom)
    os.makedirs(strUserFolderPath, exist_ok=True)
    include_main_knowledge_base(strRoom)

    # Create LLM
    Path_Target_Directory =  os.path.join(strPathKnowledgeBaseUser, strRoom)
    objLLM = LLM_Component.LLM(intLLMSetting = 1,
                        strIngestPath = Path_Target_Directory,
                        strPromptTemplate = Personas.strTemplateSuggestResponse,
                        strAPIKey = os.getenv('GROQ_KEY'),
                        boolCreateDatabase = True,
                        intLLMAccessory = 3)
    # Update Table
    dicNewRow = {
                    'strRoom' : strRoom,
                    'objLLM' : objLLM,
                    'strKnowledgePath' : Path_Target_Directory,
                }
    new_row = pd.DataFrame([dicNewRow]) 
    tblContextDatabase = pd.concat([tblContextDatabase, new_row], ignore_index=True)
    return tblContextDatabase

def get_llm(tblContextDatabase,strRoom):
    '''
    [[Inputs]]
        1. tblContextDatabase = the pandas table you want to find the llm assigned to the room; each llm in this table has different contexts as it is assigned to different rooms
        2. strRoom = the room identifier for which the LLM is assigned, this is used to see if theres an llm assigned to the room already
    [[Process/Outputs]]
        This checks if there's an llm already for that room
    '''
    tblResult = tblContextDatabase[tblContextDatabase['strRoom'] == strRoom]
    if not tblResult.empty:
        return True
    else:
        return False

def get_llm_response(tblContextDatabase,
                     strRoom,
                     strQuestion):
    '''
    [[Inputs]]
        1. tblContextDatabase = the pandas table you want to find the llm assigned to the room; each llm in this table has different contexts as it is assigned to different rooms
        2. strRoom = the room identifier for which the LLM is assigned, this is used to locate the corresponding LLM in the database
        3. strQuestion = the question of customer that the llm will advise response
    [[Process/Outputs]]
        This asks the llm the appropriate response to a customer's query
    '''
    tblResult = tblContextDatabase[tblContextDatabase['strRoom'] == strRoom]
    if not tblResult.empty:
        # Get the LLM object
        tempobjLLM = tblResult['objLLM'].iloc[0]
        strResponse, strContext = tempobjLLM.get_response(strQuestion = strQuestion, 
                                                          strOutputPath = None, 
                                                          boolShowSource = True)
        print("[[VERBOSE]] check llm response here: ", strResponse)
        print("[[VERBOSE]] check llm reference here: ", strContext)
        return strResponse,strContext
    else:
        # Do something if no rows matched the filter
        print(f"No data found for room: {strRoom}")
        return None,None

