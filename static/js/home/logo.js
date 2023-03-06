var old_visible = true;
var el = document.getElementById("titleChanger");
var cornerLogo = document.getElementById("cornerLogo");
var logoIcon = document.getElementById("backgroundLogo");
var logoContainer = document.getElementById("logoContainer");

function isElementInViewport (el) {

    // Special bonus for those using jQuery
    if (typeof jQuery === "function" && el instanceof jQuery) {
        el = el[0];
    }

    var rect = el.getBoundingClientRect();

    return (
        rect.bottom >= 0
    );
}

function onVisibilityChange(el, callback) {
    return function () {
        var visible = isElementInViewport(el);
        if (visible != old_visible) {
            old_visible = visible;
            if (typeof callback == 'function') {
                callback();
            }
        }
    }
}

var handler = onVisibilityChange(el, function() {
    logoIcon.classList.toggle("shifted");
    logoContainer.classList.toggle("shifted");
    cornerLogo.classList.toggle("shifted");
    for(var i = 0; i < 2; i++) {
        if(logoIcon.classList.contains("shifted")) {
            document.getElementsByClassName("path")[i].removeAttribute("stroke");     
        }else {
            document.getElementsByClassName("path")[i].setAttribute("stroke", "black");
        }
        
    }
});


// jQuery
$(window).on('resize scroll', handler);

history.scrollRestoration = "manual";

$(window).on('beforeunload', function() {
      $(window).scrollTop(0);
});