import cv2
import numpy as np
import mediapipe as mp
import time
from model.keypoint_classifier.keypoint_classifier import KeyPointClassifier
import csv
import base64

class GestureRecognizer:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )
        self.keypoint_classifier = KeyPointClassifier()
        with open("model/keypoint_classifier/keypoint_classifier_label.csv", encoding="utf-8-sig") as f:
            self.labels = [row[0] for row in csv.reader(f)]

        self.current_word = []
        self.current_sentence = []
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.5
        self.last_hand_detected = False
        self.hand_appeared_time = None
        self.hand_appear_wait = 1.5
        self.gesture_ready = False

    def reset(self):
        self.current_word = []
        self.current_sentence = []
        self.last_gesture_time = 0
        self.last_hand_detected = False
        self.hand_appeared_time = None
        self.gesture_ready = False

    def decode_image(self, img_base64):
        header, encoded = img_base64.split(',', 1)
        img_bytes = base64.b64decode(encoded)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        img = cv2.flip(img, 1)
        return img

    def recognize(self, img_base64):
        img = self.decode_image(img_base64)
        current_time = time.time()
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)

        hand_detected = results.multi_hand_landmarks is not None
        gesture = None

        if hand_detected:
            if not self.last_hand_detected:
                self.hand_appeared_time = current_time
                self.gesture_ready = False

            if self.hand_appeared_time and (current_time - self.hand_appeared_time >= self.hand_appear_wait):
                self.gesture_ready = True

            if self.gesture_ready and (current_time - self.last_gesture_time >= self.gesture_cooldown):
                for hand_landmarks in results.multi_hand_landmarks:
                    landmark_list = []
                    for landmark in hand_landmarks.landmark:
                        x = min(int(landmark.x * img.shape[1]), img.shape[1] - 1)
                        y = min(int(landmark.y * img.shape[0]), img.shape[0] - 1)
                        landmark_list.append([x, y])

                    base_x, base_y = landmark_list[0]
                    relative_landmarks = [[x - base_x, y - base_y] for x, y in landmark_list]
                    flat_landmarks = np.array(relative_landmarks).flatten()
                    max_val = max(np.max(np.abs(flat_landmarks)), 1)
                    normalized_landmarks = (flat_landmarks / max_val).tolist()

                    gesture_id = self.keypoint_classifier(normalized_landmarks)
                    gesture = self.labels[gesture_id]

                    self.current_word.append(gesture)

                    self.last_gesture_time = current_time
                    self.gesture_ready = False
                    break

        else:
            self.hand_appeared_time = None
            self.gesture_ready = False

        self.last_hand_detected = hand_detected

        return {
            "gesture": gesture,
            "current_word": "".join(self.current_word),
            "current_sentence": " ".join(self.current_sentence),
        }

    def finalize_word(self):
        """Used on spacebar press — adds current word to sentence but keeps state alive."""
        if self.current_word:
            word = "".join(self.current_word)
            self.current_sentence.append(word)
            self.current_word = []

    def finalize_sentence(self):
        """Used on escape key press — finalizes everything and resets state."""
        self.finalize_word()
        final_sentence = " ".join(self.current_sentence)
        self.reset()
        return final_sentence
