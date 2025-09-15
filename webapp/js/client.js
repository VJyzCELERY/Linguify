let socket;
let displayDiv = document.getElementById('textDisplay');
let notification = document.getElementById('notification');
let server_available = false;
let mic_available = false;
let fullSentences = [];
let isMuted = false;
const resetbutton = document.getElementById('resetbutton');
const savebutton = document.getElementById('savebutton');
const micbutton = document.getElementById('micbutton');
let isSaving = false;
let mediaStream = null;


function reset() {
    fullSentences = [];
    let transcription = document.querySelectorAll(`span[id=transcript]`);
    let realtime = document.querySelectorAll(`span[class=realtime]`);
    transcription.forEach(span => span.remove());
    realtime.forEach(span => span.remove());
}

resetbutton.onclick = () => reset();
savebutton.onclick = () => saveTranscript();

function connectToServer() {
    socket = new WebSocket("ws://localhost:8001");

    socket.onopen = function(event) {
        server_available = true;
        program_status();
        console.log("WebSocket connection established");
    };

    socket.onclose = function(event) {
        server_available = false;
        console.log("WebSocket connection closed");
    };

    socket.onerror = function(event) {
        console.error("WebSocket error observed:", event);
    };

    socket.onmessage = function(event) {
        console.log("Raw message received:", event.data);
        
        let rawMessage = event.data.trim();
        
        try {
            let data = JSON.parse(rawMessage);
    
            if (data && data.type) {
                if (data.type === 'realtime') {
                    displayRealtimeText(data.text, displayDiv);
                } else if (data.type === 'fullSentence') {
                    fullSentences.push(data.text);
                    displayRealtimeText("", displayDiv);
                }
            } else {
                console.error("Received data doesn't contain a valid 'type' field:", data);
            }
        } catch (e) {
            console.error("Error parsing message:", e);
            console.log("Received data (unparsed):", rawMessage);
            rawMessage = event.data.trim();
    
            const jsonMatch = rawMessage.match(/^{.*}$/); 
            if (jsonMatch) {
                try {
                    let data = JSON.parse(jsonMatch[0]);
                    console.log("Extracted JSON data:", data);
                    if (data && data.type) {
                        if (data.type === 'realtime') {
                            displayRealtimeText(data.text, displayDiv);
                        } else if (data.type === 'fullSentence') {
                            fullSentences.push(data.text);
                            displayRealtimeText("", displayDiv);
                        }
                    }
                } catch (extractionError) {
                    
                    console.error("Error parsing extracted JSON:", extractionError);
                }
            } else {
                console.log("No valid JSON found in the message.");
            }
        }
    };
}

const serverCheckInterval = 3000;
setInterval(() => {
    if (!server_available) {
        connectToServer();
    }
}, serverCheckInterval);

function program_status() {
    if (!mic_available)
        notification.innerHTML = "Please allow microphone access";
    else if (!server_available)
        notification.innerHTML = "Server not available";
    else if(isMuted)
        notification.innerHTML = "Muted";
    else
        notification.innerHTML = "🎙️Reading sound input🎙️";
}

function displayRealtimeText(realtimeText, displayDiv) {
    displayDiv.innerHTML = "";
    fullSentences.forEach((sentence, index) => {
      let span = document.createElement('span');
      span.textContent = sentence + " ";
      span.contentEditable = true; 
      span.id = "transcript";
      span.className = index % 2 === 0 ? 'even' : 'odd';
  
      span.addEventListener('input', () => {
        fullSentences[index] = span.textContent.trim(); 
  
        if (socket && socket.readyState === WebSocket.OPEN) {
          socket.send(
            JSON.stringify({
              type: 'update',
              sentences: fullSentences,
            })
          );
        }
      });
  
      displayDiv.appendChild(span);
    });
  
    if (realtimeText) {
      let realtimeSpan = document.createElement('span');
      realtimeSpan.textContent = realtimeText;
      realtimeSpan.className = 'realtime';
      displayDiv.appendChild(realtimeSpan);
    }

}

function saveTranscript() {
    if (isSaving) return; 
  
    isSaving = true;
    saveTranscript();
    
    setTimeout(() => {
      isSaving = false;
    }, 1000);
    console.log("Saving transcript...");
    
    try {
      let content = '';
      const spans = document.querySelectorAll('span#transcript');
      
      spans.forEach(span => {
        content += span.innerHTML + '\n';
      });
  
      const timestamp = new Date().toISOString().replace(/[:.-]/g, '_');
      const filename = `transcript_${timestamp}.txt`;
  
      const blob = new Blob([content], { type: 'text/plain' });
  
      const link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = filename;
  
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
  
      console.log('Transcript saved successfully as:', filename);
    } catch (error) {
      console.error("Error during save operation:", error);
    }
}

function toggleMute() {
    if (mic_available && mediaStream) {
        isMuted = !isMuted;
        program_status();
        micbutton.src = isMuted ? 'asset/mute.png' : 'asset/unmute.png';

        let track = mediaStream.getTracks().find(track => track.kind === 'audio');
        if (track) {
            track.enabled = !isMuted;
        }
    }
}
micbutton.onclick = () => toggleMute();

navigator.mediaDevices.getUserMedia({ audio: true })
.then(stream => {
    mediaStream = stream; 
    audioContext = new AudioContext();
    let source = audioContext.createMediaStreamSource(stream);
    processor = audioContext.createScriptProcessor(256, 1, 1);

    source.connect(processor);
    processor.connect(audioContext.destination);
    mic_available = true;
    program_status();

    processor.onaudioprocess = function (e) {
        let inputData = e.inputBuffer.getChannelData(0);
        let outputData = new Int16Array(inputData.length); 
    
        if (isMuted) {
            outputData.fill(0);
        } else {
            for (let i = 0; i < inputData.length; i++) {
                outputData[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
            }
        }
    
        if (socket.readyState === WebSocket.OPEN) {
            let metadata = JSON.stringify({ sampleRate: audioContext.sampleRate });
            let metadataBytes = new TextEncoder().encode(metadata);
    
            let metadataLength = new Uint8Array(4);
            new DataView(metadataLength.buffer).setUint32(0, metadataBytes.length, true);
    
            let combinedBuffer = new Uint8Array(
                metadataLength.byteLength + metadataBytes.byteLength + outputData.byteLength
            );
            combinedBuffer.set(metadataLength, 0);
            combinedBuffer.set(metadataBytes, metadataLength.byteLength);
            combinedBuffer.set(new Uint8Array(outputData.buffer), metadataLength.byteLength + metadataBytes.byteLength); 
            socket.send(combinedBuffer.buffer);
        }
    };
})
.catch(e => {
    console.error("Error accessing microphone:", e);
    notification.innerHTML = "Please allow microphone access.";
    mic_available = false;
    program_status();
});