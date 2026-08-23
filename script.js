const API_URL = "http://127.0.0.1:8000";

async function uploadArtwork() {

    const fileInput = document.getElementById("artwork");
    const category = document.getElementById("category").value;
    const message = document.getElementById("message");

    if (fileInput.files.length === 0) {
        message.textContent = "Please select an image.";
        return;
    }

    const formData = new FormData();

    formData.append("file", fileInput.files[0]);
    formData.append("category", category);

    message.textContent = "Uploading...";

    try {

        const response = await fetch(`${API_URL}/upload`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail);
        }

        message.textContent = "Artwork uploaded successfully!";

        fileInput.value = "";

        loadArtwork();

    } catch (error) {

        message.textContent = "Upload failed: " + error.message;

    }
}


async function loadArtwork() {

    const gallery = document.getElementById("gallery");

    try {

        const response = await fetch(`${API_URL}/artworks`);

        const artworks = await response.json();

        gallery.innerHTML = "";

        artworks.forEach(artwork => {

            const card = document.createElement("div");

            card.className = "card";

            card.innerHTML = `
                <img src="${API_URL}${artwork.image_url}">
                <h3>${artwork.filename}</h3>
                <p>Category: ${artwork.category}</p>
            `;

            gallery.appendChild(card);

        });

    } catch (error) {

        gallery.innerHTML = "<p>Could not load artwork.</p>";

    }
}


loadArtwork();