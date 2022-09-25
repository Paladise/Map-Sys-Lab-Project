const dropZone = document.getElementById("dropZone");
const dropZoneInput = document.getElementById("dropZoneInput");
dropZone.addEventListener("click", function(event) {
    dropZoneInput.click();
});

window.addEventListener("scroll", function() {
    var canvas = document.getElementById("particleCanvas");
    var logo = document.getElementById("logo");
    if (window.scrollY > (canvas.offsetTop + canvas.offsetHeight - logo.clientHeight)) {
        console.log("is");
        // logo.style.filter = "brightness(0) saturate(100%) invert(21%) sepia(92%) saturate(3393%) hue-rotate(213deg) brightness(94%) contrast(97%)";
        logo.style.filter = "brightness(0) saturate(100%) invert(61%) sepia(75%) saturate(2168%) hue-rotate(152deg) brightness(101%) contrast(95%)";
    }else {
        console.log("not");
        logo.style.filter = "none";
    }
});