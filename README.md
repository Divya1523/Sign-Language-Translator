The Sign Language Translator is an AI-powered system designed to bridge communication gaps between the deaf community and non-signers. It captures hand gestures through cameras and uses machine learning and NLP to convert them into text or speech. With real-time translation, Text-to-Speech (TTS), and a user-friendly interface, the tool promotes accessible and inclusive communication. Future enhancements include multi-language support and smart assistant integration, making it a scalable and intelligent solution for everyday interactions.

Approach:
Use Mediapipe to extract hand landmarks
Classify gesture using ML model trained on American Sign Language dataset and built using LSTM (Tensorflow & Keras)
Display recognized text on web UI
Add speech output using Web Speech API

Tools & Technologies:
Python (Flask), OpenCV, Mediapipe
Tensorflow and Keras for ML classifier
HTML, CSS, JavaScript for UI
Google Speech API & Easy GUI (for audio in other modules)
