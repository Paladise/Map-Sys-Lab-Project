var floors = [];

function supported(attribute) {
    var i = document.createElement('input');
    i.setAttribute(attribute, true);
    return !!i[attribute];
}

// var input = document.getElementById("fileUpload"); 

// input.onchange = function () {
//   var file = input.files[0];

// //   drawOnCanvas(file);   
//   displayAsImage(file);
// };


function drawOnCanvas(file) {
  var reader = new FileReader();

  reader.onload = function (e) {
    var dataURL = e.target.result,
        c = document.querySelector('canvas'),
        ctx = c.getContext('2d'),
        img = new Image();

    img.onload = function() {
      c.width = img.width;
      c.height = img.height;
      ctx.drawImage(img, 0, 0);
    };

    img.src = dataURL;
  };

  reader.readAsDataURL(file);
}

function displayAsImage(file) {
  var imgURL = URL.createObjectURL(file),
      img = document.createElement('img');

  img.onload = function() {
    URL.revokeObjectURL(imgURL);
  };

  img.src = imgURL;
  document.body.appendChild(img);
}

function addFloor() {
    var num = floors.length + 1;
    floors.push(num);
    var singleContainer = document.createElement("div");
    singleContainer.classList.add("single-container");
    var secondaryContainer = document.createElement("div");
    secondaryContainer.classList.add("secondary-container");
    secondaryContainer.id = "floor" + num + "container";
    var filenameContainer = document.createElement("div");
    filenameContainer.classList.add("filename-container");
    var filename = document.createElement("p");
    filename.classList.add("filename");
    filename.id = "filename" + num;
    filename.innerHTML = "Floor " + num;
    filenameContainer.appendChild(filename);
    var uploadIcon = document.createElement("span");
    uploadIcon.classList.add("material-symbols-outlined");
    uploadIcon.classList.add("upload-icon");
    uploadIcon.innerHTML = "upload";
    var label = document.createElement("label");
    label.setAttribute("for", "fileUpload" + num);
    label.classList.add("file-upload");
    label.id = "fileUploadLabel" + num;
    // label.innerHTML = "Upload";
    label.appendChild(uploadIcon);
    var input = document.createElement("input");
    input.setAttribute("type", "file");
    input.setAttribute("accept", "image/*");
    input.id = "fileUpload" + num;
    input.setAttribute("name", num);
    
    if(supported("capture") == true) {
        input.setAttribute("capture", true); // Allow phones to take pictures directly from camera
    }
    
    input.addEventListener("change", e => {
       let floorNum = input.name;
       let container = document.getElementById("floor" + floorNum + "container");
       container.querySelector("#filename" + floorNum).innerHTML = "Floor " + floorNum + " | " + input.files[0].name;
    });
    
    secondaryContainer.appendChild(filenameContainer);
    secondaryContainer.appendChild(label);
    secondaryContainer.appendChild(input);
    singleContainer.appendChild(secondaryContainer);
    document.getElementById("upload-form").insertBefore(singleContainer, document.getElementById("additions"));
}

$("#addFloor").click(addFloor);

addFloor();
// addFloor();

class FileUpload {

    constructor(input, id, num) {
        this.id = id;
        this.input = input;
        this.floor_num = num;
        this.max_length = 1024 * 1024; // 1 mb
    }

    upload() {
        this.create_progress_bar();
        this.initFileUpload();
    }
    
    create_progress_bar() {
        let progressBarContainer = document.createElement("div");
        progressBarContainer.id = "progressBarContainer" + this.floor_num;
        progressBarContainer.classList.add("progress-bar-container");
        document.getElementById("floor" + this.floor_num + "container").appendChild(progressBarContainer);
        let progressBar = document.createElement("div");
        progressBar.setAttribute("id", "progressBar" + this.floor_num);
        progressBar.classList.add("progress-bar");
        progressBar.style.width = "0%";
        progressBarContainer.appendChild(progressBar);
    }

    initFileUpload() {
        this.file = this.input.files[0]; // Get first file if multiple files are uploaded to same input
        this.upload_file(0, null);
    }

    upload_file(start, model_id) {
        var end;
        var self = this;
        var existingPath = model_id;
        var formData = new FormData();
        var nextChunk = start + this.max_length + 1;
        var currentChunk = this.file.slice(start, nextChunk);
        var uploadedChunk = start + currentChunk.size;
        if (uploadedChunk >= this.file.size) {
            end = 1;
        } else {
            end = 0;
        }
        formData.append('file', currentChunk);
        formData.append('filename', "floor" + this.floor_num + this.file.name.substr(this.file.name.indexOf("."))); // formData.append('filename', this.file.name);
        formData.append('end', end);
        formData.append('existingPath', existingPath);
        formData.append('nextSlice', nextChunk);
        formData.append('id', this.id);
        $.ajaxSetup({
            headers: {
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        });
        $.ajax({
            xhr: function () {
                var xhr = new XMLHttpRequest();
                xhr.upload.addEventListener('progress', function (e) {
                    if (e.lengthComputable) {
                        if (self.file.size < self.max_length) {
                            var percent = Math.round((e.loaded / e.total) * 100);
                        } else {
                            var percent = Math.round((uploadedChunk / self.file.size) * 100);
                        } 
                        
                        var width = parseInt(document.getElementById("progressBar" + self.floor_num).style.width);
                        var id = setInterval(frame, 50);
                        
                        function frame() {
                            if (width >= percent) {
                                clearInterval(id);
                            } else {
                                width++;
                                $('#progressBar' + self.floor_num).css('width', width + '%');
                                $('#progressBar' + self.floor_num).text(width + '%');
                            }
                        }
                                            
                        // $('#progressBar' + self.floor_num).css('width', percent + '%');
                        // $('#progressBar' + self.floor_num).text(percent + '%');
                    }
                });
                return xhr;
            },

            url: $("#submit").data('url'),
            type: 'POST',
            cache: false,
            processData: false,
            contentType: false,
            data: formData,
            error: function (xhr) {
                alert("Xhr error:" + xhr.statusText);
            },
            success: function (res) {
                if (nextChunk < self.file.size) {
                    // upload file in chunks
                    existingPath = res.existingPath
                    self.upload_file(nextChunk, existingPath);
                } else {
                    // upload complete
                    
                    var width = parseInt(document.getElementById("progressBar" + self.floor_num).style.width);
                    var id = setInterval(frame, 50);
                    
                    function frame() {
                        if (width >= 100) {
                            clearInterval(id);
                            $("#progressBarContainer" + self.floor_num).remove();
                            document.getElementById("fileUploadLabel" + self.floor_num).firstChild.innerHTML = "done";
                        } else {
                            width++;
                            $('#progressBar' + self.floor_num).css('width', width + '%');
                            $('#progressBar' + self.floor_num).text(width + '%');
                        }
                    }
                }
            }
        });
    };
}

function submitForm(event) {
    event.preventDefault();
    $.ajax({
        // url: $("#getId").data('url'),
        url: "/get_id",
        success: function(data) {
            console.log(data);
            for(var i = 0; i < floors.length; i++) {
                var num = floors[i];
                var uploader = new FileUpload(document.querySelector("#fileUpload" + num), data["store_id"], num);
                uploader.upload();
            }
        },
        failure: function(data) { 
            alert('Got an error dude');
        }
    })
    return false;
}