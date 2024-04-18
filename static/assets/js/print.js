async function printPDF(url, scale = 1) {
    // const pdfjsLib = window["pdfjs-dist/build/pdf"];

    // pdfjsLib.GlobalWorkerOptions.workerSrc = '//mozilla.github.io/pdf.js/build/pdf.worker.js';
    pdfjsLib.GlobalWorkerOptions.workerSrc = "/static/libs/pdf/pdf.worker.mjs";

    const pdf = await pdfjsLib.getDocument(url).promise;
    const totalPages = pdf.numPages;

    const content = document.body;
    document.body = document.createElement("body");
    for (let pageNumber = 1; pageNumber <= totalPages; pageNumber++) {
        const page = await pdf.getPage(pageNumber);
        const viewport = page.getViewport({ scale: scale });

        const canvas = document.createElement("canvas");
        document.body.appendChild(canvas);
        const context = canvas.getContext("2d");
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        const renderContext = {
            canvasContext: context,
            viewport: viewport,
        };
        await page.render(renderContext).promise;
    }
    window.print();
    document.body = content;
}
