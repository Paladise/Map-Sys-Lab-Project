function supported(attribute) {
    var i = document.createElement('input');
    i.setAttribute(attribute, true);
    return !!i[attribute];
}

if(supported("capture") == true) {
    document.getElementById("captureInput").setAttribute("capture", True);
    document.body.innerHTML += "@capture is supported";
}else {
    document.body.innerHTML += "@capture is not supported";
}

var input = document.getElementById("captureInput"); 

input.onchange = function () {
  var file = input.files[0];

  //upload(file);
  drawOnCanvas(file);   // see Example 6
  displayAsImage(file); // see Example 7
};


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