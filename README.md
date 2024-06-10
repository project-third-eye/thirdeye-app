# ThirdEye-App

ThirdEye is an AI-based online proctoring tool developed by a team of engineering students. It uses the lightweight and fast Flask framework alongside the YOLO object detection model to perform its tasks.

## Project Overview

Conventional online exam tools typically rely solely on the laptop's webcam for proctoring. This allows students to exploit blind spots near the laptop screen, which can drastically affect the quality of the exam. Consequently, students who cheat can achieve better results than those who work hard.

The main idea behind ThirdEye is to use the students' mobile phones as secondary cameras. When placed beside the student's shoulder, the mobile phone can easily cover blind spots that the laptop's webcam cannot reach. 

## Key Features

1. **Dual Camera Proctoring**:
   - Utilizes both the laptop's webcam and the student's mobile phone for comprehensive monitoring.
   - Covers blind spots that a single camera setup would miss.

2. **Object Detection**:
   - Detects objects such as mobile phones, books, and multiple persons.
   - Issues warnings to students in the form of a 3-second beep when unauthorized objects or multiple persons are detected.

3. **Real-Time Monitoring**:
   - Performs real-time object detection.
   - Conducts student recognition through the laptop's webcam using the `face_recognition` module.

## Technical Details

- **Framework**: Flask
- **Object Detection Model**: YOLO
- **Face Recognition Module**: `face_recognition`
- **Database**: MongoDB
- **Front End**: HTML, CSS, JavaScript

## Benefits

- **Enhanced Exam Integrity**: By covering more angles and detecting unauthorized objects, ThirdEye helps maintain the integrity of online exams.
- **Fair Assessment**: Ensures that students who work hard are not disadvantaged by those who attempt to cheat.
- **Cost Cutting**: Using a mobile phone as the secondary camera can decrease the overall cost since new webcams are not bought.
  
## How to Use

1. **Setup**: Install the necessary dependencies and set up the Flask server.
2. **Application Setup**:
   - Download any IP webcam app and connect the laptop and mobile phone to the same WiFi network (Droidcam app used for project purposes).
   - Open the app and type the address of the mobile phone into the ThirdEye app.
3. **Image Capturing**: An image of the student at the time of the exam is taken and this image is used for training and verification.
4. **Mobile Phone Placement**: Place the mobile phone beside the student's shoulder to cover blind spots.
5. **Start Proctoring**: Launch the application to begin monitoring during exams.

---

This project aims to provide a more secure and fair online examination environment by leveraging AI and multi-camera setups. Your contributions and feedback are welcome!
