document.getElementById("videoForm").onsubmit = async (e) => {
    e.preventDefault();
    let url = document.getElementById("video_url").value;
    
    let response = await fetch("/download_video", {
        method: "POST",
        body: new URLSearchParams({ video_url: url }),
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });

    let result = await response.json();
    alert(result.message || result.error);
};

document.getElementById("photoForm").onsubmit = async (e) => {
    e.preventDefault();
    let url = document.getElementById("photo_url").value;
    let filename = document.getElementById("photo_filename").value;

    let response = await fetch("/download_photo", {
        method: "POST",
        body: new URLSearchParams({ photo_url: url, filename: filename }),
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });

    if (response.ok) {
        let blob = await response.blob();
        let a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = filename || "image.jpg";
        a.click();
    } else {
        alert("Error downloading photo.");
    }
};

document.getElementById("qrForm").onsubmit = async (e) => {
    e.preventDefault();
    let link = document.getElementById("qr_link").value;

    let response = await fetch("/generate_qr", {
        method: "POST",
        body: new URLSearchParams({ qr_link: link }),
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
    });

    if (response.ok) {
        let blob = await response.blob();
        let a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "qrcode.png";
        a.click();
    } else {
        alert("Error generating QR Code.");
    }
};
