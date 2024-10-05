document.getElementById('UserType').addEventListener('change', function() {
    const selectedUserType = this.value;
    const llmPanel = document.querySelector('.llm-panel'); // Select the llm-panel

    if (selectedUserType === "Customer") {
      // Hide the llm-panel when "Customer" is selected
      llmPanel.style.display = 'none';
    } else if (selectedUserType === "Agent") {
      // Show the llm-panel when "Agent" is selected
      llmPanel.style.display = 'flex';
    }
  });


const socket = io(); 

function joinRoom() {
    const roomNumber = document.getElementById('roomNumber').value;
    const strId = document.getElementById('customerName').value; 
    socket.emit('join_room', { roomNumber: roomNumber, strId: strId });
    //update UI soon
    console.log(`User ${strId} joined room ${roomNumber}`);
}

function sendMessage() {
    const strId = document.getElementById('customerName').value; // Adjusted to use the correct input ID
    const strUserQuestion = document.getElementById('userMessage').value; // Adjusted to use the correct input ID
    const roomNumber = document.getElementById('roomNumber').value;
    console.log('sendMessage() function called ' + strUserQuestion); 
    // Clear text area
    document.getElementById("userMessage").value = '';
    // Emit a message to the server
    socket.emit('send_message', { strId, strUserQuestion, roomNumber });
    // Add functionality to call llm for advice
}

socket.on('chat_history', (data) => {
    console.log('check chat_history: ',data)
    const chatHistory = data.chat_history;
    const divMessagePane = document.getElementById('messages');
    
    divMessagePane.innerHTML = '';  // Clear existing messages
    
    // Loop through the chat history and add each message
    chatHistory.forEach((msg) => {
        const divMessage = document.createElement('div');
        divMessage.classList.add('SingleMessage');
        divMessage.style.whiteSpace = 'pre-line';
        divMessage.innerHTML = `<b>${msg.strUser}: ${msg.dtDate} </b> <br> ${msg.strMessage}`;
        divMessagePane.appendChild(divMessage);
    });
});

// Function to handle pressing enter key
function handleEnterKey(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault(); // Prevents adding a new line in the textarea
        sendMessage(); // Calls the sendMessage function
    }
}

// Function to handle uploading files (unchanged)
function uploadFile() {
    const strId = document.getElementById('customerName').value;
    const fileInput = document.getElementById('fileInput');
    const divMessages = document.getElementById('messages');
    const formData = new FormData();

    if (fileInput.files.length > 0) {
        const selectedFile = fileInput.files[0];
        if (selectedFile.type === 'text/csv' || selectedFile.type === 'text/plain') {
            formData.append('file', selectedFile);
        } else {
            alert('Please select a CSV or TXT file.');
            return;
        }
    } else {
        alert('Please select a file before uploading.');
        return;
    }

    formData.append('strId', strId);

    const loadingIndicator = document.createElement('div');
    loadingIndicator.textContent = 'Uploading...';
    divMessages.appendChild(loadingIndicator);

    fetch('/upload_file', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        divMessages.removeChild(loadingIndicator);
        divMessages.innerHTML += `<div>${data.message}</div>`;
    })
    .catch(error => {
        console.error('Error:', error);
        divMessages.removeChild(loadingIndicator);
    });
}

function toggleLLMAdvising() {
    const checkbox = document.getElementById('toggleSwitch');
    const heading = document.getElementById('switch-content');
    
    if (checkbox.checked) {
        heading.style.color = '#2196F3';
        heading.innerHTML = "LLM Advising Is On";
    } else {
        heading.style.color = '#000000';
        heading.innerHTML = "LLM Advising Is Off";
    }
}