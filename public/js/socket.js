const socket = io();

// 2) Grab our new DOM elements
const progressContainer = document.getElementById("progress-container");
const progressBar = document.getElementById("progress-bar");
const progressText = document.getElementById("progress-text");
const statusEl = document.getElementById("status");

const resultsContainer = document.getElementById("results-container");

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

socket.on("ended-processing", (data) => {
    resultsContainer.style.display = "block";
    // empty the table besides the header of the table and fill the table. the data is of form id:
    // {"proposed comment": "bla bla bla", "bleu score": 0.2}

    const table = resultsContainer.querySelector("table");

    // remove all the rows besides the table header
    while (table.rows.length > 1) {
        table.deleteRow(1);
    }

    Object.entries(data).forEach(([id, info]) => {
        const row = table.insertRow(); // create a new row
        const idCell = row.insertCell(); // cell 1: id
        const commentCell = row.insertCell(); // cell 2: proposed comment
        const scoreCell = row.insertCell(); // cell 3: bleu score

        idCell.textContent = id;
        commentCell.textContent = info["proposed comment"];
        scoreCell.textContent = info["max bleu score"].toFixed(4);
    });
});
