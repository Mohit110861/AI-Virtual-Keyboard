# AI-Virtual-Keyboard

This project is made by Vinit Mehra, Linu Shibu, and Siddharth Sawhney for the Artificial Intelligence Course.  
It bridges the real world and augmented environments by creating a virtual keyboard system using OpenCV and Python.  
The system allows users to control a virtual keyboard using finger movements detected by a webcam, enabling gesture-based typing without additional hardware.

---

## Issue in existing system

Virtual Reality (VR) devices and technologies often overlook accessibility for disabled or especially-abled people.  
Traditional input devices (keyboard, mouse) are being supplemented by new interaction methods like touch screens and sensors, but many lack simple, camera-based gesture interfaces.

---

## Problem statement

With the proliferation of small cameras in phones and tablets, researchers have explored using cameras as substitutes for physical keyboards.  
A camera captures hand movements, and software interprets keystrokes in real-time by analyzing images from various angles.

---

## Objective

- Develop a virtual keyboard capable of detecting hand gestures to type letters.
- Use OpenCV, MediaPipe, and cvzone to detect hand position and gestures.
- Use pynput to simulate keyboard input and type the detected letters.
- Move beyond physical mechanical keyboards to gesture-based input methods.

---

## Proposed Methodology

### Keyboard Layout Model  
Create a QWERTY keyboard layout using OpenCV drawing functions, overlayed as a semi-transparent virtual keyboard on the webcam feed.

### Palm Detection Model  
Use MediaPipe’s palm detection to locate hands with bounding boxes, enabling accurate hand tracking and occlusion handling.

### Hand Detection Model  
Use MediaPipe’s hand landmark model to identify 21 key 3D points on the hand for precise finger tracking.

### Click Detection  
Measure the distance between landmarks 8 (index finger tip) and 12 (middle finger tip) to detect clicking gestures.  
When the distance is below a threshold, interpret it as a key press, identify the corresponding key, and append it to the typed text.

---

## Screenshot of demo

![image](https://github.com/vinit714/AI-Virtual-Keyboard/assets/52816788/f90b74b9-a1c3-4fbc-b9cf-b693512c1daf)

---

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/AI-Virtual-Keyboard.git
cd AI-Virtual-Keyboard
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
pip install opencv-python mediapipe cvzone pynput numpy
python virtual_keyboard.py
Libraries Used
opencv-python: For webcam video capture and drawing the keyboard layout.

mediapipe: For hand and palm detection and tracking.

cvzone: Wrapper over MediaPipe and OpenCV to simplify hand tracking functions.

pynput: To simulate keyboard presses programmatically.

numpy: Numerical operations and array manipulations.
