import os
import re
import subprocess
from pytubefix import YouTube
import urllib.parse
from flask import Flask, render_template, request, jsonify

# Initialize Flask app
app = Flask(__name__)

# Function to sanitize video titles
def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "_", title)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    raw_url = urllib.parse.unquote(data.get('url')).strip()
    print(f"Received video URL: {raw_url}")

    # Parse the URL for video ID (e.g., `?v=video_id`)
    parsed_url = urllib.parse.urlparse(raw_url)
    video_id = urllib.parse.parse_qs(parsed_url.query).get('v', [None])[0]

    if not video_id:
        return jsonify({"error": "Invalid video URL."}), 400

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"Cleaned video URL: {video_url}")

    # Initialize the output folder
    output_folder = './downloads/video'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        # Use the client 'WEB' to enable PoToken support
        video = YouTube(video_url, client='WEB')

        # Get the highest resolution video stream (adaptive stream)
        video_stream = video.streams.filter(progressive=False, only_video=True).order_by("resolution").last()

        # Get the highest audio stream
        audio_stream = video.streams.filter(progressive=False, only_audio=True).first()

        if video_stream and audio_stream:
            video_title = sanitize_filename(video.title)
            numbered_title = f"{video_title}"
            print(f"Downloading: {video.title}")

            # Download video and audio separately
            video_stream.download(output_path=output_folder, filename=f"{numbered_title}_video.mp4")
            audio_stream.download(output_path=output_folder, filename=f"{numbered_title}_audio.mp4")

            # Combine video and audio using ffmpeg
            video_path = os.path.join(output_folder, f"{numbered_title}_video.mp4")
            audio_path = os.path.join(output_folder, f"{numbered_title}_audio.mp4")
            output_path = os.path.join(output_folder, f"{numbered_title}.mp4")

            # Use ffmpeg to combine video and audio
            subprocess.run([
                'ffmpeg', '-i', video_path, '-i', audio_path, '-c:v', 'libx264', '-c:a', 'aac', '-strict',
                'experimental', '-preset', 'fast', output_path
            ])

            # Remove the temporary video and audio files
            os.remove(video_path)
            os.remove(audio_path)

            print(f"Downloaded and combined: {video.title}")
        else:
            print(f"Video or audio stream not found for {video.title}")

        return jsonify({"message": f"Downloaded video from {video_url}."})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
