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
    elif boolPurpose == 2:
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
        This creates LLM for a room, the new llm is added to the table which you must then access.
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
        # Get the LLM object
        tempobjLLM = tblResult['objLLM'].iloc[0]
        # Set the persona to advising
        #strPromptTemplate = Personas.strTemplateSuggestResponse
        strPromptTemplate = Personas.strTemplateContextResponse
        tempobjLLM.create_chain(intLLMAccessory = 3,
                                intRetrieverK = 5,
                                intLLMSetting = 1,
                                strPromptTemplate = strPromptTemplate)
        # Ask the LLM object
        strResponse, strContext = tempobjLLM.get_response(strQuestion = strQuestion, 
                                                          strOutputPath = None, 
                                                          boolShowSource = True)
        #print("[[VERBOSE]] check llm response here: ", strResponse)
        #print("[[VERBOSE]] check llm reference here: ", strContext)
        return strResponse,strContext
    else:
        # Do something if no rows matched the filter
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
                                intLLMSetting = 1,
                                strPromptTemplate = strPromptTemplate)
        # Ask the LLM object
        strResponse, strContext = tempobjLLM.get_response(strQuestion = strQuestion, 
                                                          strOutputPath = None, 
                                                          boolShowSource = True)
        #print("[[VERBOSE]] check llm response here: ", strResponse)
        #print("[[VERBOSE]] check llm reference here: ", strContext)
        return strResponse,strContext
    else:
        # Do something if no rows matched the filter
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
        # Why create_chain() instead of ingest_context()? This is because the chain needs the output of new chroma as retriever, thus whenever create_chain() is called, the directory is reingested and added to the chain
        strPromptTemplate = Personas.strTemplateSuggestResponse
        tempobjLLM.create_chain(intLLMAccessory = 3,
                                intRetrieverK = 5,
                                intLLMSetting = 1,
                                strPromptTemplate = strPromptTemplate)
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