

/* =========================================================
   GSAP
========================================================= */

gsap.registerPlugin(ScrollTrigger)

/* =========================================================
   PRELOADER
========================================================= */

window.addEventListener("load", () => {

    gsap.to("#preloader", {
        opacity: 0,
        duration: 1,
        delay: 1,
        pointerEvents: "none"
    })

})

/* =========================================================
   REVEAL ANIMATIONS
========================================================= */

gsap.utils.toArray(".reveal").forEach((el) => {

    gsap.to(el, {
        opacity: 1,
        y: 0,
        duration: 1.2,
        ease: "power4.out",

        scrollTrigger: {
            trigger: el,
            start: "top 85%"
        }
    })

})

/* =========================================================
   CUSTOM CURSOR
========================================================= */


/* =========================================================
   TILT EFFECT
========================================================= */

VanillaTilt.init(document.querySelectorAll(".tilt-card"), {
    max: 12,
    speed: 500,
    glare: true,
    "max-glare": .25
})

/* =========================================================
   MOBILE MENU
========================================================= */

const menuToggle = document.getElementById("menuToggle")
const mobileMenu = document.getElementById("mobileMenu")

menuToggle.addEventListener("click", () => {
    mobileMenu.classList.toggle("active")
})

/* =========================================================
   PARTICLE SYSTEM
========================================================= */

const canvas = document.getElementById("particle-canvas")
const ctx = canvas.getContext("2d")

let particles = []

canvas.width = window.innerWidth
canvas.height = window.innerHeight

class Particle {

    constructor() {

        this.x = Math.random() * canvas.width
        this.y = Math.random() * canvas.height

        this.size = Math.random() * 2 // antes: *3

        this.speedX = (Math.random() - 0.5) * 0.4
        this.speedY = (Math.random() - 0.5) * 0.4

        this.color = [
            "#00f0ff",
            "#8b5cf6",
            "#00ffbf"
        ][Math.floor(Math.random() * 3)]
    }

    update() {
        this.x += this.speedX
        this.y += this.speedY

        if (this.x > canvas.width) this.x = 0
        if (this.x < 0) this.x = canvas.width

        if (this.y > canvas.height) this.y = 0
        if (this.y < 0) this.y = canvas.height
    }

    draw() {

        ctx.beginPath()

        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)

        ctx.fillStyle = this.color

        ctx.shadowBlur = 5
        ctx.shadowColor = this.color

        ctx.fill()
    }
}

function initParticles() {

    particles = []

    for (let i = 0; i < 40; i++) {
        particles.push(new Particle())
    }
}

initParticles()

function animateParticles() {

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    particles.forEach((particle) => {
        particle.update()
        particle.draw()
    })

    requestAnimationFrame(animateParticles)
}

animateParticles()

/* =========================================================
   MOUSE PARALLAX
========================================================= */



/* =========================================================
   THREE.JS
========================================================= */

const scene = new THREE.Scene()

const camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
)

camera.position.z = 5

const renderer = new THREE.WebGLRenderer({
    alpha: true,
    antialias: true
})

renderer.setSize(window.innerWidth, window.innerHeight)

document
    .getElementById("webgl-container")
    .appendChild(renderer.domElement)

/* GEOMETRY */
/* LIGHTS */

const light1 = new THREE.PointLight(0x00ffff, 10)
light1.position.set(2, 3, 4)

scene.add(light1)

const light2 = new THREE.PointLight(0x7c3aed, 10)
light2.position.set(-2, -3, 4)

scene.add(light2)

/* MOUSE INTERACTION */

let mouseX = 0
let mouseY = 0

document.addEventListener("mousemove", (event) => {

    mouseX = (event.clientX / window.innerWidth) * 2 - 1
    mouseY = -(event.clientY / window.innerHeight) * 2 + 1

})

/* ANIMATION */


/* =========================================================
   RESIZE
========================================================= */

window.addEventListener("resize", () => {

    camera.aspect = window.innerWidth / window.innerHeight
    camera.updateProjectionMatrix()

    renderer.setSize(
        window.innerWidth,
        window.innerHeight
    )

    canvas.width = window.innerWidth
    canvas.height = window.innerHeight

})

/* =========================================================
   NAVBAR SCROLL FX
========================================================= */

window.addEventListener("scroll", () => {

    const navbar = document.querySelector(".navbar")

    if (window.scrollY > 50) {

        navbar.style.background =
            "rgba(5,8,22,.75)"

        navbar.style.borderColor =
            "rgba(255,255,255,.12)"

    } else {

        navbar.style.background =
            "rgba(255,255,255,.05)"
    }

})
const wrapper = document.getElementById("notificationWrapper");
const btn = document.getElementById("notificationBtn");

btn.addEventListener("click", (e) => {
  e.stopPropagation();
  wrapper.classList.toggle("active");
});

document.addEventListener("click", (e) => {
  if (!wrapper.contains(e.target)) {
    wrapper.classList.remove("active");
  }
});