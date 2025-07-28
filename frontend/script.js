// Define the base URL of your backend API using a relative path
const API_BASE_URL = "/api/v1";

// Get references to DOM elements
const uploadForm = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const statusMessage = document.getElementById("status-message");
const documentList = document.getElementById("document-list");

/**
 * Fetches the list of documents from the backend and displays them.
 */
async function fetchDocuments() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/documents`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const docs = await response.json();

        // Clear the current list
        documentList.innerHTML = "";

        if (docs.length === 0) {
            documentList.innerHTML = "<p>No documents uploaded yet.</p>";
            return;
        }

        // This is the single, correct loop to render each document item WITH the delete button.
        docs.forEach((doc) => {
            const docItem = document.createElement("div");
            docItem.className = "doc-item";
            docItem.innerHTML = `
                <div class="doc-details">
                    <div class="doc-name">${doc.filename}</div>
                    <div class="doc-meta">
                        Uploaded on: ${new Date(doc.upload_date).toLocaleString()} | 
                        Size: ${(doc.file_size / 1024).toFixed(2)} KB
                    </div>
                </div>
                <button class="delete-btn" data-doc-id="${doc._id}">Delete</button>
            `;
            documentList.appendChild(docItem);
        });

    } catch (error) {
        documentList.innerHTML = `<p class="status-error">Could not load documents: ${error.message}</p>`;
    }
}

/**
 * Handles the document upload form submission.
 */
async function handleUpload(event) {
    event.preventDefault(); // Prevent the form from submitting normally

    const file = fileInput.files[0];
    if (!file) {
        setStatus("Please select a file to upload.", "error");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setStatus("Uploading and processing, please wait...", "loading");

    try {
        const response = await fetch(`${API_BASE_URL}/admin/documents/upload`, {
            method: "POST",
            body: formData,
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || "Upload failed.");
        }

        setStatus(`Success! Document '${result.filename}' uploaded.`, "success");
        uploadForm.reset(); // Clear the file input
        await fetchDocuments(); // Refresh the document list

    } catch (error) {
        setStatus(`Error: ${error.message}`, "error");
    }
}

/**
 * Helper function to display status messages.
 */
function setStatus(message, type) {
    statusMessage.textContent = message;
    statusMessage.className = `status-${type}`; // Applies CSS class for color
}

// --- Event Listeners ---

// Attach the event listener to the form for uploads
uploadForm.addEventListener("submit", handleUpload);

// Initial call to load documents when the page loads
document.addEventListener("DOMContentLoaded", fetchDocuments);

// Attach a single event listener to the list for handling delete button clicks
documentList.addEventListener("click", async (event) => {
    if (event.target.classList.contains("delete-btn")) {
        const docId = event.target.dataset.docId;

        if (confirm("Are you sure you want to delete this document and all its data?")) {
            try {
                const response = await fetch(`${API_BASE_URL}/admin/documents/${docId}`, {
                    method: "DELETE",
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || "Failed to delete document.");
                }

                setStatus("Document deleted successfully.", "success");
                await fetchDocuments(); // Refresh the list

            } catch (error) {
                setStatus(`Error: ${error.message}`, "error");
            }
        }
    }
});
