import cv2
from cvzone.HandTrackingModule import HandDetector
from time import sleep, time
import numpy as np
import cvzone
from pynput.keyboard import Controller, Key
import json
import os

class AdvancedVirtualKeyboard:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1280)
        self.cap.set(4, 720)
        
        self.detector = HandDetector(detectionCon=0.8, maxHands=2)
        self.keyboard = Controller()
        
        # Keyboard layouts
        self.layouts = {
            'qwerty': {
                'name': 'QWERTY',
                'keys': [
                    ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "⌫"],
                    ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"],
                    ["Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Enter"],
                    ["Shift", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Shift"],
                    ["Ctrl", "Win", "Alt", "Space", "Alt", "Win", "Menu", "Ctrl"]
                ]
            },
            'numeric': {
                'name': 'NUMERIC',
                'keys': [
                    ["7", "8", "9", "/"],
                    ["4", "5", "6", "*"],
                    ["1", "2", "3", "-"],
                    ["0", ".", "=", "+"]
                ]
            },
            'symbols': {
                'name': 'SYMBOLS',
                'keys': [
                    ["!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", "⌫"],
                    ["Tab", "~", "`", "|", "\\", "{", "}", "[", "]", ":", ";", "'", "Enter"],
                    ["Caps", "<", ">", "?", "/", "=", "+", "-", "*", "&", "|", "Enter"],
                    ["Shift", "Space", "Space", "Space", "Space", "Space", "Space", "Shift"]
                ]
            }
        }
        
        self.current_layout = 'qwerty'
        self.caps_lock = False
        self.shift_pressed = False
        self.final_text = ""
        self.text_history = []
        self.settings = {
            'sensitivity': 30,
            'click_delay': 0.3,
            'show_distance': True,
            'show_landmarks': True,
            'theme': 'dark'
        }
        
        self.button_list = []
        self.create_buttons()
        
        # Gesture tracking
        self.gesture_history = []
        self.last_click_time = 0
        self.last_layout_switch_time = 0
        self.double_click_threshold = 0.5
        
        # Visual effects
        self.particles = []
        self.click_effects = []
        
    def create_buttons(self):
        self.button_list = []
        keys = self.layouts[self.current_layout]['keys']
        
        for i, row in enumerate(keys):
            for j, key in enumerate(row):
                # Adjust button sizes based on key type
                if key in ['Space']:
                    size = [200, 85]
                elif key in ['Enter', 'Shift', 'Caps', 'Tab']:
                    size = [120, 85]
                elif key in ['Ctrl', 'Alt', 'Win', 'Menu']:
                    size = [100, 85]
                else:
                    size = [85, 85]
                
                x = 100 * j + 50
                y = 100 * i + 50
                self.button_list.append(Button([x, y], key, size))
    
    def draw_advanced_ui(self, img):
        # Draw background gradient
        height, width = img.shape[:2]
        gradient = np.zeros((height, width, 3), dtype=np.uint8)
        
        if self.settings['theme'] == 'dark':
            for i in range(height):
                color = int(30 + (i / height) * 20)
                gradient[i, :] = [color, color, color]
        else:
            for i in range(height):
                color = int(200 - (i / height) * 50)
                gradient[i, :] = [color, color, color]
        
        img = cv2.addWeighted(img, 0.7, gradient, 0.3, 0)
        
        # Draw buttons with advanced styling
        for button in self.button_list:
            x, y = button.pos
            w, h = button.size
            
            # Button background with gradient
            if button.is_hovered:
                cv2.rectangle(img, (x-2, y-2), (x + w + 2, y + h + 2), (100, 100, 255), 2)
                cv2.rectangle(img, button.pos, (x + w, y + h), (150, 150, 255), cv2.FILLED)
            elif button.is_pressed:
                cv2.rectangle(img, (x-2, y-2), (x + w + 2, y + h + 2), (0, 255, 0), 2)
                cv2.rectangle(img, button.pos, (x + w, y + h), (0, 200, 0), cv2.FILLED)
            else:
                cvzone.cornerRect(img, (x, y, w, h), 15, rt=0, colorR=(255, 0, 255))
                cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
            
            # Text styling
            text_size = cv2.getTextSize(button.text, cv2.FONT_HERSHEY_PLAIN, 2, 3)[0]
            text_x = x + (w - text_size[0]) // 2
            text_y = y + (h + text_size[1]) // 2
            
            cv2.putText(img, button.text, (text_x, text_y),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)
        
        # Draw text display area
        cv2.rectangle(img, (50, 350), (1200, 450), (50, 50, 50), cv2.FILLED)
        cv2.rectangle(img, (50, 350), (1200, 450), (255, 255, 255), 2)
        
        # Display current text with word wrap
        words = self.final_text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + word) < 50:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        for i, line in enumerate(lines[-2:]):  # Show last 2 lines
            cv2.putText(img, line, (60, 400 + i * 30),
                        cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        
        # Draw status bar
        status_text = f"Layout: {self.layouts[self.current_layout]['name']} | Caps: {'ON' if self.caps_lock else 'OFF'} | Shift: {'ON' if self.shift_pressed else 'OFF'}"
        cv2.rectangle(img, (50, 500), (1200, 530), (30, 30, 30), cv2.FILLED)
        cv2.putText(img, status_text, (60, 520),
                    cv2.FONT_HERSHEY_PLAIN, 1, (200, 200, 200), 1)
        
        # Draw settings panel
        self.draw_settings_panel(img)
        
        return img
    
    def draw_settings_panel(self, img):
        # Settings button
        cv2.rectangle(img, (1100, 50), (1200, 100), (100, 100, 100), cv2.FILLED)
        cv2.putText(img, "SETTINGS", (1110, 80),
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2)
        
        # Layout switcher
        cv2.rectangle(img, (1100, 120), (1200, 170), (80, 80, 80), cv2.FILLED)
        cv2.putText(img, "LAYOUT", (1110, 150),
                    cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2)
    
    def process_hand_gestures(self, hands, img):
        if not hands:
            return
        
        # Process first hand
        hand = hands[0]
        lm_list = hand['lmList']
        bbox = hand['bbox']
        
        # Reset button states
        for button in self.button_list:
            button.is_hovered = False
            button.is_pressed = False
        
        # Check button interactions
        if lm_list:
            index_tip = lm_list[8]
            
            for button in self.button_list:
                x, y = button.pos
                w, h = button.size
                
                if x < index_tip[0] < x + w and y < index_tip[1] < y + h:
                    button.is_hovered = True
                    
                    # Check for click gesture
                    # Get landmark points for index and middle finger tips
                    index_tip = lm_list[8]
                    middle_tip = lm_list[12]
                    
                    # Calculate distance between fingertips
                    l = np.sqrt((index_tip[0] - middle_tip[0])**2 + (index_tip[1] - middle_tip[1])**2)
                    
                    # Draw distance line if enabled
                    if self.settings['show_distance']:
                        cv2.line(img, (int(index_tip[0]), int(index_tip[1])), 
                                (int(middle_tip[0]), int(middle_tip[1])), (255, 0, 0), 2)
                        cv2.putText(img, f'{int(l)}', (int((index_tip[0] + middle_tip[0])/2), 
                                int((index_tip[1] + middle_tip[1])/2)), 
                                cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2)
                    
                    if l < self.settings['sensitivity']:
                        button.is_pressed = True
                        self.handle_button_click(button)
        
        # Process second hand for gestures
        if len(hands) >= 2:
            self.process_two_hand_gestures(hands, img)
    
    def process_two_hand_gestures(self, hands, img):
        # Two-hand gestures for special functions
        hand1, hand2 = hands[0], hands[1]
        
        # Calculate distance between hands using wrist positions
        hand1_wrist = hand1['lmList'][0]  # Wrist landmark
        hand2_wrist = hand2['lmList'][0]  # Wrist landmark
        
        distance = np.sqrt((hand1_wrist[0] - hand2_wrist[0])**2 + 
                          (hand1_wrist[1] - hand2_wrist[1])**2)
        
        # Draw line between hands if distance is small
        if distance < 200:
            cv2.line(img, (int(hand1_wrist[0]), int(hand1_wrist[1])), 
                    (int(hand2_wrist[0]), int(hand2_wrist[1])), (0, 255, 0), 3)
            cv2.putText(img, f'Layout Switch: {int(distance)}', (50, 50), 
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
        
        # Swipe gesture to change layout
        current_time = time()
        if distance < 100 and current_time - self.last_layout_switch_time > 2.0:  # Hands close together
            self.cycle_layout()
            self.last_layout_switch_time = current_time
    
    def handle_button_click(self, button):
        current_time = time()
        
        if current_time - self.last_click_time < self.settings['click_delay']:
            return
        
        self.last_click_time = current_time
        
        # Handle special keys
        if button.text == '⌫':
            if self.final_text:
                self.final_text = self.final_text[:-1]
        elif button.text == 'Space':
            self.final_text += ' '
        elif button.text == 'Enter':
            self.final_text += '\n'
            self.text_history.append(self.final_text)
        elif button.text == 'Caps':
            self.caps_lock = not self.caps_lock
        elif button.text == 'Shift':
            self.shift_pressed = not self.shift_pressed
        elif button.text == 'Tab':
            self.final_text += '    '
        elif button.text in ['Ctrl', 'Alt', 'Win', 'Menu']:
            # Handle modifier keys
            pass
        else:
            # Regular character
            char = button.text
            
            # Apply caps lock and shift
            if self.caps_lock or self.shift_pressed:
                char = char.upper()
            else:
                char = char.lower()
            
            self.final_text += char
            self.keyboard.press(char)
        
        # Add click effect
        self.add_click_effect(button.pos)
    
    def add_click_effect(self, pos):
        effect = {
            'pos': pos,
            'time': time(),
            'particles': []
        }
        
        # Create particle effect
        for _ in range(10):
            particle = {
                'x': pos[0] + np.random.randint(-20, 20),
                'y': pos[1] + np.random.randint(-20, 20),
                'vx': np.random.randint(-5, 5),
                'vy': np.random.randint(-5, 5),
                'life': 1.0
            }
            effect['particles'].append(particle)
        
        self.click_effects.append(effect)
    
    def update_effects(self, img):
        current_time = time()
        
        # Update click effects
        for effect in self.click_effects[:]:
            if current_time - effect['time'] > 1.0:
                self.click_effects.remove(effect)
                continue
            
            for particle in effect['particles']:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['life'] -= 0.02
                
                if particle['life'] > 0:
                    alpha = int(255 * particle['life'])
                    cv2.circle(img, (int(particle['x']), int(particle['y'])), 
                              2, (0, 255, 255, alpha), -1)
    
    def cycle_layout(self):
        layouts = list(self.layouts.keys())
        current_index = layouts.index(self.current_layout)
        self.current_layout = layouts[(current_index + 1) % len(layouts)]
        self.create_buttons()
    
    def save_text(self):
        if self.final_text:
            with open('keyboard_output.txt', 'w', encoding='utf-8') as f:
                f.write(self.final_text)
    
    def run(self):
        while True:
            success, img = self.cap.read()
            if not success:
                break
            
            # Flip image for mirror effect
            img = cv2.flip(img, 1)
            
            # Detect hands
            hands, img = self.detector.findHands(img, draw=self.settings['show_landmarks'])
            
            # Process gestures
            self.process_hand_gestures(hands, img)
            
            # Draw UI
            img = self.draw_advanced_ui(img)
            
            # Update effects
            self.update_effects(img)
            
            # Show image
            cv2.imshow("Advanced Virtual Keyboard", img)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self.save_text()
            elif key == ord('l'):
                self.cycle_layout()
            elif key == ord('c'):
                self.final_text = ""
        
        self.cap.release()
        cv2.destroyAllWindows()

class Button:
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text
        self.is_hovered = False
        self.is_pressed = False

if __name__ == "__main__":
    keyboard = AdvancedVirtualKeyboard()
    keyboard.run()


