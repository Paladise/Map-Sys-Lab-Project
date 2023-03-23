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

$('.slide-image').on('mousemove', function(event) {
  // This gives you the position of the image on the page
  var bbox = event.target.getBoundingClientRect();

  // Then we measure how far into the image the mouse is in both x and y directions
  var mouseX = event.clientX - bbox.left;
  var mouseY = event.clientY - bbox.top;

  // Then work out how far through the image as a percentage the mouse is
  var xPercent = (mouseX / bbox.width) * 100;
  var yPercent = (mouseY / bbox.height) * 100;
  
  xPercent = Math.max(xPercent, 10);
  xPercent = Math.min(xPercent, 90);
  
  yPercent = Math.max(yPercent, 10);
  yPercent = Math.min(yPercent, 90);

  // Then we change the `transform-origin` css property on the image to center the zoom effect on the mouse position
  //event.target.style.transformOrigin = xPercent + '% ' + yPercent + '%';
  // It's a bit clearer in jQuery:
  $(this).css('transform-origin', (xPercent+'% ' + yPercent+ '%') );
  // We add the '%' units to make sure the string looks exactly like the css declaration it becomes.

});