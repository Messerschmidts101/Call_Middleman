from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Route to render the chatroom page
@app.route('/')
def index():
    return render_template('chat.html')  # Ensure this matches your HTML filename

# Join a room
@socketio.on('join_room')
def on_join(data):
    username = data['strId']  # Get username from the data
    room = data['roomNumber']  # Get room from the data
    join_room(room)
    send({'username': 'System', 'message': f'{username} has entered the room.'}, to=room)

# Leave a room
@socketio.on('leave_room')
def on_leave(data):
    username = data['strId']
    room = data['roomNumber']
    leave_room(room)
    send({'username': 'System', 'message': f'{username} has left the room.'}, to=room)

# Handle incoming messages
@socketio.on('send_message')
def handle_message(data):
    room = data['roomNumber']  # Assuming you are using this to identify the room
    message = data['strUserQuestion']
    username = data['strId']
    send({'username': username, 'message': message}, to=room)


if __name__ == '__main__':
    socketio.run(app, debug=True)  # Added debug=True for development purposes
