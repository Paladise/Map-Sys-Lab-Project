class Webcam {
    constructor(webcamElement, facingMode = 'user') {
        this._webcamElement = webcamElement;
        this._facingMode = facingMode;
        this._webcamList = [];
        this._streamList = [];
        this._selectedDeviceId = '';
    }

    get facingMode() {
        return this._facingMode;
    }

    set facingMode(value) {
        this._facingMode = value;
    }

    get webcamList() {
        return this._webcamList;
    }

    get webcamCount() {
        return this._webcamList.length;
    }

    get selectedDeviceId() {
        return this._selectedDeviceId;
    }

    /* Get all video input devices info */
    getVideoInputs(mediaDevices) {
        this._webcamList = [];
        mediaDevices.forEach(mediaDevice => {
            if (mediaDevice.kind === 'videoinput') {
                this._webcamList.push(mediaDevice);
            }
        });
        if (this._webcamList.length == 1) {
            this._facingMode = 'user';
        }
        return this._webcamList;
    }

    /* Get media constraints */
    getMediaConstraints() {
        var videoConstraints = {};
        if (this._selectedDeviceId == '') {
            videoConstraints.facingMode = this._facingMode;
        } else {
            videoConstraints.deviceId = {
                exact: this._selectedDeviceId
            };
        }
        var constraints = {
            video: videoConstraints,
            audio: false
        };
        return constraints;
    }

    /* Select camera based on facingMode */
    selectCamera() {
        for (let webcam of this._webcamList) {
            if ((this._facingMode == 'user' && webcam.label.toLowerCase().includes('front')) ||
                (this._facingMode == 'environment' && webcam.label.toLowerCase().includes('back'))
            ) {
                this._selectedDeviceId = webcam.deviceId;
                break;
            }
        }
    }

    /* Change Facing mode and selected camera */
    flip() {
        this._facingMode = (this._facingMode == 'user') ? 'environment' : 'user';
        this._webcamElement.style.transform = "";
        this.selectCamera();
    }

    /*
      1. Get permission from user
      2. Get all video input devices info
      3. Select camera based on facingMode 
      4. Start stream
    */
    async start(startStream = true) {
        return new Promise((resolve, reject) => {
            this.stop();
            navigator.mediaDevices.getUserMedia(this.getMediaConstraints()) //get permisson from user
                .then(stream => {
                    this._streamList.push(stream);
                    this.info() //get all video input devices info
                        .then(webcams => {
                            this.selectCamera(); //select camera based on facingMode
                            if (startStream) {
                                this.stream()
                                    .then(facingMode => {
                                        resolve(this._facingMode);
                                    })
                                    .catch(error => {
                                        reject(error);
                                    });
                            } else {
                                resolve(this._selectedDeviceId);
                            }
                        })
                        .catch(error => {
                            reject(error);
                        });
                })
                .catch(error => {
                    reject(error);
                });
        });
    }

    /* Get all video input devices info */
    async info() {
        return new Promise((resolve, reject) => {
            navigator.mediaDevices.enumerateDevices()
                .then(devices => {
                    this.getVideoInputs(devices);
                    resolve(this._webcamList);
                })
                .catch(error => {
                    reject(error);
                });
        });
    }

    /* Start streaming webcam to video element */
    async stream() {
        return new Promise((resolve, reject) => {
            navigator.mediaDevices.getUserMedia(this.getMediaConstraints())
                .then(stream => {
                    this._streamList.push(stream);
                    this._webcamElement.srcObject = stream;
                    if (this._facingMode == 'user') {
                        this._webcamElement.style.transform = "scale(-1,1)";
                    }
                    this._webcamElement.play();
                    resolve(this._facingMode);
                })
                .catch(error => {
                    console.log(error);
                    reject(error);
                });
        });
    }

    /* Stop streaming webcam */
    stop() {
        this._streamList.forEach(stream => {
            stream.getTracks().forEach(track => {
                track.stop();
            });
        });
    }

    snap() {  
        let canvasElement = document.createElement("canvas");
        canvasElement.width = webcamElement.getBoundingClientRect().width;
        canvasElement.height = webcamElement.getBoundingClientRect().height;
        console.log(canvasElement.width);
        console.log(canvasElement.height);
        let context = canvasElement.getContext('2d');
        if (this._facingMode == 'user') {
            context.translate(canvasElement.width, 0);
            context.scale(-1, 1);
        }
        context.clearRect(0, 0, canvasElement.width, canvasElement.height);
        context.drawImage(this._webcamElement, 0, 0, canvasElement.width, canvasElement.height);
        let data = canvasElement.toDataURL('image/png');
        canvasElement.remove();
        console.log(data);
        var input = document.createElement("input");
        
        input.type = "hidden";
        input.name = "floor" + (form.children.length - 1);
        input.value = data;
        form.insertBefore(input, form.children[form.children.length - 1]);        
        return data;
    }
}

const webcamElement = document.getElementById('webcam');
const webcam = new Webcam(webcamElement, 'user');
const pictureButton = document.getElementById('takePicture');
const flipButton = document.getElementById('flipCamera');
const form = document.getElementById("processingForm");
webcam.start()
    .then(result => {
        console.log("webcam started");
    })
    .catch(err => {
        console.log(err);
    });

pictureButton.addEventListener("click", function() {
    console.log("Took picture");
    let picture = webcam.snap();
    // pictureButton.href = picture;
});

flipButton.addEventListener("click", function() {
    console.log("Flipped camera");
    webcam.flip();
    webcam.start();
})