import * as pdfjsLib from "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.10.38/pdf.min.mjs";

pdfjsLib.GlobalWorkerOptions.workerSrc =
  "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.10.38/pdf.worker.min.mjs";

const root = document.querySelector("[data-pdf-viewer]");
if (root) {
  const canvas = root.querySelector("canvas");
  const context = canvas.getContext("2d");
  const status = root.querySelector("[data-pdf-status]");
  const pageLabel = root.querySelector("[data-pdf-page]");
  const previousButton = root.querySelector("[data-pdf-prev]");
  const nextButton = root.querySelector("[data-pdf-next]");
  const zoomOutButton = root.querySelector("[data-pdf-zoom-out]");
  const zoomInButton = root.querySelector("[data-pdf-zoom-in]");
  const zoomLabel = root.querySelector("[data-pdf-zoom]");
  const downloadLink = root.querySelector("[data-pdf-download]");

  let pdf = null;
  let pageNumber = 1;
  let scale = 1;
  let rendering = false;
  let pendingPage = null;

  function updateControls() {
    pageLabel.textContent = pdf ? `${pageNumber} / ${pdf.numPages}` : "—";
    zoomLabel.textContent = `${Math.round(scale * 100)}%`;
    previousButton.disabled = !pdf || pageNumber <= 1;
    nextButton.disabled = !pdf || pageNumber >= pdf.numPages;
    zoomOutButton.disabled = scale <= 0.6;
    zoomInButton.disabled = scale >= 2.5;
  }

  async function renderPage(number) {
    if (!pdf) return;
    if (rendering) {
      pendingPage = number;
      return;
    }
    rendering = true;
    try {
      const page = await pdf.getPage(number);
      const baseViewport = page.getViewport({ scale: 1 });
      const availableWidth = Math.max(260, root.querySelector(".pdf-canvas-wrap").clientWidth - 24);
      const fitScale = Math.min(1.5, availableWidth / baseViewport.width);
      const viewport = page.getViewport({ scale: fitScale * scale });
      const pixelRatio = window.devicePixelRatio || 1;
      canvas.width = Math.floor(viewport.width * pixelRatio);
      canvas.height = Math.floor(viewport.height * pixelRatio);
      canvas.style.width = `${Math.floor(viewport.width)}px`;
      canvas.style.height = `${Math.floor(viewport.height)}px`;
      context.setTransform(pixelRatio, 0, 0, pixelRatio, 0, 0);
      await page.render({ canvasContext: context, viewport }).promise;
      status.textContent = "";
      pageNumber = number;
      updateControls();
    } catch (error) {
      console.error("PDF render error", error);
      status.textContent = "PDF көрсөтүлбөй калды. «Жүктөп алуу» баскычын колдонуңуз.";
    } finally {
      rendering = false;
      if (pendingPage !== null) {
        const next = pendingPage;
        pendingPage = null;
        renderPage(next);
      }
    }
  }

  previousButton.addEventListener("click", () => {
    if (pdf && pageNumber > 1) renderPage(pageNumber - 1);
  });
  nextButton.addEventListener("click", () => {
    if (pdf && pageNumber < pdf.numPages) renderPage(pageNumber + 1);
  });
  zoomOutButton.addEventListener("click", () => {
    scale = Math.max(0.6, Math.round((scale - 0.2) * 10) / 10);
    renderPage(pageNumber);
  });
  zoomInButton.addEventListener("click", () => {
    scale = Math.min(2.5, Math.round((scale + 0.2) * 10) / 10);
    renderPage(pageNumber);
  });

  let resizeTimer;
  window.addEventListener("resize", () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => renderPage(pageNumber), 150);
  });

  if (downloadLink) downloadLink.href = root.dataset.downloadUrl;

  pdfjsLib.getDocument({ url: root.dataset.pdfUrl }).promise
    .then((loadedPdf) => {
      pdf = loadedPdf;
      updateControls();
      renderPage(1);
    })
    .catch((error) => {
      console.error("PDF load error", error);
      status.textContent = "PDF жүктөлгөн жок. Интернет байланышын текшерип, кайра аракет кылыңыз.";
      updateControls();
    });
}
