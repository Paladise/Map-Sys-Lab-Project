const canvas = document.getElementById("particleCanvas");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = document.body.scrollHeight;
let particlesArray;

window.addEventListener("resize",
  function() {
    canvas.width = window.innerWidth;
    canvas.height = document.body.scrollHeight;
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
    if (this.x > canvas.width || this.x < 0) {
      this.directionX = -this.directionX;
    }

    if (this.y > canvas.height || this.y < 0) {
      this.directionY = -this.directionY;
    }

    this.x += this.directionX;
    this.y += this.directionY;
    this.draw();
  }

}

function init() {
  particlesArray = [];
  let numberOfParticles = (canvas.height * canvas.width) / 20000;
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

function animate() {
  requestAnimationFrame(animate);
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
      let appears_at = (canvas.width / 12) * (canvas.height / 12);

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
animate();