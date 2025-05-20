const socket = io();

const progressContainer = document.getElementById("progress-container");
const progressBar = document.getElementById("progress-bar");
const progressText = document.getElementById("progress-text");
const uploadStatusEl = document.getElementById("upload-status");
const statusStatusEl = document.getElementById("status-status");

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

function populateCommentTable(results) {
    commentResultsContainer.classList.remove("hidden");

    const tbody = commentResultsContainer.querySelector("table tbody");
    tbody.innerHTML = "";

    Object.entries(results).forEach(([id, info]) => {
        const row = tbody.insertRow();
        const idCell = row.insertCell();
        const commentCell = row.insertCell();
        const scoreCell = row.insertCell();
        const span = document.createElement("span");

        idCell.textContent = id;
        span.className = "comment-cell";
        span.textContent = info["proposed_comment"];
        commentCell.appendChild(span);
        scoreCell.textContent = info["max_bleu_score"].toFixed(2);
    });
}

function populateRefinementTable(results) {
    refinementResultsContainer.classList.remove("hidden");

    const tbody = refinementResultsContainer.querySelector("table tbody");
    tbody.innerHTML = "";

    Object.entries(results).forEach(([id, info]) => {
        const row = tbody.insertRow();
        const idCell = row.insertCell();
        const compiledCell = row.insertCell();
        const testedCell = row.insertCell();

        idCell.textContent = id;
        compiledCell.textContent = info["compilation"] || false ? tick : cross;
        testedCell.textContent = info["test"] || false ? tick : cross;
    });
}

// Upload logic
document.getElementById("upload-btn").onclick = async () => {
    uploadStatusEl.classList.add("hidden");
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
        uploadStatusEl.classList.remove("hidden");
        uploadStatusEl.style.color = "red";
        uploadStatusEl.textContent =
            json.error + (json.message ? ": " + json.message : "");
        return;
    }

    commentResultsContainer.classList.add("hidden");
    refinementResultsContainer.classList.add("hidden");

    uploadStatusEl.classList.remove("hidden");
    uploadStatusEl.style.color = "green";
    uploadStatusEl.textContent = json["id"];

    uuid.value = json["id"];
    document.getElementById("request-status").click();
};

[...document.getElementsByClassName("download-results")].forEach((e) => {
    e.onclick = () => {
        const dataStr =
            "data:text/json;charset=utf-8," +
            encodeURIComponent(JSON.stringify(results));
        const dlAnchorElem = document.createElement("a");
        dlAnchorElem.setAttribute("href", dataStr);
        dlAnchorElem.setAttribute("download", "results.json");
        document.body.appendChild(dlAnchorElem); // required for firefox
        dlAnchorElem.click();
        dlAnchorElem.remove();
    };
});

function setProgress(percent) {
    progressContainer.classList.remove("hidden");
    progressBar.value = percent;
    progressText.textContent = `${percent.toFixed(0)}%`;
}

socket.on("progress", (data) => {
    setProgress(data.percent);
});

socket.on("started-processing", () => {
    setProgress(0);
    if (queue_position_interval != null) {
        clearTimeout(queue_position_interval);
        queue_position_interval = null;
    }
});

socket.on("changed-subject", () => {
    console.log("changed-subject");
    commentResultsContainer.classList.add("hidden");
    refinementResultsContainer.classList.add("hidden");
    progressContainer.classList.add("hidden");
});

socket.on("complete", (data) => {
    commentResultsContainer.classList.add("hidden");
    refinementResultsContainer.classList.add("hidden");
    progressContainer.classList.add("hidden");
    if (data.type == "comment") {
        commentResultsContainer.classList.remove("hidden");
        populateCommentTable(data.results);
    } else if (data.type == "refinement") {
        refinementResultsContainer.classList.remove("hidden");
        populateRefinementTable(data.results);
    } else {
        console.error(`Unknown type ${data.type}`);
    }
});

socket.on("successful-upload", () => {
    uploadStatusEl.classList.remove("hidden");
    uploadStatusEl.style.color = "green";
    uploadStatusEl.textContent = "Upload succeeded!";
});

socket.on("queue_position", (data) => {
    console.log(`got answer for queue position with ${data}`);
    if (data.status == "waiting")
        statusStatusEl.textContent = `Currently waiting, position in queue ${data.position}`;
    else {
        if (queue_position_interval != null) {
            console.log("clearing interval");
            clearTimeout(queue_position_interval);
            queue_position_interval = null;
        }
        statusStatusEl.textContent = data.status;
    }
});

let queue_position_interval = null;

document.getElementById("request-status").onclick = async () => {
    if (!uuid.reportValidity()) return;
    const res = await fetch(`/answers/status/${uuid.value}`, {
        headers: {
            "X-Socket-Id": socket.id,
        },
    });

    const json = await res.json();
    if (!res.ok) {
        statusStatusEl.classList.remove("hidden");
        statusStatusEl.style.color = "red";
        statusStatusEl.textContent = json.message ? json.message : json.error;
        return;
    }
    statusStatusEl.classList.remove("hidden");
    statusStatusEl.style.color = "green";
    statusStatusEl.textContent = json["status"];

    if (json.status == "complete") {
        commentResultsContainer.classList.add("hidden");
        refinementResultsContainer.classList.add("hidden");
        if (json.type == "comment") populateCommentTable(json.results);
        else if (json.type == "comment") populateRefinementTable(json.results);
        else console.error(`Unknown type ${data.type}`);
        // set global variable, used when user wants to download results
        results = json.results;
    } else if (json.status == "waiting") {
        statusStatusEl.textContent = `Currently waiting, position in queue ${json.queue_position}`;
        queue_position_interval = setInterval(() => {
            socket.emit("get_queue_position", { id: uuid.value });
        }, 3000);
    }
};

uuid.addEventListener("keyup", (e) => {
    if (e.key === "Enter") {
        document.getElementById("request-status").click();
    }
});

if (window.location.hash) {
    uuid.value = window.location.hash.substring(1); // remove # from hash
    document.getElementById("request-status").click();
}
