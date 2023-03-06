const blob = document.getElementById("blob");

window.onpointermove = event => { 
    var { clientX, clientY } = event;
    var scrollLeft = $(window).scrollLeft() ;
    var scrollTop = $(window).scrollTop() ;
    
    clientX += scrollLeft;
    clientY += scrollTop;
  
    blob.animate({
        left: `${clientX}px`,
        top: `${clientY}px`
    }, { duration: 3000, fill: "forwards" });
}