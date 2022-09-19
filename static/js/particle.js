const canvas = document.getElementById("particleCanvas");
const html = document.getElementsByTagName('html')[0];
const main = document.getElementsByClassName("header-canvas")[0];
const ctx = canvas.getContext("2d");
canvas.width = html.clientWidth;
canvas.height = window.innerHeight;

let particlesAray;

let mouse = {
  x: null,
  y: null,
  over_canvas: 0,
  radius: (canvas.height / 100) * (canvas.width / 100)
}

main.addEventListener("mousemove",
  function(event) {
    mouse.x = event.x;
    mouse.y = event.y;
  }
);

main.addEventListener("mouseout",
  function() {
    mouse.x = NaN;
    mouse.y = NaN;
  }
);

window.addEventListener("resize",
  function() {
    canvas.width = html.clientWidth;
    canvas.height = innerHeight;
    mouse.radius = ((canvas.height/100) * (canvas.width/100));
    init();
  }
);

class Particle {
  constructor(x, y, directionX, directionY, size, color) {
    this.x = x;
    this.y = y;
    this.directionX = directionX;
    this.directionY = directionY;
    this.size = size;
    this.color = color;
  }

  draw() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
    ctx.fillStyle = this.color;
    ctx.fill();
  }

  update() {
    if(this.x > canvas.width || this.x < 0) {
      this.directionX = -this.directionX;
    }

    if(this.y > canvas.height || this.y < 0) {
      this.directionY = -this.directionY;
    }

    // Mouse Input
    let dx = mouse.x - this.x;
    let dy = mouse.y - this.y;
    let distance = Math.sqrt(dx*dx + dy*dy);
    if(distance < mouse.radius + this.size) {
      if(mouse.x < this.x && this.x < canvas.width - this.size * 10) {
        this.x += 10;
      }

      if(mouse.x > this.x && this.x > this.size * 10) {
        this.x -= 10;
      }

      if(mouse.y < this.y && this.y < canvas.height - this.size * 10) {
        this.y += 10;
      }

      if(mouse.y > this.y && this.y > this.size * 10) {
        this.y -= 10;
      }
    }

    this.x += this.directionX;
    this.y += this.directionY;
    this.draw();
  }

}

function init() {
  particlesArray = [];
  let numberOfParticles = (canvas.height * canvas.width) / 7000;
  for(let i = 0; i < numberOfParticles; i++) {
    let size = (Math.random() * 5) + 1;
    let x = (Math.random() * ((innerWidth - size * 2) - (size * 2)) + size * 2);
    let y = (Math.random() * ((innerHeight - size * 2) - (size * 2)) + size * 2);
    let directionX = (Math.random() * 1.5) - 0.75;
    let directionY = (Math.random() * 1.5) - 0.75;
    let color = "rgba(255, 255, 255, " + (Math.random() / 2 + 0.25) + ")";

    particlesArray.push(new Particle(x, y, directionX, directionY, size, color));
  }
}

function animate() {
  requestAnimationFrame(animate);
  ctx.clearRect(0, 0, innerWidth, innerHeight);

  for(let i = 0; i < particlesArray.length; i++) {
    particlesArray[i].update();
  }

  connect();
}

function connect() {
  let opacityValue = 1;

  for(let a = 0; a < particlesArray.length; a++) {
    for(let b = a; b < particlesArray.length; b++) {
      let dX = particlesArray[a].x - particlesArray[b].x;
      let dY = particlesArray[a].y - particlesArray[b].y;
      let dist = dX*dX + dY*dY;
      let appears_at = (canvas.width/7) * (canvas.height/7);

      if(dist < appears_at) {
        opacityValue = 1 - (dist / appears_at);
        ctx.strokeStyle = "rgba(255, 255, 255," + opacityValue + ")";
        ctx.beginPath();
        ctx.moveTo(particlesArray[a].x, particlesArray[a].y);
        ctx.lineTo(particlesArray[b].x, particlesArray[b].y);
        ctx.stroke();
      }
    }
  }

}

init();
animate();