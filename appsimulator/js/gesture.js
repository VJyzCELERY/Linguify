document.addEventListener('DOMContentLoaded', function() {
    const videoElement = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const textOutElement = document.querySelector('.textout'); 
    const errorElement = document.getElementById('error');

    let socket = null; 

    function initWebSocket() {
        socket = new WebSocket('ws://localhost:8002'); 

        socket.onopen = () => {
            console.log("Connected to Gesture WebSocket server.");
        };

        socket.onerror = (error) => {
            errorElement.textContent = 'WebSocket error: ' + error.message;
            console.error("WebSocket Error:", error);
        };

        socket.onclose = () => {
            console.log("Disconnected from Gesture WebSocket server.");
            setTimeout(initWebSocket, 5000);  
        };

        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.prediction) { 
                    textOutElement.innerHTML = `${data.prediction}`;
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
    }

    initWebSocket();

    navigator.mediaDevices.getUserMedia({ video: true })
        .then((stream) => {
            videoElement.srcObject = stream;
        })
        .catch((err) => {
            errorElement.textContent = 'Error accessing webcam: ' + err;
        });

    function captureFrame() {
        if (!canvas) {
            console.error("Canvas element is not available for drawing.");
            return;
        }

        const context = canvas.getContext('2d');
        if (!context) {
            console.error("Failed to get canvas context.");
            return;
        }

        canvas.width = videoElement.videoWidth;
        canvas.height = videoElement.videoHeight;

        context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

        const dataUrl = canvas.toDataURL('image/jpeg');
        console.log("Sending Image Data URL:", dataUrl); 

        if (socket && socket.readyState === WebSocket.OPEN) {
            const message = JSON.stringify({ image: dataUrl });
            socket.send(message);
        } else {
            console.error("WebSocket is not open. Attempting to reconnect.");
            if (socket.readyState !== WebSocket.CONNECTING) {
                initWebSocket();  
            }
        }
    }

    setInterval(captureFrame, 100);
});
