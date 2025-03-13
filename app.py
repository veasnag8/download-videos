import os
import yt_dlp
import requests
import qrcode
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

# Ensure download folders exist
os.makedirs("downloads/videos", exist_ok=True)
os.makedirs("downloads/photos", exist_ok=True)
os.makedirs("downloads/qrcodes", exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download_video", methods=["POST"])
def download_video():
    url = request.form.get("video_url")
    if not url:
        return {"error": "Invalid URL"}, 400
    
    ydl_opts = {
        'outtmpl': 'downloads/videos/%(title)s.%(ext)s',
        'format': 'best'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        return {"message": "Download complete!", "filename": filename}
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/download_photo", methods=["POST"])
def download_photo():
    url = request.form.get("photo_url")
    filename = request.form.get("filename") or "image"

    if not url:
        return {"error": "Invalid URL"}, 400

    filepath = f"downloads/photos/{filename}.jpg"
    response = requests.get(url)
    with open(filepath, "wb") as file:
        file.write(response.content)

    return send_file(filepath, as_attachment=True)

@app.route("/generate_qr", methods=["POST"])
def generate_qr():
    link = request.form.get("qr_link")
    if not link:
        return {"error": "Invalid link"}, 400

    qr = qrcode.make(link)
    qr_path = "downloads/qrcodes/qrcode.png"
    qr.save(qr_path)

    return send_file(qr_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
