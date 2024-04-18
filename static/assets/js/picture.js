async function init() {
    const camCtl = new CameraControler();

    const controls = document.getElementById("controls");
    const preview = document.getElementById("preview");
    const showImg = document.getElementById("showImg");

    const cameraSelector = document.getElementById("cameraSelector");
    const cameraResolution = document.getElementById("cameraResolution");

    const sendForm = document.getElementById("sendForm");

    const previewVideo = document.getElementById("camPreview");
    const previewPicture = document.getElementById("photoTaken");
    const formImg = document.getElementById("formImg");

    const startButton = document.getElementById("startCamBut");
    const settingsButton = document.getElementById("settingsBut");
    const captureButton = document.getElementById("captureBut");
    const recaptureButton = document.getElementById("recaptureBut");
    const acceptButton = document.getElementById("acceptBut");

    controls.style.display = "";
    preview.style.display = "none";
    showImg.style.display = "none";

    startButton.setAttribute("disabled", true);
    await camCtl.loadCameras((e) => {
        cameraSelector.appendChild(new Option(e.label, e.deviceId));
    });
    startButton.removeAttribute("disabled");

    const startCam = () => {
        try {
            const id = cameraSelector.selectedOptions[0].value;
            const res = cameraResolution.selectedOptions[0].value;

            camCtl.startCamera(previewVideo, id, res);

            controls.style.display = "none";
            preview.style.display = "";
            showImg.style.display = "none";
        } catch (err) {
            console.error("start", err);
        }
    };
    startButton.onclick = startCam;
    recaptureButton.onclick = startCam;

    settingsButton.onclick = () => {
        try {
            camCtl.stopCamera();
            controls.style.display = "";
            preview.style.display = "none";
            showImg.style.display = "none";
        } catch (err) {
            console.error("stop", err);
        }
    };
    captureButton.onclick = () => {
        try {
            const data = camCtl.captureFrame();
            camCtl.stopCamera();
            controls.style.display = "none";
            preview.style.display = "none";
            showImg.style.display = "";
            previewPicture.src = data;
            formImg.value = data;
        } catch (err) {
            console.error("capture", err);
        }
    };

    acceptButton.onclick = () => {
        if (formImg.value && formImg.value != "") {
            sendForm.submit();
        }
    };
}

window.addEventListener("load", init);
