from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room, emit
from dotenv import load_dotenv
import os
import utils as U


##########################################
#######                            #######
#######          Constants         #######
#######                            #######
##########################################
load_dotenv()
app = Flask(__name__)
#app.config['SECRET_KEY'] = 'your_secret_key' ; just for optional cyber-sec purposes to secure session
socketio = SocketIO(app)
tblChatHistory = U.create_chat_history_table()
tblContextDatabase = U.create_context_table()
strPathKnowledgeBaseUser = U.create_knowledge_base_path(0)
strPathKnowledgeBaseMain = U.create_knowledge_base_path(1)

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
    if U.get_llm(tblContextDatabase = tblContextDatabase,
                 strRoom = strRoom):
        pass # nothing happens really as there is an llm already created
    else:
        tblContextDatabase = U.create_llm_to_room(tblContextDatabase = tblContextDatabase,
                            strRoom = strRoom,
                            strPathKnowledgeBaseUser = strPathKnowledgeBaseUser,
                            strPathKnowledgeBaseMain = strPathKnowledgeBaseMain)
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
    emit_protocol(strUser = strUser,
                  strMessage = strMessage,
                  strRoom = strRoom, 
                  boolPurpose = 0)
    
@socketio.on('ask_llm')
def ask_llm(data):
    global tblContextDatabase
    print('[[VERBOSE]]: checking context database before asking llm: ')
    print(tblContextDatabase)
    strRoom = data['intRoomNumber']
    strQuestion = data['strUserQuestion']
    strResponse,strContext = U.get_llm_response(tblContextDatabase = tblContextDatabase,
                                                strRoom = strRoom,
                                                strQuestion = strQuestion)
    emit_protocol(strUser = None,
                  strMessage = strResponse,
                  strRoom = strRoom, 
                  boolPurpose = 3)

def emit_protocol(strUser,strMessage,strRoom,boolPurpose = 0):
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
    print('Updated Chat History')
    print(tblChatHistory)

if __name__ == '__main__':
    socketio.run(app, debug=True)  # Added debug=True for development purposes
