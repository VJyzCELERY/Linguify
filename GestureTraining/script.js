document.addEventListener('DOMContentLoaded', function() {
    const videoElement = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const predictionElement = document.getElementById('prediction');
    const errorElement = document.getElementById('error');

    let socket;
    const socketUrl = 'ws://localhost:8001';

    function connectWebSocket() {
        socket = new WebSocket(socketUrl);

        socket.onopen = () => {
            console.log("Connected to WebSocket server.");
            errorElement.textContent = '';
        };

        socket.onerror = (error) => {
            errorElement.textContent = 'WebSocket error: ' + error.message;
            console.error("WebSocket Error:", error);
        };

        socket.onclose = (event) => {
            console.log("Disconnected from WebSocket server.");
            if (!event.wasClean) {
                errorElement.textContent = 'WebSocket connection closed unexpectedly. Reconnecting...';
                setTimeout(connectWebSocket, 3000); 
            }
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                // Handle prediction response
                if (data.prediction) {
                    predictionElement.textContent = data.prediction;
                } else if (data.error) {
                    errorElement.textContent = data.error;
                    console.error("Backend error:", data.error);
                }
            } catch (error) {
                errorElement.textContent = 'Error processing the WebSocket message.';
                console.error('Error parsing WebSocket message:', error);
            }
        };
    }

    connectWebSocket(); 

    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            videoElement.srcObject = stream;
        })
        .catch((err) => {
            errorElement.textContent = 'Error accessing webcam: ' + err;
        });

    function captureFrame() {
        const context = canvas.getContext('2d');
        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

        const dataUrl = canvas.toDataURL('image/jpeg');

        if (socket.readyState === WebSocket.OPEN) {
            const message = JSON.stringify({ image: dataUrl });
            socket.send(message);
        } else {
            errorElement.textContent = 'WebSocket connection is not open. Attempting to reconnect...';
        }
    }

    setInterval(captureFrame, 100); 
});
