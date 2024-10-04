from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import utils as U



##########################################
#######                            #######
#######          Constants         #######
#######                            #######
##########################################
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)
dicAllChatHistory = {
    'strUser': [],
    'strMessage': [],
    'dtDate': [],
    'strRoom': [],
}
tblChatHistory = U.create_chat_history_table()
print('initialized chat history table: ')
print(tblChatHistory)

##########################################
#######                            #######
#######           Routes           #######
#######                            #######
##########################################
# Route to render the chatroom page
@app.route('/')
def index():
    return render_template('chat.html')  # Ensure this matches your HTML filename

# Join a room
@socketio.on('join_room')
def on_join(data):
    strUser = data['strId']  # Get username from the data
    strRoom = data['roomNumber']  # Get room from the data
    join_room(strRoom)
    emit_protocol(strUser = strUser,
                  strMessage = None,
                  strRoom = strRoom, 
                  boolPurpose = 1)
# Leave a room
@socketio.on('leave_room')
def on_leave(data):
    strUser = data['strId']
    strRoom = data['roomNumber']
    leave_room(strRoom)
    emit_protocol(strUser = strUser,
                  strMessage = None,
                  strRoom = strRoom, 
                  boolPurpose = 2)
# Handle incoming messages
@socketio.on('send_message')
def handle_message(data):
    strRoom = data['roomNumber']  # Assuming you are using this to identify the room
    strMessage = data['strUserQuestion']
    strUser = data['strId']
    emit_protocol(strUser = strUser,
                  strMessage = strMessage,
                  strRoom = strRoom, 
                  boolPurpose = 0)

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

def show_chat_history():
    global tblChatHistory
    
    print('Updated Chat History')
    print(tblChatHistory)
if __name__ == '__main__':
    socketio.run(app, debug=True)  # Added debug=True for development purposes
