const socket = io();

const progressContainer = document.getElementById("progress-container");
const progressBar = document.getElementById("progress-bar");
const progressText = document.getElementById("progress-text");
const statusEl = document.getElementById("status");

const resultsContainer = document.getElementById("results-container");

let results = {};

// Download logic
document.getElementById("download-dataset").onclick = () => {
    const ds = document.getElementById("dataset-select").value;
    const withCtx = document.getElementById("with-context").checked;
    const url =
        `/datasets/download/${ds}` + (withCtx ? "?withContext=true" : "");
    window.location = url;
};

// Upload logic
document.getElementById("upload-btn").onclick = async () => {
    const type = document.getElementById("answer-cype").value;
    const fileInput = document.getElementById("file-cnput");
    if (!fileInput.files.length) {
        return alert("Please choose a JSON file first.");
    }
    const file = fileInput.files[0];
    const form = new FormData();
    form.append("file", file);

    const res = await fetch(`/answers/submit/${type}`, {
        headers: {
            "X-Socket-Id": socket.id,
        },
        method: "POST",
        body: form,
    });

    const json = await res.json();
    if (!res.ok) {
        statusEl.style.color = "red";
        statusEl.textContent =
            json.error + (json.message ? ": " + json.message : "");
        return;
    }

    results = json;
    progressContainer.style.display = "none";
    resultsContainer.style.display = "block";

    const tbody = resultsContainer.querySelector("table tbody");
    tbody.innerHTML = "";

    Object.entries(results).forEach(([id, info]) => {
        const row = tbody.insertRow(); // create a new row
        const idCell = row.insertCell(); // cell 1: id
        const commentCell = row.insertCell(); // cell 2: proposed comment
        const scoreCell = row.insertCell(); // cell 3: bleu score

        idCell.textContent = id;
        commentCell.innerHTML = `<span class='comment-cell'>${info["proposed_comment"]}</span>`;
        scoreCell.textContent = info["max_bleu_score"];
    });
};

document.getElementById("download-results").onclick = () => {
    const dataStr =
        "data:text/json;charset=utf-8," +
        encodeURIComponent(JSON.stringify(results));
    const dlAnchorElem = document.createElement("a");
    dlAnchorElem.setAttribute("href", dataStr);
    dlAnchorElem.setAttribute("download", "results.json");
    document.body.appendChild(dlAnchorElem);
    dlAnchorElem.click();
    document.body.removeChild(dlAnchorElem);
};

function setProgress(percent) {
    progressBar.value = percent;
    progressText.textContent = `${percent}%`;
}

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

socket.on("successul-upload", () => {
    statusEl.style.color = "green";
    statusEl.textContent = "Upload succeeded!";
});
