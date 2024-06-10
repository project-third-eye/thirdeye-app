from flask import Flask, render_template
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd

app = Flask(__name__)

# Function to capture audio from microphone
def record_audio(duration=16*60, fs=44100):
    print("Recording...")
    audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    print("Recording finished")
    return audio_data.flatten()

# Function to detect noise
def detect_noise(audio_data, threshold=0.1):
    # Compute the absolute amplitude of the audio data
    amplitude = np.abs(audio_data)
    # Check if any amplitude exceeds the threshold
    is_noise = any(amplitude > threshold)
    return is_noise

# Route to display the webpage
@app.route('/')
def index():
    return render_template('index.html')

# Route to get and display the noise data
@app.route('/noise_data')
def noise_data():
    # Record audio for 5 seconds
    audio_data = record_audio()
    # Detect noise
    is_noise = detect_noise(audio_data)
    # Plot the audio data
    plt.plot(audio_data)
    plt.xlabel('Sample')
    plt.ylabel('Amplitude')
    plt.title('Audio Data')
    plt.grid(True)
    plt.savefig('static/audio_plot.png')
    plt.close()
    # Return whether noise is detected
    return render_template('sound.html', is_noise=is_noise)

if __name__ == '__main__':
    app.run(debug=True)
