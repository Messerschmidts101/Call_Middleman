from flask import Flask, render_template
from flask_socketio import SocketIO, join_room, leave_room, send

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Route to render the chatroom page
@app.route('/')
def index():
    return render_template('chat.html')

# Join a room
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(f'{username} has entered the room.', to=room)

# Leave a room
@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(f'{username} has left the room.', to=room)

# Handle incoming messages
@socketio.on('message')
def handle_message(data):
    room = data['room']
    send(f"{data['username']}: {data['message']}", to=room)

if __name__ == '__main__':
    socketio.run(app)
