var dots = document.getElementsByClassName("dot");
var images = document.getElementsByClassName("slide-image");
var texts = document.getElementsByClassName("slide-text");
var activeDot = document.querySelector(".active-dot");
var curSlideIndex = 0;
var myLoop;

function showSlides(slideIndex) {
    clearInterval(myLoop);
    
    let i;
    if (slideIndex >= images.length) {slideIndex = 0} 
    for (i = 0; i < images.length; i++) {
        images[i].style.display = "none"; 
        texts[i].style.display = "none";
    }
    
    curSlideIndex = slideIndex;
    
    images[slideIndex].style.display = "block";  
    texts[slideIndex].style.display = "block";
    activeDot.style.left = (slideIndex * 20) + "px";
    
    myLoop = setInterval(loopSlides, 8000);
}

$(".dot").bind("click", function() {
    var divs = $(".dot");
    var curIdx = divs.index($(this));

    showSlides(curIdx);
});

showSlides(curSlideIndex);

function loopSlides() {
    curSlideIndex++;
    showSlides(curSlideIndex);
}
