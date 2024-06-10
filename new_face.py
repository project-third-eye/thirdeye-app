import cv2
import tkinter as tk
import numpy as np
import os
import face_recognition

def main():
    # Create Tkinter window
    root = tk.Tk()
    root.title("Face Recognition")

    reference_encoding = None

    # Function to select reference image
    def select_reference_image():
        nonlocal reference_encoding
        reference_image_path = "D:/snapshot"  # Path to directory containing reference image
        reference_image_files = os.listdir(reference_image_path)
        # Filter out directories from the list of files
        reference_image_files = [file for file in reference_image_files if os.path.isfile(os.path.join(reference_image_path, file))]
        if not reference_image_files:
            print("Error: No reference image found in the directory.")
            return
        reference_image_file = os.path.join(reference_image_path, reference_image_files[0])
        reference_image = face_recognition.load_image_file(reference_image_file)
        reference_encoding = face_recognition.face_encodings(reference_image)[0]

    # Call select_reference_image() to automatically select the reference image
    select_reference_image()

    # Function to open webcam and perform face recognition
    def recognize_face():
        if reference_encoding is None:
            print("Error: No reference image selected.")
            return

        # Open webcam
        cap = cv2.VideoCapture(0)

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to capture frame")
                break

            # Convert frame to RGB (face_recognition uses RGB format)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Find all face locations and encodings in the frame
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for face_location, face_encoding in zip(face_locations, face_encodings):
                # Compare current face encoding with the reference encoding
                is_same_person = face_recognition.compare_faces([reference_encoding], face_encoding)[0]
                # Draw a rectangle around the face and display text indicating whether it's the same person
                color = (0, 255, 0) if is_same_person else (0, 0, 255)
                cv2.rectangle(frame, (face_location[3], face_location[0]), (face_location[1], face_location[2]), color, 2)
                cv2.putText(frame, "Same Person" if is_same_person else "Different Person", (face_location[3], face_location[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

            # Display the frame
            cv2.imshow('Webcam', frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the capture
        cap.release()
        cv2.destroyAllWindows()

    # Call recognize_face() to start face recognition automatically
    recognize_face()

    # Run Tkinter event loop
    root.mainloop()

if __name__ == "__main__":

    main()