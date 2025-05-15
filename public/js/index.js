const socket = io();

const progressContainer = document.getElementById("progress-container");
const progressBar = document.getElementById("progress-bar");
const progressText = document.getElementById("progress-text");
const statusEl = document.getElementById("status");

const commentResultsContainer = document.querySelector(
    ".results-container#comment",
);
const refinementResultsContainer = document.querySelector(
    ".results-container#refinement",
);

const tick = "✅";
const cross = "❌";

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
    statusEl.classList.add("hidden");
    progressContainer.classList.add("hidden");

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
    progressContainer.classList.add("hidden");

    commentResultsContainer.classList.add("hidden");
    refinementResultsContainer.classList.add("hidden");
    const resultsContainer =
        type === "comment"
            ? commentResultsContainer
            : refinementResultsContainer;

    resultsContainer.classList.remove("hidden");

    const tbody = resultsContainer.querySelector("table tbody");
    tbody.innerHTML = "";

    Object.entries(results).forEach(([id, info]) => {
        const row = tbody.insertRow(); // create a new row
        const idCell = row.insertCell(); // cell 1: id
        idCell.textContent = id;

        if (type == "comment") {
            const commentCell = row.insertCell();
            const scoreCell = row.insertCell();

            const span = document.createElement("span");
            span.className = "comment-cell";
            span.textContent = info["proposed_comment"];
            commentCell.appendChild(span);
            scoreCell.textContent = info["max_bleu_score"].toFixed(2);
        } else {
            const compiledCell = row.insertCell();
            const testedCell = row.insertCell();

            compiledCell.textContent =
                info["compilation"] || false ? tick : cross;
            testedCell.textContent = info["test"] || false ? tick : cross;
        }
    });
};

[...document.getElementsByClassName("download-results")].forEach((e) => {
    e.onclick = () => {
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
});

function setProgress(percent) {
    progressContainer.classList.remove("hidden");
    progressBar.value = percent;
    progressText.textContent = `${percent.toFixed(0)}%`;
}

socket.on("progress", (data) => {
    setProgress(data.percent);
    if (data.percent == 100) {
        statusEl.style.color = "green";
        statusEl.textContent = "Processing complete!";
    }
});

socket.on("started-processing", () => {
    setProgress(0);
});

socket.on("successful-upload", () => {
    statusEl.classList.remove("hidden");
    statusEl.style.color = "green";
    statusEl.textContent = "Upload succeeded!";
});

// INFO-MODAL LOGIC
const aboutButton = document.getElementById("about-button");
const modalOverlay = document.getElementById("modal-overlay");
const modalContent = document.getElementById("modal-content");
const modalClose = document.getElementById("modal-close");

function show_modal_with(content) {
    modalOverlay.classList.remove("hidden");
    modalContent.innerHTML = "";
    modalContent.appendChild(content);
    modalOverlay.focus();
}

// open modal
aboutButton.addEventListener("click", () => {
    show_modal_with(about.content.cloneNode(true));
});

// close modal via “×” button
modalClose.addEventListener("click", () => {
    modalOverlay.classList.add("hidden");
});

// also close if you click outside the white box
modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) {
        modalOverlay.classList.add("hidden");
    }
});

modalOverlay.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        modalOverlay.classList.add("hidden");
        console.log("hiding");
    }
});

window["info-download-btn"].addEventListener("click", (e) => {
    show_modal_with(window["info-download"].content.cloneNode(true));
});

document.getElementById("request-status").onclick = () => {
    url.reportValidity();
};
