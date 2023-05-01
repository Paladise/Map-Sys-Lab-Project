const canvas = document.getElementById("particleCanvas");
const ctx = canvas.getContext("2d");
const particleContainerContent = document.getElementById("particleContainerContent");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
let particlesArray;

let mouse = {
  x: null,
  y: null,
  over_canvas: 0,
  radius: (canvas.height / 100) * (canvas.width / 100)
}

canvas.addEventListener("mousemove",
  function(event) {
    var scrollTop = (window.pageYOffset !== undefined) ? window.pageYOffset : (document.documentElement || document.body.parentNode || document.body).scrollTop;
    mouse.x = event.x;
    mouse.y = event.y + scrollTop;
  }
);

canvas.addEventListener("mouseout",
  function() {
    mouse.x = NaN;
    mouse.y = NaN;
  }
);

function resizeParticleCanvas() {
    canvas.width = particleContainerContent.getBoundingClientRect().width;
    canvas.height = particleContainerContent.scrollHeight;
    canvas.style.width = particleContainerContent.getBoundingClientRect().width;
    canvas.style.height = particleContainerContent.scrollHeight;
    mouse.radius = ((canvas.height / 100) * (canvas.width / 100));
    init();
}

window.addEventListener("resize", resizeParticleCanvas);

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
    if (this.x > canvas.width || this.x < 0) {
      this.directionX = -this.directionX;
    }

    if (this.y > canvas.height || this.y < 0) {
      this.directionY = -this.directionY;
    }

    // Mouse Input
    let dx = mouse.x - this.x;
    let dy = mouse.y - this.y;
    let distance = Math.sqrt(dx * dx + dy * dy);
    if (distance < mouse.radius + this.size) {
      if (mouse.x < this.x && this.x < canvas.width - this.size * 10) {
        this.x += 10;
      }

      if (mouse.x > this.x && this.x > this.size * 10) {
        this.x -= 10;
      }

      if (mouse.y < this.y && this.y < canvas.height - this.size * 10) {
        this.y += 10;
      }

      if (mouse.y > this.y && this.y > this.size * 10) {
        this.y -= 10;
      }
      this.directionX *= -1;
      this.directionY *= -1;
    }

    this.x += this.directionX;
    this.y += this.directionY;
    this.draw();
  }

}

function init() {
  particlesArray = [];
  let numberOfParticles = (canvas.height * canvas.width) / 6500;
  for (let i = 0; i < numberOfParticles; i++) {
    let size = (Math.random() * 5) + 1;
    let x = (Math.random() * ((canvas.width - size * 2) - (size * 2)) + size * 2);
    let y = (Math.random() * ((canvas.height - size * 2) - (size * 2)) + size * 2);
    let directionX = (Math.random() * 2) - 0.69;
    let directionY = (Math.random() * 2) - 0.69;
    let color = "rgba(255, 255, 255, " + (Math.random() / 2 + 0.25) + ")";

    particlesArray.push(new Particle(x, y, directionX, directionY, size, color));
  }
}

function animate_particles() {
  requestAnimationFrame(animate_particles);
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  for (let i = 0; i < particlesArray.length; i++) {
    particlesArray[i].update();
  }

  connect();
}

function connect() {
  let opacityValue = 1;

  for (let a = 0; a < particlesArray.length; a++) {
    for (let b = a; b < particlesArray.length; b++) {
      let dX = particlesArray[a].x - particlesArray[b].x;
      let dY = particlesArray[a].y - particlesArray[b].y;
      let dist = dX * dX + dY * dY;
      let appears_at = (canvas.width / 7) * (canvas.height / 7);

      if (dist < appears_at) {
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
animate_particles();