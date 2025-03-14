import os
import yt_dlp
from flask import Flask, request, jsonify, send_from_directory, render_template_string

# Initialize Flask app
app = Flask(__name__)

# Folder to store the downloaded videos
DOWNLOAD_FOLDER = 'downloads'
app.config['UPLOAD_FOLDER'] = DOWNLOAD_FOLDER
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_video(url):
    """Download video from any social media platform"""
    ydl_opts = {
        'format': 'best',
        'quiet': False,
        'noplaylist': True,
        'extractaudio': False,
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, 'temp_video.%(ext)s'),  # Save video in the download folder
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Attempting to download video from URL: {url}")
            info_dict = ydl.extract_info(url, download=True)
            video_file_path = ydl.prepare_filename(info_dict)
        
        print("[✅] Video downloaded successfully.")
        return video_file_path

    except Exception as e:
        print(f"[❌] Error: {e}")
        return None

@app.route('/')
def index():
    """Render the HTML interface for user input"""
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SNA Downloader</title>
        <!-- Bootstrap CSS link -->
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            #loading {
                display: none;
                text-align: center;
                font-size: 20px;
                color: blue;
            }
            #download-link {
                display: none;
            }
            #error-message {
                color: red;
                display: none;
            }
        </style>
    </head>
    <body class="d-flex align-items-center justify-content-center vh-100 bg-light">
        <div class="container">
            <h1 class="text-center mb-5">Welcome To SNA Video Downloader</h1>
            <h6 class="text-center mb-4">Can download from FaceBook , YouTube , TikTok , Others..</h6>
            <div class="d-flex justify-content-center">
                <form id="video-form" action="/download" method="POST" class="w-50">
                    <div class="mb-3">
                        <label for="video-url" class="form-label">Enter Video URL:</label>
                        <input type="text" id="video-url" name="url" class="form-control" placeholder="Enter URL here" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Prepare Download</button>
                </form>
            </div>

            <!-- Loading indicator -->
                <div class="d-flex justify-content-center align-items-center flex-column">
                    <div id="loading" class="mt-2">
                        <p>Loading... Please wait while we prepare your download.</p>
                    </div>

                    <!-- Download link section -->
                    <div id="download-link" class="mt-2">
                        <p>Video download ready! Click the link below to download:</p>
                        <a id="download-button" href="#" class="btn btn-success w-100" download>Download Video</a>
                    </div>

                    <!-- Error message section -->
                    <div id="error-message" class="mt-3">
                        <p>Error downloading video. Please try again.</p>
                    </div>
                </div>
                <footer class="text-center mt-5">
                    <p>&copy; 2025 <a href="https://t.me/oppasna">SNA</a>
                        . All rights reserved.</p>
                </footer>
        </div>

        <!-- Bootstrap JS link -->
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            document.getElementById('video-form').addEventListener('submit', async function (event) {
                event.preventDefault();
                const url = document.getElementById('video-url').value;

                // Show the loading indicator
                document.getElementById('loading').style.display = 'block';
                document.getElementById('download-link').style.display = 'none';
                document.getElementById('error-message').style.display = 'none';

                // Make the POST request to the server
                const response = await fetch('/download', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: url })
                });

                const result = await response.json();
                document.getElementById('loading').style.display = 'none'; // Hide loading

                if (result.success) {
                    // Show the download link
                    document.getElementById('download-link').style.display = 'block';
                    document.getElementById('download-button').href = result.download_url;
                    document.getElementById('error-message').style.display = 'none';
                } else {
                    // Show the error message
                    document.getElementById('error-message').style.display = 'block';
                    document.getElementById('download-link').style.display = 'none';
                }
            });
        </script>
    </body>
    </html>
    """)

@app.route('/download', methods=['POST'])
def download():
    """Handle the video URL submission"""
    data = request.get_json()
    video_url = data.get('url')
    
    if video_url and video_url.lower().startswith("http"):
        video_file_path = download_video(video_url)
        
        if video_file_path:
            filename = os.path.basename(video_file_path)
            download_url = f"/download_file/{filename}"
            return jsonify(success=True, download_url=download_url)
        else:
            return jsonify(success=False, message="Video download failed. Please try again."), 400
    else:
        return jsonify(success=False, message="Invalid URL. Please provide a valid video URL."), 400

@app.route('/download_file/<filename>')
def download_file(filename):
    """Serve the downloaded video file"""
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
