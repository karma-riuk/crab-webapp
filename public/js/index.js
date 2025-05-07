// Download logic
document.getElementById("downloadBtn").onclick = () => {
    const ds = document.getElementById("datasetSelect").value;
    const withCtx = document.getElementById("withContext").checked;
    const url =
        `/datasets/download/${ds}` + (withCtx ? "?withContext=true" : "");
    window.location = url;
};

// Upload logic
document.getElementById("uploadBtn").onclick = async () => {
    const type = document.getElementById("answerType").value;
    const fileInput = document.getElementById("fileInput");
    if (!fileInput.files.length) {
        return alert("Please choose a JSON file first.");
    }
    const file = fileInput.files[0];
    const form = new FormData();
    form.append("file", file);

    const res = await fetch(`/answers/submit/${type}`, {
        method: "POST",
        body: form,
    });

    const json = await res.json();
    console.log(json);
    const statusEl = document.getElementById("status");
    if (res.ok) {
        statusEl.style.color = "green";
        statusEl.textContent = json.message || "Upload succeeded!";
    } else {
        statusEl.style.color = "red";
        statusEl.textContent =
            json.error + (json.message ? ": " + json.message : "");
    }
};
