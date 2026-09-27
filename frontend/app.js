const $ = (id) => document.getElementById(id);

let selectedUploadFiles = [];
let uploadController = null;


/* =========================
   FILE SELECTION
========================= */

$("files").addEventListener("change", () => {

    selectedUploadFiles =
        Array.from($("files").files);

    displaySelectedFiles();
});


/* =========================
   FOLDER SELECTION
========================= */

$("folder").addEventListener("change", () => {

    selectedUploadFiles =
        Array.from($("folder").files);

    displaySelectedFolder();
});


/* =========================
   DISPLAY NORMAL FILES
========================= */

function displaySelectedFiles() {

    const container =
        $("selectedFiles");

    container.replaceChildren();


    if (!selectedUploadFiles.length) {

        container.textContent =
            "No files selected";

        return;
    }


    const supportedFiles =
        selectedUploadFiles.filter(file =>
            isSupportedFile(file.name)
        );


    if (!supportedFiles.length) {

        container.textContent =
            "No supported files selected.";

        return;
    }


    /* File count */

    const fileCount =
        document.createElement("div");

    fileCount.className =
        "file-summary";

    fileCount.textContent =
        `${supportedFiles.length} supported file(s)`;


    container.appendChild(
        fileCount
    );


    /* File preview */

    const preview =
        document.createElement("div");

    preview.className =
        "file-preview";


    for (
        const file of supportedFiles.slice(0, 8)
    ) {

        const item =
            document.createElement("div");

        item.className =
            "selected-file";


        const icon =
            document.createElement("span");

        icon.className =
            "file-icon";

        icon.textContent =
            "📄";


        const name =
            document.createElement("span");

        name.className =
            "file-name";

        name.textContent =
            file.name;


        item.appendChild(icon);

        item.appendChild(name);

        preview.appendChild(item);
    }


    container.appendChild(
        preview
    );


    if (supportedFiles.length > 8) {

        const more =
            document.createElement("div");

        more.className =
            "more-files";

        more.textContent =
            `+ ${supportedFiles.length - 8} more`;


        container.appendChild(
            more
        );
    }
}


/* =========================
   DISPLAY SELECTED FOLDER
========================= */

function displaySelectedFolder() {

    const container =
        $("selectedFiles");

    container.replaceChildren();


    if (!selectedUploadFiles.length) {

        container.textContent =
            "No folder selected";

        return;
    }


    /* =========================
       FILTER SUPPORTED FILES
    ========================= */

    const supportedFiles =
        selectedUploadFiles.filter(file =>
            isSupportedFile(file.name)
        );


    if (!supportedFiles.length) {

        container.textContent =
            "No supported files in this folder.";

        return;
    }


    /* =========================
       GET FOLDER NAME
    ========================= */

    let folderName =
        "Selected folder";


    const firstFile =
        supportedFiles[0];


    const relativePath =
        firstFile.webkitRelativePath;


    if (relativePath) {

        const parts =
            relativePath.split("/");


        if (parts.length > 1) {

            folderName =
                parts[0];
        }
    }


    /* =========================
       FOLDER HEADER
    ========================= */

    const folderHeader =
        document.createElement("div");

    folderHeader.className =
        "folder-header";


    const folderIcon =
        document.createElement("span");

    folderIcon.className =
        "folder-icon";

    folderIcon.textContent =
        "📁";


    const folderNameElement =
        document.createElement("strong");

    folderNameElement.textContent =
        folderName;


    folderHeader.appendChild(
        folderIcon
    );

    folderHeader.appendChild(
        folderNameElement
    );


    container.appendChild(
        folderHeader
    );


    /* =========================
       FILE COUNT
    ========================= */

    const fileCount =
        document.createElement("div");

    fileCount.className =
        "file-summary";

    fileCount.textContent =
        `${supportedFiles.length} supported file(s)`;


    container.appendChild(
        fileCount
    );


    /* =========================
       FILE PREVIEW
    ========================= */

    const preview =
        document.createElement("div");

    preview.className =
        "file-preview";


    for (
        const file of supportedFiles.slice(0, 8)
    ) {

        const item =
            document.createElement("div");

        item.className =
            "selected-file";


        const icon =
            document.createElement("span");

        icon.className =
            "file-icon";

        icon.textContent =
            "📄";


        const name =
            document.createElement("span");

        name.className =
            "file-name";


        /*
         * Show complete relative path
         *
         * Example:
         *
         * ai-codebase-assistant-v2/app/main.py
         */

        name.textContent =
            file.webkitRelativePath ||
            file.name;


        item.appendChild(
            icon
        );

        item.appendChild(
            name
        );


        preview.appendChild(
            item
        );
    }


    container.appendChild(
        preview
    );


    /* =========================
       MORE FILES
    ========================= */

    if (supportedFiles.length > 8) {

        const more =
            document.createElement("div");

        more.className =
            "more-files";

        more.textContent =
            `+ ${supportedFiles.length - 8} more`;


        container.appendChild(
            more
        );
    }
}


/* =========================
   SUPPORTED FILE CHECK
========================= */

function isSupportedFile(filename) {

    const supportedExtensions = [

        ".py",
        ".js",
        ".ts",

        ".java",

        ".c",
        ".cpp",
        ".h",
        ".hpp",

        ".sql",

        ".html",
        ".css",

        ".md",
        ".txt",

        ".pdf",

        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".xml"
    ];


    const lower =
        filename.toLowerCase();


    /*
     * Dockerfile has no extension
     */

    if (
        lower === "dockerfile"
    ) {
        return true;
    }


    return supportedExtensions.some(
        extension =>
            lower.endsWith(extension)
    );
}


/* =========================
   INDEX SAMPLE PROJECT
========================= */

$("indexBtn").onclick = async () => {

    $("indexStatus").textContent =
        "Indexing...";


    try {

        const r =
            await fetch(
                "/api/index-folder",
                {
                    method: "POST"
                }
            );


        const data =
            await r.json();


        if (!r.ok) {

            $("indexStatus").textContent =
                data.detail ||
                "Indexing failed.";

            return;
        }


        $("indexStatus").textContent =
            `Indexed ${data.indexed_files} files and ${data.indexed_chunks} chunks.`;


        updateStats(
            data.indexed_files,
            data.indexed_chunks
        );


    } catch (error) {

        $("indexStatus").textContent =
            "Indexing failed: " +
            error.message;
    }
};


/* =========================
   UPLOAD FILES / FOLDER
========================= */

$("uploadBtn").onclick = async () => {

    const files =
        selectedUploadFiles;


    if (!files.length) {

        $("uploadStatus").textContent =
            "Please select files or a folder first.";

        return;
    }


    /* =========================
       CREATE ABORT CONTROLLER
    ========================= */

    uploadController =
        new AbortController();


    $("uploadBtn").disabled =
        true;

    $("cancelUploadBtn").disabled =
        false;


    $("uploadStatus").textContent =
        `Uploading ${files.length} file(s)...`;


    try {

        const form =
            new FormData();


        /* =========================
           ADD FILES TO FORM DATA
        ========================= */

        for (
            const file of files
        ) {

            /*
             * IMPORTANT:
             *
             * For folder uploads,
             * preserve the relative path.
             *
             * Example:
             *
             * project/app/main.py
             *
             * instead of:
             *
             * main.py
             */

            form.append(
                "files",
                file,
                file.webkitRelativePath ||
                file.name
            );
        }


        /* =========================
           SEND TO BACKEND
        ========================= */

        const r =
            await fetch(
                "/api/upload",
                {
                    method: "POST",

                    body: form,

                    signal:
                        uploadController.signal
                }
            );


        const data =
            await r.json();


        /* =========================
           HANDLE ERROR
        ========================= */

        if (!r.ok) {

            $("uploadStatus").textContent =
                data.detail ||
                "Upload failed.";

            return;
        }


        /* =========================
           SUCCESS
        ========================= */

        $("uploadStatus").textContent =
            `Indexed ${data.indexed_files} files and ${data.indexed_chunks} chunks.`;


        updateStats(
            data.indexed_files,
            data.indexed_chunks
        );


        /*
         * Do NOT clear the selected files.
         *
         * This keeps the folder name
         * and file list visible.
         */


    } catch (error) {

        if (
            error.name ===
            "AbortError"
        ) {

            $("uploadStatus").textContent =
                "Upload cancelled.";

        } else {

            $("uploadStatus").textContent =
                "Upload failed: " +
                error.message;
        }

    } finally {

        uploadController =
            null;


        $("uploadBtn").disabled =
            false;


        $("cancelUploadBtn").disabled =
            true;
    }
};


/* =========================
   CANCEL UPLOAD
========================= */

$("cancelUploadBtn").onclick = () => {

    if (uploadController) {

        uploadController.abort();
    }
};


/* =========================
   ASK QUESTION
========================= */

$("askBtn").onclick = async () => {

    const question =
        $("question").value.trim();


    if (!question) {
        return;
    }


    $("answer").textContent =
        "Thinking...";


    $("sources").replaceChildren();


    try {

        const r =
            await fetch(
                "/api/ask",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        question:
                            question,

                        top_k:
                            5
                    })
                }
            );


        const data =
            await r.json();


        if (!r.ok) {

            $("answer").textContent =
                data.detail ||
                "Request failed.";

            return;
        }


        $("answer").textContent =
            data.answer;


        /* =========================
           SOURCES
        ========================= */

        for (
            const source of data.sources
        ) {

            const li =
                document.createElement(
                    "li"
                );


            if (
                source.page
            ) {

                li.textContent =
                    `${source.path} — Page ${source.page}`;

            } else {

                li.textContent =
                    `${source.path}:${source.start_line}-${source.end_line}`;
            }


            $("sources").appendChild(
                li
            );
        }


    } catch (error) {

        $("answer").textContent =
            "Request failed: " +
            error.message;
    }
};


/* =========================
   UPDATE SIDEBAR STATS
========================= */

function updateStats(
    files,
    chunks
) {

    $("fileCount").textContent =
        files;

    $("chunkCount").textContent =
        chunks;
}