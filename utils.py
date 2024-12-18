from datetime import datetime
import Large_Language_Model.LLM_Component as LLM_Component
import Large_Language_Model.Personas as Personas
import pandas as pd
import speech_recognition as sr
import os,shutil,subprocess

def create_audio_transcriber():
    return sr.Recognizer()

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
                           intPurpose = 0,
                           strMessage = None):
    """
    [[Inputs]]
        1. strUsername = the name of the user
        2. intPurpose = purpose of the creation, this can be either of the following: [0] message of the user; [1] notif of joined the room; [2] notif of left the room
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
    if intPurpose == 1:
        strMessage = f'{strUsername} has joined the room.' 
        strUsername = 'System'
    elif intPurpose == 2:
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
                       strPathKnowledgeBaseMain,
                       intLLMSetting = 1,
                       intLLMAccessory = 5,
                       strPromptTemplate = Personas.strTemplateSuggestResponseV2):
    """
    [[Inputs]]
        1. tblContextDatabase = the pandas table you want to modify; if None, returns an llm object instead.
        2. strRoom = the room that needs to have the LLM
        3. strPathKnowledgeBaseUser = the directory path containing specific contexts
        4. strPathKnowledgeBaseMain = the directory path containing general contexts
    [[Process/Outputs]]
        This creates LLM for a room, the new llm is added to the table which you must then access; however if tblContextDatabase is None, returns an llm object instead.
    """
    def include_main_knowledge_base(strRoom):
        Path_Target_Directory =  os.path.join(strPathKnowledgeBaseUser, strRoom)
        shutil.copytree(strPathKnowledgeBaseMain, Path_Target_Directory,dirs_exist_ok=True)

    # Create a directory based on strRoom
    strUserFolderPath = os.path.join(strPathKnowledgeBaseUser, strRoom)
    os.makedirs(strUserFolderPath, exist_ok=True)
    include_main_knowledge_base(strRoom)
    strUserDirectory =  os.path.join(strPathKnowledgeBaseUser, strRoom)

    # Create LLM
    objLLM = LLM_Component.LLM(intLLMSetting = intLLMSetting,
                        strIngestPath = strUserDirectory,
                        strPromptTemplate = strPromptTemplate,
                        strAPIKey = os.getenv('GROQ_KEY'),
                        boolCreateDatabase = True,
                        intLLMAccessory = intLLMAccessory)
    
    if tblContextDatabase is None: 
        return objLLM
    else:
        # Update Table
        dicNewRow = {'strRoom' : strRoom,
                    'objLLM' : objLLM,
                    'strKnowledgePath' : strUserDirectory}
        new_row = pd.DataFrame([dicNewRow]) 
        tblContextDatabase = pd.concat([tblContextDatabase, new_row], ignore_index=True)
        return tblContextDatabase

def get_llm(tblContextDatabase,strRoom):
    '''
    [[Inputs]]
        1. tblContextDatabase = the pandas table you want to find the llm assigned to the room; each llm in this table has different contexts as it is assigned to different rooms
        2. strRoom = the room identifier for which the LLM is assigned, this is used to see if theres an llm assigned to the room already
    [[Process/Outputs]]
        This checks if there's an llm already for that room: return True if already exists, otherwise returns False.
    '''
    tblResult = tblContextDatabase[tblContextDatabase['strRoom'] == strRoom]
    if not tblResult.empty:
        return True
    else:
        return False

def get_llm_advice(tblContextDatabase,
                     strRoom,
                     strQuestion):
    '''
    [[Inputs]]
        1. tblContextDatabase = the pandas table you want to find the llm assigned to the room; each llm in this table has different contexts as it is assigned to different rooms
        2. strRoom = the room identifier for which the LLM is assigned, this is used to locate the corresponding LLM in the database
        3. strQuestion = the question of customer that the llm will advise response
    [[Process/Outputs]]
        This asks the llm the appropriate response to a customer's query.
    '''
    tblResult = tblContextDatabase[tblContextDatabase['strRoom'] == strRoom]
    if not tblResult.empty:
        print('[[VERBOSE]] get_llm_advice')
        # Get the LLM object
        tempobjLLM = tblResult['objLLM'].iloc[0]
        # Set the persona to advising
        strPromptTemplate = Personas.strTemplateSuggestResponseV2
        tempobjLLM.create_chain(intLLMAccessory = 5,
                                intRetrieverK = 2,
                                strPromptTemplate = strPromptTemplate)
        # Ask the LLM object
        strResponse, strContext = tempobjLLM.get_response(strQuestion = strQuestion, 
                                                          strOutputPath = None, 
                                                          boolShowSource = True)
        return strResponse,strContext
    else:
        print(f"No data found for room: {strRoom}")
        return None,None

def get_llm_translation(tblContextDatabase,
                        strRoom,
                        strQuestion):
    '''
    [[Inputs]]
        1. tblContextDatabase = the pandas table you want to find the llm assigned to the room; each llm in this table has different contexts as it is assigned to different rooms
        2. strRoom = the room identifier for which the LLM is assigned, this is used to locate the corresponding LLM in the database
        3. strQuestion = the question of customer that the llm will advise response
    [[Process/Outputs]]
        This asks the llm to translate the customer's query to something informative and safe.
    '''
    tblResult = tblContextDatabase[tblContextDatabase['strRoom'] == strRoom]
    if not tblResult.empty:
        # Get the LLM object
        tempobjLLM = tblResult['objLLM'].iloc[0]
        # Set the persona to translating
        strPromptTemplate = Personas.strTemplateTranslateToCalm
        tempobjLLM.create_chain(intLLMAccessory = 0,
                                intRetrieverK = None,
                                strPromptTemplate = strPromptTemplate)
        # Ask the LLM object
        strResponse, strContext = tempobjLLM.get_response(strQuestion = strQuestion, 
                                                          strOutputPath = None, 
                                                          boolShowSource = False,
                                                          boolSaveChat = False)
        return strResponse,strContext
    else:
        print(f"No data found for room: {strRoom}")
        return None,None
    
def create_embeddings_to_room(tblContextDatabase,
                                strRoom):
    '''
    [[Inputs]]
        1. tblContextDatabase = the pandas table you want to find the llm assigned to the room; each llm in this table has different contexts as it is assigned to different rooms.
        2. strRoom = the room identifier for which the LLM is assigned, this is used to locate the corresponding LLM in the database.
    [[Process/Outputs]]
        This creates the embeddings to a room, this is necessary whenever new contents are to be included in the context of the llm assigned to the room. Outputs boolean based on operation success.
    '''
    tblResult = tblContextDatabase[tblContextDatabase['strRoom'] == strRoom]
    if not tblResult.empty:
        # Get the LLM object
        tempobjLLM = tblResult['objLLM'].iloc[0]
        # Instruct to ingest data
        tempobjLLM.add_context()
        return True
    else:
        # Do something if no rows matched the filter
        print(f"No data found for room: {strRoom}")
        return False
    
def create_transcript_to_room(strRoom,objAudioFile,objAudioTranscriber,boolVerbose = False):
    # Step 1: Save the audio file to disk
    strAudioFilePath = os.path.join(os.getcwd(), 'Website', 'Database', 'User_Knowledge_Base', strRoom, 'audio.wav')
    strConvertedAudioFilePath = os.path.join(os.getcwd(), 'Website', 'Database', 'User_Knowledge_Base', strRoom, 'converted_audio.wav')
    try:
        with open(strAudioFilePath, 'wb') as f:
            f.write(objAudioFile.read())
        if boolVerbose:
            if os.path.exists(strAudioFilePath):
                print(f"[[VERBOSE]] Raw audio file saved at: {strAudioFilePath}, Size: {os.path.getsize(strAudioFilePath)} bytes")
            else:
                print(f"[[VERBOSE]] Raw audio file not found after saving at: {strAudioFilePath}")
        # Convert the audio to PCM WAV using ffmpeg; necessary for transcriber 
        subprocess.run(['ffmpeg','-y', '-i', strAudioFilePath, '-ar', '16000', '-ac', '1', strConvertedAudioFilePath], check=True)
    except Exception as e:
        return f"[[VERBOSE]] Error failed to store audio due to reason: {e}"

    # Step 2: Create transcription
    try:
        with sr.AudioFile(strConvertedAudioFilePath) as objSource:
            objAudio = objAudioTranscriber.record(objSource)  # Read the entire audio file
        strTranscriptResult = objAudioTranscriber.recognize_google(objAudio)
        if boolVerbose:
            print('[[VERBOSE]] Check transcript here: ', strTranscriptResult)
    except Exception as e:
        return f"[[VERBOSE]] Error failed to transcribe audio due to reason: {e}"

    # Step 3: Delete the audio file
    try:
        if os.path.exists(strAudioFilePath):
            os.remove(strAudioFilePath)
            if boolVerbose:
                print(f"[[VERBOSE]] Deleted raw audio file: {strAudioFilePath}")
        if os.path.exists(strConvertedAudioFilePath):
            os.remove(strConvertedAudioFilePath)
            if boolVerbose:
                print(f"[[VERBOSE]] Deleted converted audio file: {strConvertedAudioFilePath}")
    except Exception as e:
        return f"[[VERBOSE]] Error: Failed to delete audio files due to reason: {e}"
    
    return strTranscriptResult