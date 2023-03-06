let maxAngle = 10;

let refs = {
  transformedDiv: document.querySelector('.background-logo')
};
refs.transformedDiv.addEventListener("transitionend", transitionComplete, false);

let lastRender = {};
let isTransitionComplete = true;

window.addEventListener("resize", onResize, false);
function onResize() {
  page.width = window.innerWidth;
  page.height = window.innerHeight;
}

let page = {};
page.width = window.innerWidth;
page.height = window.innerHeight;

document.addEventListener("mousemove", onMouseMove);

function onMouseMove(event) {
  mousePosition.x = event.pageX;
  mousePosition.y = event.pageY;
  setTrackingActive();
}

function updatePerspective() {
 
  if (
      isTransitionComplete && (
        lastRender.mouseX !== mousePosition.x ||
        lastRender.mouseY !== mousePosition.y ||
        lastRender.pageWidth !== page.width ||
        lastRender.pageHeight !== page.height
      )
    ) {
    let degreesY = 0;
    let degreesX = 0;

    //console.log(page, mousePosition);
    if (mousePosition.x !== -1) {
      degreesY = -(page.width / 2 - mousePosition.x) / (page.width/  2) * maxAngle;
      degreesX = (page.height / 2 - mousePosition.y) / (page.height / 2) * maxAngle;
    }
    if (lastRender.mouseX === -1) {
      setTrackingStarting();
    }
    
    lastRender.mouseX = mousePosition.x;
    lastRender.mouseY = mousePosition.y;
    lastRender.pageWidth = page.width;
    lastRender.pageHeight = page.height;

    refs.transformedDiv.style.transform = `perspective( 2000px ) rotateY(${degreesY}deg) rotateX(${degreesX}deg)`;
  }
  
  window.requestAnimationFrame(updatePerspective);
}

let mousePosition = {};
clearMousePosition();

window.requestAnimationFrame(updatePerspective);

function clearMousePosition() {
  setTrackingEnding();
  mousePosition.x = -1;
  mousePosition.y = -1;
}

let resetTimeout = initResetTimeout();
function initResetTimeout() {
  return window.setTimeout(clearMousePosition, 3000);
}
function resetResetTimeout() {
  window.clearTimeout(resetTimeout);
  resetTimeout = initResetTimeout();
}

function transitionComplete() {
  isTransitionComplete = true;
  refs.transformedDiv.classList.remove("smooth", "fast");
}
function setTrackingStarting() {
  isTransitionComplete = false;
  refs.transformedDiv.classList.add("fast");
}
function setTrackingActive() {
  refs.transformedDiv.classList.remove("smooth");
  resetResetTimeout();
}
function setTrackingEnding() {
  refs.transformedDiv.classList.add("smooth");
  refs.transformedDiv.classList.remove("fast");
}