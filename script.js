const startBtn = document.getElementById('startButton');
const stopBtn = document.getElementById('stopButton');
const cameraStatus = document.getElementById('cameraStatus');
const video = document.getElementById('videoElement');
const gestureInput = document.getElementById('gestureInput');
const sentenceInput = document.getElementById('sentenceInput');
const gestureFeedback = document.getElementById('gestureFeedback');

let stream = null;
let recognitionInterval = null;

startBtn.addEventListener('click', async () => {
  try {
    cameraStatus.textContent = 'Initializing Camera...';
    stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    await video.play();
    cameraStatus.textContent = 'Camera is Ready!';
    startBtn.style.display = 'none';
    stopBtn.style.display = 'inline-block';
    startRecognitionLoop();
  } catch (err) {
    console.error('Error accessing camera:', err);
    cameraStatus.textContent = 'Failed to access camera.';
  }
});

stopBtn.addEventListener('click', async () => {
  stopRecognitionLoop();
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
  cameraStatus.textContent = 'Camera stopped.';
  startBtn.style.display = 'inline-block';
  stopBtn.style.display = 'none';

  try {
    const res = await fetch('/stop', { method: 'POST' });
    const data = await res.json();
    if (data.final_sentence) {
      gestureFeedback.textContent = `Final Sentence: ${data.final_sentence}`;
      sentenceInput.value = data.final_sentence;
      gestureInput.value = '';
    }
  } catch (err) {
    console.error('Error finalizing sentence:', err);
  }
});

document.addEventListener('keydown', async (e) => {
  if (e.code === 'Space') {
    e.preventDefault();
    try {
      await fetch('/space', { method: 'POST' });
      gestureFeedback.textContent = 'Word finalized and space added.';
      gestureInput.value = '';
    } catch (err) {
      console.error('Error sending space:', err);
    }
  }
});

function startRecognitionLoop() {
  recognitionInterval = setInterval(() => {
    captureFrameAndRecognize();
  }, 2000);
}

function stopRecognitionLoop() {
  if (recognitionInterval) {
    clearInterval(recognitionInterval);
    recognitionInterval = null;
  }
}

function captureFrameAndRecognize() {
  if (!video.videoWidth || !video.videoHeight) return;

  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  const imageData = canvas.toDataURL('image/jpeg');

  fetch('/recognize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: imageData }),
  })
    .then(res => res.json())
    .then(data => {
      if (data.gesture) {
        gestureInput.value = data.gesture;
        gestureFeedback.textContent = `Detected Letter: ${data.gesture}`;
        const audio = new Audio('https://www.soundjay.com/button/beep-07.wav');
        audio.play();
      }
      if (data.current_sentence) {
        sentenceInput.value = data.current_sentence;
      }
    })
    .catch(err => {
      console.error('Error recognizing gesture:', err);
    });
}

const speakBtn = document.getElementById('speakButton');

speakBtn.addEventListener('click', () => {
  const text = sentenceInput.value;
  if (!text.trim()) {
    gestureFeedback.textContent = 'No sentence to speak!';
    return;
  }

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'en-US'; // or 'en-IN' for Indian accent
  utterance.pitch = 1;
  utterance.rate = 1;
  utterance.volume = 1;

  speechSynthesis.speak(utterance);
});

