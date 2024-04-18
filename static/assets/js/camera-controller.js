class CameraControler {
    async loadCameras(onCam) {
        const constraints = { video: true, audio: false };
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        const devices = await navigator.mediaDevices.enumerateDevices();
        if (onCam) {
            for (let i = 0; i < devices.length; i++) {
                let device = devices[i];
                if (device.kind == "videoinput") {
                    // cams.appendChild(new Option(device.label, device.deviceId));
                    onCam(device);
                }
            }
        }
        const tracks = stream.getTracks(); // stop the camera to avoid the NotReadableError
        for (let i = 0; i < tracks.length; i++) {
            const track = tracks[i];
            track.stop();
        }
    }

    async startCamera(videoComponent, cameraId, resolution) {
        this.stopCamera();
        this.video = videoComponent;
        if (!this.video) {
            throw "Not video component was given";
        }
        if (!(this.video instanceof HTMLVideoElement)) {
            throw "The given component is not a video component";
        }

        this.video.style.display = "block";
        let constraints = {};
        if (cameraId) {
            constraints = {
                video: { deviceId: cameraId },
                audio: false,
            };
        } else {
            constraints = {
                video: {
                    width: 1280,
                    height: 720,
                    facingMode: { exact: "environment" },
                },
                audio: false,
            };
        }
        if (resolution) {
            const res = resolution.split("x");
            const width = parseInt(res[0]);
            const height = parseInt(res[1]);

            constraints["video"]["width"] = width;
            constraints["video"]["height"] = height;
        }
        try {
            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;
        } catch (err) {
            console.error("getUserMediaError", err, err.stack);
        }
    }

    stopCamera() {
        try {
            if (this.stream) {
                const tracks = this.stream.getTracks();
                for (let i = 0; i < tracks.length; i++) {
                    const track = tracks[i];
                    track.stop();
                }
            }
        } catch (e) {
            alert(e.message);
        }
    }

    captureFrame() {
        const w = this.video.videoWidth;
        const h = this.video.videoHeight;
        const canvas = document.createElement("canvas");
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(this.video, 0, 0, w, h);
        return canvas.toDataURL("image/jpeg");
    }
}
