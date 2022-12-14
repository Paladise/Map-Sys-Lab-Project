const dropZone = document.getElementById("dropZone");
const dropZoneInput = document.getElementById("dropZoneInput");
dropZone.addEventListener("click", function(event) {
    dropZoneInput.click();
});

const developers = document.getElementById("developers");
if(Math.round(Math.random()) == 0) {
    developers.innerHTML = "Developed by Sean Su & Andrei Basto (2023)"
}else{
    developers.innerHTML = "Developed by Andrei Basto & Sean Su (2023)"
}

const uploadImageForm = document.getElementById("uploadImageForm");

document.getElementById("dropZoneInput").onchange = function() {
    uploadImageForm.submit();
};