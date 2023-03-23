window.addEventListener('pageshow', function (event) {
    if (!event.persisted) { // If first time page is showing, don't need to remove it
        return;
    }
    
    var unloadCircle = document.getElementById("pageUnloadCircle");
    unloadCircle.remove(); // In browser cache, so remove it
});

document.addEventListener("DOMContentLoaded", function() {
   if(!window.AnimationEvent) {return; }
   
   var anchors = document.getElementsByTagName("a");
   for(var idx = 0; idx < anchors.length; idx++) {
        if (anchors[idx].hostname !== window.location.hostname ||
            anchors[idx].pathname === window.location.pathname) {
            continue;
        }
        
        anchors[idx].addEventListener('click', function(event) {
            var anchor = event.currentTarget;
            var elem = document.createElement("div");
            elem.classList.add("page-unload-circle");
            elem.setAttribute("id", "pageUnloadCircle")
            document.body.appendChild(elem);
            
            var listener = function() {
                window.location = anchor.href;
                // elem.removeEventListener('animationend', listener);
            };
            elem.addEventListener('animationend', listener);
            
            event.preventDefault();

            elem.classList.add("fill");
        });
   }
});