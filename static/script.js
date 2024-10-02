function sendMessage() {
    const customerName = document.getElementById('customerName').value;
    const roomNumber = document.getElementById('roomNumber').value;
    const userMessage = document.getElementById('userMessage').value;
    const divMessages = document.getElementById('messages');

    console.log('sendMessage() function called', userMessage);

    // Clear textarea after sending message
    document.getElementById("userMessage").value = '';

    // Display user's message
    divMessages.innerHTML += `
        <div class="user-message">
            <b>User (${customerName}, Room ${roomNumber}):</b>
            <p>${userMessage.replace(/\n/g, '<br>')}</p>
        </div>`;

    // Scroll to bottom of the messages
    divMessages.scrollTop = divMessages.scrollHeight;

    // Display loading indicator
    divMessages.innerHTML += '<div class="bot-message">Bot is typing...</div>';

    // Make a POST request to Flask server
    fetch('/get_response', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'customerName': customerName,
            'roomNumber': roomNumber,
            'userMessage': userMessage,
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Received bot response:', data);
        
        // Remove loading indicator
        divMessages.removeChild(divMessages.lastChild);

        // Display bot's response
        divMessages.innerHTML += `
            <div class="bot-message">
                <b>Bot:</b> 
                <p>${data.strBotResponse.replace(/\n/g, '<br>')}</p>
            </div>`;

        // Scroll to bottom after the bot response
        divMessages.scrollTop = divMessages.scrollHeight;
    })
    .catch(error => {
        console.error('Error:', error);
        // Remove loading indicator if there's an error
        divMessages.removeChild(divMessages.lastChild);
    });
}

function handleEnterKey(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault(); // Prevents adding a new line in the textarea
        sendMessage(); // Calls the sendMessage function
    }
}

// Function to handle file uploading
function uploadFile() {
    const customerName = document.getElementById('customerName').value;
    const fileInput = document.getElementById('fileInput');
    const divMessages = document.getElementById('messages');
    const formData = new FormData();

    // Check if a file is selected
    if (fileInput.files.length > 0) {
        const selectedFile = fileInput.files[0];

        // Check if the file type is either CSV or TXT
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

    // Append customerName to the form data
    formData.append('customerName', customerName);

    // Display loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.textContent = 'Uploading...';
    divMessages.appendChild(loadingIndicator);

    // Make a POST request to Flask server for file upload
    fetch('/upload_file', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading indicator
        divMessages.removeChild(loadingIndicator);

        // Display response from the server
        divMessages.innerHTML += `
            <div class="file-upload-response">
                <p>${data.message}</p>
            </div>`;
    })
    .catch(error => {
        console.error('Error:', error);
        divMessages.removeChild(loadingIndicator);
    });
}
