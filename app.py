import os
import yt_dlp
from flask import Flask, request, jsonify, Response, render_template_string

# Initialize Flask app
app = Flask(__name__)

# Create a directory to store downloaded videos
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_video(url):
    """Download video from any social media platform to a temporary file."""
    ydl_opts = {
        'format': 'best',
        'quiet': False,
        'noplaylist': True,
        'extractaudio': False,
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
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
            <h6 class="text-center mb-4">Can download from FaceBook, YouTube, TikTok, Others..</h6>
            <div class="d-flex justify-content-center">
                <form id="video-form" action="/download" method="POST" class="w-50">
                    <div class="mb-3">
                        <label for="video-url" class="form-label">Enter Video URL:</label>
                        <input type="text" id="video-url" name="url" class="form-control" placeholder="Enter URL here" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Prepare Download</button>
                </form>
            </div>

            <div class="d-flex justify-content-center align-items-center flex-column">
                <div id="loading" class="mt-2">
                    <p>Loading... Please wait while we prepare your download.</p>
                </div>

                <div id="download-link" class="mt-2">
                    <p>Video download ready! Click the link below to download:</p>
                    <a id="download-button" href="#" class="btn btn-success w-100" download>Download Video</a>
                </div>

                <div id="error-message" class="mt-3">
                    <p>Error downloading video. Please try again.</p>
                </div>
            </div>
            <footer class="text-center mt-5">
                <p>&copy; 2025 <a href="https://t.me/oppasna">SNA</a>. All rights reserved.</p>
            </footer>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            document.getElementById('video-form').addEventListener('submit', async function (event) {
                event.preventDefault();
                const url = document.getElementById('video-url').value;

                document.getElementById('loading').style.display = 'block';
                document.getElementById('download-link').style.display = 'none';
                document.getElementById('error-message').style.display = 'none';

                const response = await fetch('/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });

                const result = await response.json();
                document.getElementById('loading').style.display = 'none';

                if (result.success) {
                    document.getElementById('download-link').style.display = 'block';
                    document.getElementById('download-button').href = result.download_url;
                } else {
                    document.getElementById('error-message').style.display = 'block';
                }
            });
        </script>
    </body>
    </html>
    """)

@app.route('/download', methods=['POST'])
def download():
    """Handle the video URL submission and prepare for download"""
    data = request.get_json()
    video_url = data.get('url')

    if video_url and video_url.lower().startswith("http"):
        video_file_path = download_video(video_url)

        if video_file_path:
            return jsonify(success=True, download_url=f"/stream/{os.path.basename(video_file_path)}")
        else:
            return jsonify(success=False, message="Video download failed. Please try again."), 400
    else:
        return jsonify(success=False, message="Invalid URL. Please provide a valid video URL."), 400

@app.route('/stream/<filename>')
def stream(filename):
    """Stream the downloaded video and delete it afterward"""
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)

    if not os.path.exists(file_path):
        return jsonify(success=False, message="File not found"), 404

    def generate():
        with open(file_path, 'rb') as video_file:
            yield from video_file
        os.remove(file_path)  # Delete after streaming

    return Response(generate(), mimetype="video/mp4", headers={"Content-Disposition": f"attachment; filename={filename}"})

if __name__ == '__main__':
    app.run(debug=True)
