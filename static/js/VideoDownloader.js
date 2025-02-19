class VideoDownloader {
    constructor(urlInputId, spinnerId, messageId) {
        this.urlInput = document.getElementById(urlInputId);
        this.spinner = document.getElementById(spinnerId);
        this.message = document.getElementById(messageId);
    }

    downloadVideo() {
        const url = this.urlInput.value;
        const encodedUrl = encodeURIComponent(url);

        this.showSpinner(true);

        fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: encodedUrl })
        })
        .then(response => response.json())
        .then(data => {
            this.displayMessage(data.error || data.message);
            this.showSpinner(false);
        })
        .catch(error => {
            this.displayMessage(`Error: ${error.message}`);
            this.showSpinner(false);
        });
    }

    showSpinner(isVisible) {
        this.spinner.style.display = isVisible ? "inline-block" : "none";
    }

    displayMessage(message) {
        this.message.innerText = message;
    }
}
