var paths = document.getElementsByClassName('path');
for(var i = 0; i < paths.length; i++) {
    let length = paths[i].getTotalLength();
    paths[i].style.strokeDasharray = length;
    paths[i].style.strokeDashoffset = length;
}