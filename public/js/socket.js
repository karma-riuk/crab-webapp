const socket = io();

// 2) Grab our new DOM elements
const progressContainer = document.getElementById("progress-container");
const progressBar = document.getElementById("progress-bar");
const progressText = document.getElementById("progress-text");
const statusEl = document.getElementById("status");

function setProgress(percent) {
    progressBar.value = percent;
    progressText.textContent = `${percent}%`;
}

// 3) Update UI on each progress message
socket.on("progress", (data) => {
    setProgress(data.percent);
    if (data.percent == 100) {
        statusEl.style.color = "green";
        statusEl.textContent = "Processing complete!";
    }
});

socket.on("started-processing", () => {
    progressContainer.style.display = "block";
    setProgress(0);
});
