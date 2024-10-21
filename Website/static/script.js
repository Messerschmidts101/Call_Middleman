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
    const intRoomNumber = document.getElementById('roomNumber').value;
    const strId = document.getElementById('customerName').value; 

    const divMessagePane = document.getElementById('messages');
    
    divMessagePane.innerHTML = '';  // Clear existing messages
    const divMessage = document.createElement('div');
    divMessage.classList.add('SingleMessage');
    divMessage.style.whiteSpace = 'pre-line';
    divMessage.innerHTML = `<b>LOADING ROOM...</b>`;
    divMessagePane.appendChild(divMessage);
    
    socket.emit('join_room', { intRoomNumber: intRoomNumber, strId: strId });
    //update UI soon
    console.log(`User ${strId} joined room ${intRoomNumber}`);
}

function sendMessage() {
    const strId = document.getElementById('customerName').value; // Adjusted to use the correct input ID
    const strUserQuestion = document.getElementById('userMessage').value; // Adjusted to use the correct input ID
    const intRoomNumber = document.getElementById('roomNumber').value;
    const strUserType = document.getElementById('UserType').value;
    console.log('sendMessage() function called ' + strId + ' ' + strUserQuestion + ' ' + intRoomNumber + ' ' + strUserType); 
    // Clear text area
    document.getElementById("userMessage").value = '';
    // Emit a message to the server
    socket.emit('send_message', { strId, strUserQuestion, intRoomNumber, strUserType });
    socket.emit('ask_llm', { intRoomNumber, strUserQuestion, strUserType });
    // Add functionality to call llm for advice
}

socket.on('chat_history', (data) => {
    console.log('check chat_history: ',data)
    const chatHistory = data.chat_history;
    const strId = document.getElementById('customerName').value; // Adjusted to use the correct input ID

    const divMessagePane = document.getElementById('messages');
    
    divMessagePane.innerHTML = '';  // Clear existing messages
    
    // Loop through the chat history and add each message
    chatHistory.forEach((msg) => {
        const divMessage = document.createElement('div');
        divMessage.classList.add('SingleMessage');
        divMessage.style.whiteSpace = 'pre-line';

        // Assign id based on whether the message user matches the customer name
        if (strId === msg.strUser) {
            divMessage.id = 'owner';
        } else if ('System' == msg.strUser){
            divMessage.id = 'system';
        } else {
            divMessage.id = 'other';
        }

        // Set the message content
        divMessage.innerHTML = `<b>${msg.strUser}: ${msg.dtDate} </b> <br> ${msg.strMessage}`;
        divMessagePane.appendChild(divMessage);
    });
});


socket.on('llm_advise', (data) => {
    console.log('check llm_advise: ', data);
    const llmAdvise = data.llm_advise; // Assuming llm_advise is an array of messages
    const divLLMPane = document.getElementById('advisedResponse');
    
    // Clear previous responses
    divLLMPane.innerHTML = ''; 

    // Display the single LLM advice
    divLLMPane.innerHTML = `<b>${llmAdvise.dtDate}</b>${llmAdvise.strMessage}`;
});
    

// Function to handle pressing enter key
function handleEnterKey(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault(); // Prevents adding a new line in the textarea
        sendMessage(); // Calls the sendMessage function
    }
}

function uploadFile() {
    const strId = document.getElementById('customerName').value;
    const strUserQuestion = document.getElementById('userMessage').value;
    const intRoomNumber = document.getElementById('roomNumber').value;
    const strUserType = document.getElementById('UserType').value;
    const fileInput = document.getElementById('fileInput');
    const divInput = document.getElementById('file-status');
    const file = fileInput.files[0];
    
    divInput.innerHTML = '';  // Clear existing messages
    
    if (!file) {
        alert('Please select a file first.');
        return;
    }

    // Inform the user that the upload is starting
    const divMessage = document.createElement('div');
    divMessage.classList.add('SingleMessage');
    divMessage.style.whiteSpace = 'pre-line';
    divMessage.innerHTML = `<b>UPLOADING FILE TO SERVER</b>`;
    divInput.appendChild(divMessage);

    console.log('uploadFile() function called with:', {
        customerName: strId,
        userMessage: strUserQuestion,
        roomNumber: intRoomNumber,
        userType: strUserType
    });

    const formData = new FormData();
    formData.append('file', file);
    formData.append('customerName', strId);
    formData.append('userMessage', strUserQuestion);
    formData.append('roomNumber', intRoomNumber);
    formData.append('UserType', strUserType);

    fetch('/file_upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        divInput.innerHTML = '';  // Clear existing messages after the upload
        const divSuccessMessage = document.createElement('div');
        divSuccessMessage.classList.add('SingleMessage');
        divSuccessMessage.style.whiteSpace = 'pre-line';
        divSuccessMessage.innerHTML = `<b>Finished Uploading</b>`;
        divInput.appendChild(divSuccessMessage);
        // Remove the message after 10 seconds (10000 milliseconds)
        setTimeout(() => {
            divSuccessMessage.remove();
        }, 10000); // 10 seconds
    })
    .catch(error => {
        console.error('Error:', error);
        divInput.innerHTML = '';  // Clear existing messages
        const divErrorMessage = document.createElement('div');
        divErrorMessage.classList.add('SingleMessage');
        divErrorMessage.style.whiteSpace = 'pre-line';
        divErrorMessage.innerHTML = `<b>Upload Failed. Please try again.</b>`;
        divInput.appendChild(divErrorMessage);
        // Remove the message after 10 seconds (10000 milliseconds)
        setTimeout(() => {
            divSuccessMessage.remove();
        }, 10000); // 10 seconds
    });
}

/* =================================================*/
/* =============== FOR SENDING AUDIO ===============*/
/* =================================================*/

let mediaRecorder;
let audioChunks = [];
let isRecording = false; // State variable to track recording status

// Function to toggle between start and stop recording
function toggleRecording() {
    if (!isRecording) {
        startRecording(); // Start recording if not already recording
    } else {
        stopRecording(); // Stop recording if it's already in progress
    }
}

// Function to start recording
function startRecording() {
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
            mediaRecorder.start();
            isRecording = true; // Set the state to recording
            updateRecordingStatus("Recording..."); // Update button text to show status
            console.log("Recording started");
        })
        .catch(error => {
            console.error('Error accessing microphone: ', error);
        });
}

// Function to stop recording and send audio to the server
function stopRecording() {
    if (!isRecording) return; // Prevent stopping if not currently recording

    mediaRecorder.stop();
    mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        console.log('Audio Blob size:', audioBlob.size);  // Check Blob size
        audioChunks = []; // Clear the chunks after stopping
        
        // Send the audioBlob to the server
        sendAudioMessage(audioBlob);
        updateRecordingStatus("Start Recording"); // Reset button text after stopping
        console.log("Recording stopped and sent");
        isRecording = false; // Reset the state after stopping
    };
}

// Function to send the audio file to the server
function sendAudioMessage(audioBlob) {
    console.log('Sending audioBlob size:', audioBlob.size);  // Check size before sending
    const intRoomNumber = document.getElementById('roomNumber').value;
    const formData = new FormData();
    formData.append('audio', audioBlob);
    formData.append('strRoom', intRoomNumber);

    fetch('/upload_audio', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to update recording button status
function updateRecordingStatus(text) {
    const statusSpan = document.getElementById('recordingStatus');
    statusSpan.textContent = text;
}
/* =====================================================*/
/* =============== END FOR SENDING AUDIO ===============*/
/* =====================================================*/