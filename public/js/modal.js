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

["download", "upload", "results"].forEach((section) => {
    window[`info-${section}-btn`].addEventListener("click", () => {
        show_modal_with(window[`info-${section}`].content.cloneNode(true));
    });
});
