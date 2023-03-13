var scrollDiv = document.getElementById("scrollArrow");

scrollDiv.addEventListener("click", function() {
    $(window).scrollTop($(".subtitle-text-container").offset().top - 200);
});