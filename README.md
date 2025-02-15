# EduBot Project  

## Overview  
EduBot is a comprehensive educational system designed to support children with learning difficulties, such as those with Down syndrome. It integrates a humanoid robot (NAO V6) with various external hardware components. The system facilitates personalized learning experiences through interactive activities it provide instruction, request actions, and give feedback to children in real-time.  

## Features  
- **Hand Gesture Recognition:** Utilizes MediaPipe for recognizing hand gestures via a Dragon Camera connected to a Raspberry Pi.
- **Color Detection:** Uses OpenCV to detect colors, allowing children to engage in activities that involve color recognition.  
- **Interactive Learning:** Involves an ESP32 microcontroller with RC522 sensor and push buttons to engage children in learning activities.  
- **Real-Time Monitoring:** Streams camera view to a web application in **Finger Counting** activity for monitoring by educators.  
- **Feedback Mechanism:** The robot communicates requests and provides feedback based on the child's actions and responses through diffrent system components.  

## Web Application  
The EduBot system features a web application developed using the **Django** framework. This application serves as the primary interface for educators to monitor children's progress and manage learning activities.  

### Key Technologies  
- **Django:** A robust web framework that enables rapid development of secure and maintainable websites.  
- **Bulma:** A modern CSS framework that provides a responsive and user-friendly interface for seamless interaction.  
- **JavaScript and HTML:** Used to enhance frontend functionality and interactivity.  

### Educator Features  
- **Monitor Progress:** Educators can view real-time data on the child’s engagement and interaction with the EduBot.  
- **Activity Selection:** The application allows teachers to select learning activities based on the child’s preferences and progress.  
- **Management Dashboard:** Facilitates managing all components of the EduBot system, including setting up tasks, reviewing outputs, and adjusting settings.  

## Hardware Components  
### 1. **NAO V6 Robot**
   - Provides personalized instructions to children during activities.  
   - Delivers real-time feedback based on child responses, enhancing engagement.
### 2. **Raspberry Pi with Dragon Camera**  
   - Used for hand gesture recognition and finger counting using the MediaPipe model.  
   - Streams live video feed to a web interface for educator monitoring.  

### 3. **ESP32 Microcontroller**  
   - Integrates with RC522 sensor and push buttons.  
   - Detects different images and conducts learning activities through button interactions.  

## Communication Protocols  
- **IoT Communication:** Facilitated using MQTT for efficient message delivery between components.  
- **Web Application:** Employs HTTP protocol for communication between the Raspberry Pi camera feed and the educator's monitoring interface.  

## Development Environment  
The following IDEs and environments are used for development and testing:  
- **Arduino IDE:** Used for programming the ESP32 with the RC522 sensor and push buttons.  
- **Visual Studio Code (VS Code):** Employed for web application development, providing a powerful code editor with extensions for Django and frontend technologies.  
- **Jupyter Notebook:** Used for testing and experimenting with the MediaPipe model, allowing for interactive coding and visualization.  
- **Raspberry Pi OS:** The operating system running on the Raspberry Pi, which executes the MediaPipe code for hand gesture recognition and streams the video to the web application during the finger counting game.  
