from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit
from dotenv import load_dotenv
import os
import utils as U

# socket vs flask
# socket is for transmit data in real time
# flask is for transmit big data not real time; updating requires reloading of web page to appear


##########################################
#######                            #######
#######          Constants         #######
#######                            #######
##########################################
load_dotenv()
app = Flask(__name__,template_folder='Website',static_folder='Website/static')
#app.config['SECRET_KEY'] = 'your_secret_key' ; just for optional cyber-sec purposes to secure session
socketio = SocketIO(app)
tblChatHistory = U.create_chat_history_table()
tblContextDatabase = U.create_context_table()
strPathKnowledgeBaseUser = U.create_knowledge_base_path(0)
strPathKnowledgeBaseMain = U.create_knowledge_base_path(1)
objAudioTranscriber = U.create_audio_transcriber()


##########################################
#######                            #######
#######           Routes           #######
#######                            #######
##########################################
@app.route('/')
def index():
    return render_template('chat.html')  
@socketio.on('join_room')
def on_join(data):
    global tblContextDatabase
    strUser = data['strId']
    strRoom = data['intRoomNumber']
    join_room(strRoom)
    #checks if llm exists, if not, create llm for that room
    if U.get_llm(tblContextDatabase = tblContextDatabase,
                 strRoom = strRoom):
        pass # nothing happens really as there is an llm already created
    else:
        tblContextDatabase = U.create_llm_to_room(tblContextDatabase = tblContextDatabase,
                            strRoom = strRoom,
                            strPathKnowledgeBaseUser = strPathKnowledgeBaseUser,
                            strPathKnowledgeBaseMain = strPathKnowledgeBaseMain) # modify this part soon when uploading file
    emit_protocol(strUser = strUser,
                  strMessage = None,
                  strRoom = strRoom, 
                  boolPurpose = 1)
    
@socketio.on('leave_room') # shit needs improvement
def on_leave(data):
    strUser = data['strId']
    strRoom = data['intRoomNumber']
    leave_room(strRoom)
    emit_protocol(strUser = strUser,
                  strMessage = None,
                  strRoom = strRoom, 
                  boolPurpose = 2)
    
@socketio.on('send_message')
def handle_message(data):
    strRoom = data['intRoomNumber']
    strMessage = data['strUserQuestion']
    strUser = data['strId']
    strUserType = data['strUserType']
    
    #print(f'[[VERBOSE]] Sending from audio: \n{strRoom}\n{strMessage}\n{strUser}\n{strUserType}')
    if strUserType.lower() == 'customer':
        print(F'[[VERBOSE]]: Original customer message: {strMessage}')
        strMessage = translate_llm(strRoom = strRoom, strMessage = strMessage)
        print(F'[[VERBOSE]]: Translated customer message: {strMessage}')
    emit_protocol(strUser = strUser,
                  strMessage = strMessage,
                  strRoom = strRoom,
                  boolPurpose = 0)

@app.route('/upload_audio', methods=['POST'])
def convert_audio_to_text_message():
    # Step 1: Get data and audio
    objAudioFile = request.files['audio']
    strRoom = request.form.get('strRoom')
    strUser = request.form.get('strId')
    strUserType = request.form.get('strUserType')

    # Step 2: Get transcription of audio
    strTranscriptResult = U.create_transcript_to_room(strRoom = strRoom, 
                                                objAudioFile = objAudioFile,
                                                objAudioTranscriber = objAudioTranscriber,
                                                boolVerbose = True)
    
    # as much as we want to call handle_message by emit or by direct function call, it wouldnt work because youre calling socketio from app route, thus communication wont trigger, thus instead the solution is to pass the transcript back to client, then from client call handle_message passing the transcript 
    return jsonify({'status': 'success trancription', 'message': strTranscriptResult}), 200
    
@socketio.on('ask_llm') # LLM advise needs to be done asynchronously with emit_protocol
def ask_llm(data):
    strUserType = data['strUserType']
    if strUserType.lower() == 'customer':
        global tblContextDatabase
        strRoom = data['intRoomNumber']
        strQuestion = data['strUserQuestion']
        strResponse,strContext = U.get_llm_advice(tblContextDatabase = tblContextDatabase,
                                                    strRoom = strRoom,
                                                    strQuestion = strQuestion)
        emit_protocol(strUser = None,
                    strMessage = strResponse,
                    strRoom = strRoom, 
                    boolPurpose = 3)
    else:
        print('[[VERBOSE]] Not a customer user type to generate an llm advise.')
    
@app.route('/file_upload', methods=['POST']) # cannot be converted to socket protocol
def handle_file_upload():
    global tblContextDatabase
    # Access file from the form data
    if 'file' not in request.files:
        return jsonify({'status': 'failure', 'error': 'No file part'})

    file = request.files['file']
    customer_name = request.form.get('customerName')
    user_message = request.form.get('userMessage')
    room_number = request.form.get('roomNumber')
    user_type = request.form.get('UserType')

    # Process the file 
    file.save(os.path.join(strPathKnowledgeBaseUser,room_number,file.filename)) 
    U.create_embeddings_to_room(tblContextDatabase = tblContextDatabase,
                                strRoom = room_number)

    return jsonify({'status': 'success'})

def emit_protocol(strUser,strMessage,strRoom,boolPurpose = 0):
    '''
    [[Inputs]]
        1. strUser = the author of the message.
        2. strMessage = the message to be sent.
        3. strRoom = the destination of the message.
        4. strUserType = the type of user of the author of the message.
        5. boolPurpose = the purpose of emit: [0] message of the user; [1] notif of joined the room; [2] notif of left the room; [3] the message will be from LLM advise
    [[Process/Outputs]]
        This improves basic emit() function by standardizing the emit() processes while still remaining the purpose of sending message to a room.
    '''
    global tblChatHistory  # Declare it as global to modify the global variable

    if boolPurpose == 0:
        dicPayload = U.create_payload_to_room(strUsername = strUser,
                                                strRoom = strRoom,
                                                boolPurpose = 0,
                                                strMessage = strMessage)
        tblChatHistory = U.add_message_to_chat_history_table(tblChatHistory = tblChatHistory,
                                                                dicPayload = dicPayload)
        tblChatHistoryOfRoom = U.get_chat_history(tblChatHistory = tblChatHistory, 
                                                    strRoom = strRoom)
        dicPayloadChatHistory = tblChatHistoryOfRoom.to_dict(orient='records')  # 'records' format gives a list of dictionaries
        emit('chat_history', 
            {'chat_history': dicPayloadChatHistory},
            room = strRoom)
    elif boolPurpose == 1:
        dicPayload = U.create_payload_to_room(strUsername = strUser,
                                          strRoom = strRoom,
                                          boolPurpose = 1,
                                          strMessage = None)
        tblChatHistory = U.add_message_to_chat_history_table(tblChatHistory = tblChatHistory,
                                                            dicPayload = dicPayload)
        tblChatHistoryOfRoom = U.get_chat_history(tblChatHistory = tblChatHistory, 
                                                strRoom = strRoom)
        dicPayloadChatHistory = tblChatHistoryOfRoom.to_dict(orient='records')  # 'records' format gives a list of dictionaries
        emit('chat_history', 
            {'chat_history': dicPayloadChatHistory},
            room = strRoom)
    elif boolPurpose == 2:
        dicPayload = U.create_payload_to_room(strUsername = strUser,
                                          strRoom = strRoom,
                                          boolPurpose = 2,
                                          strMessage = None)
        tblChatHistory = U.add_message_to_chat_history_table(tblChatHistory = tblChatHistory,
                                                            dicPayload = dicPayload)
        tblChatHistoryOfRoom = U.get_chat_history(tblChatHistory = tblChatHistory, 
                                                strRoom = strRoom)
        dicPayloadChatHistory = tblChatHistoryOfRoom.to_dict(orient='records')  # 'records' format gives a list of dictionaries
        emit('chat_history', 
            {'chat_history': dicPayloadChatHistory},
            room = strRoom)
    elif boolPurpose == 3:
        dicPayload = U.create_payload_to_room(strUsername = 'LLM Advisor',
                                                strRoom = strRoom,
                                                boolPurpose = 0,
                                                strMessage = strMessage)
       
        emit('llm_advise', 
            {'llm_advise': dicPayload},
            room = strRoom)
    show_chat_history()

def show_chat_history():
    global tblChatHistory
    print('[[VERBOSE]] Updated Chat History')
    print(tblChatHistory)

def translate_llm(strRoom,strMessage):
    strResponse,strContext = U.get_llm_translation(tblContextDatabase = tblContextDatabase,
                                                    strRoom = strRoom,
                                                    strQuestion = strMessage)
    return strResponse

if __name__ == '__main__':
    socketio.run(app, debug=True, host='192.168.1.8')  # Added debug=True for development purposes, host is required so that mobile device can access it; host is ipv4 address of server
