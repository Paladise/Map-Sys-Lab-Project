var floors = [];
var symbols = [];

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
    img.classList.add("preview-image");
    document.body.appendChild(img);
    
    img.addEventListener("click", e => {
        img.remove();
    });
}

function add(type) {
    console.log("Adding type:", type);
    var isFloor = true;
    if(type == "symbol") {
        isFloor = false;
    }
    
    if(isFloor && floors.length + 1 == 4) {
        alert("You can currently only upload 3 floors");
        return; // Don't allow more than 4 floors
    }
    
    if(isFloor) {
        var num = floors.length + 1;
        floors.push(num);
    }else {
        var num = symbols.length + 1;
        symbols.push(num);
    }
    
    const template = document.querySelector('.' + type + '-template');
    const clone = template.content.cloneNode(1).firstElementChild;
    var secondaryContainer = clone.querySelector(".secondary-container");
    secondaryContainer.setAttribute("id", type + num + "container");
    var fileInfo = clone.querySelector(".file-info");
    fileInfo.setAttribute("id", type + num + "fileInfo");
    if(type == "floor") {
        fileInfo.innerHTML = "Floor " + num;
    }
    
    var fileName = clone.querySelector(".fileName");
    fileName.setAttribute("id", type + num + "fileName");
    fileName.setAttribute("data-type", type);
    fileName.setAttribute("data-num", num);
    var label = clone.querySelector(".file-label");
    label.setAttribute("for", type + num + "upload");
    label.setAttribute("id", type + num + "label");
    var input = clone.querySelector(".file-upload");
    input.setAttribute("id", type + num + "upload");
    input.setAttribute("name", type + num + "upload");
    input.setAttribute("data-type", type);
    input.setAttribute("data-num", num);

    if(supported("capture") == true) {
        input.setAttribute("capture", true); // Allow phones to take pictures directly from camera
    }

    input.addEventListener("change", e => {
        let type = input.getAttribute("data-type");
        let num = input.getAttribute("data-num");
        
        var container = document.getElementById(type + num + "container");
        container.querySelector("#" + type + num + "fileName").innerHTML = input.files[0].name;
        container.querySelector("#" + type + num + "fileName").style.display = "block";
    });
    
    fileName.addEventListener("click", e => {
        let type = fileName.getAttribute("data-type");
        let num = fileName.getAttribute("data-num");
        
        let input = document.getElementById(type + num + "upload");
        let file = input.files[0];
        displayAsImage(file);
    });

    document.getElementById("upload-form").insertBefore(clone, document.getElementById("additions"));
}

$("#addFloor").click(function() {
    add("floor")
});

$("#addSymbol").click(function() {
    add("symbol")
});

add("floor"); // Create one floor in beginning

class FileUpload {

    constructor(input, id, type, num, extra) {
        this.id = id;
        this.input = input;
        this.num = num;
        this.type = type;
        this.extra = extra;
        
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
        document.getElementById(this.type + this.num + "container").appendChild(progressBarContainer);
        let progressBar = document.createElement("div");
        progressBar.setAttribute("id", this.type + this.num + "progressBar");
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
        if(this.type == "floor") {
            var add = this.type + this.num;
        }else{
            var add = this.type + this.extra;
        }
        formData.append('fileName', add + this.file.name.substr(this.file.name.indexOf("."))); // formData.append('fileName', this.file.name);
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
                        
                        var width = parseInt(document.getElementById(self.type + self.num + "progressBar").style.width);
                        var id = setInterval(frame, 50);
                        
                        function frame() {
                            if (width >= percent) {
                                clearInterval(id);
                            } else {
                                width++;
                                $("#" + self.type + self.num + "progressBar").css('width', width + '%');
                                $("#" + self.type + self.num + "progressBar").text(width + '%');
                            }
                        }
                                            
                        // $("#" + self.type + self.num + "ProgressBar").css('width', percent + '%');
                        // $("#" + self.type + self.num + "ProgressBar").text(percent + '%');
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
                    
                    var width = parseInt(document.getElementById(self.type + self.num + "progressBar").style.width);
                    var id = setInterval(frame, 50);
                    
                    function frame() {
                        if (width >= 100) {
                            clearInterval(id);
                            $("#" + self.type + self.num + "progressBar").remove();
                            document.getElementById(self.type + self.num + "label").firstChild.innerHTML = "done";
                        } else {
                            width++;
                            $("#" + self.type + self.num + "progressBar").css('width', width + '%');
                            $("#" + self.type + self.num + "progressBar").text(width + '%');
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
                var uploader = new FileUpload(document.getElementById("floor" + num + "upload"), data["store_id"], "floor", num, null);
                uploader.upload();
            }
            
            for(var i = 0; i < symbols.length; i++) {
                var num = symbols[i];
                var uploader = new FileUpload(document.getElementById("symbol" + num + "upload"), data["store_id"], "symbol", num, document.getElementById("symbol" + num + "fileInfo").value);
                uploader.upload();
            }
            
            $(document).ajaxStop(function() {
                window.location.replace("http://atlas.sites.tjhsst.edu/render/" + data["store_id"]);
            });
            
        },
        failure: function(data) { 
            alert('Got an error dude');
        }
    })

    return false;
}