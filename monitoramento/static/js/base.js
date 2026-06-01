document.addEventListener("DOMContentLoaded", () => {
    /* =========================================================
       GSAP REVEAL ANIMATIONS
    ========================================================= */
    if (typeof gsap !== 'undefined') {
        // Inicializa o ScrollTrigger se ele existir
        if (typeof ScrollTrigger !== 'undefined') {
            gsap.registerPlugin(ScrollTrigger);
        }

        // Executa as animações de revelação suave
        gsap.utils.toArray(".reveal").forEach((el) => {
            gsap.fromTo(el, 
                { opacity: 0, y: 30 },
                {
                    opacity: 1,
                    y: 0,
                    duration: 1.2,
                    ease: "power4.out",
                    scrollTrigger: {
                        trigger: el,
                        start: "top 90%",
                        toggleActions: "play none none none"
                    }
                }
            );
        });

        /* PRELOADER */
        const preloader = document.getElementById("preloader");
        if (preloader) {
            window.addEventListener("load", () => {
                gsap.to("#preloader", {
                    opacity: 0,
                    duration: 0.8,
                    delay: 0.5,
                    pointerEvents: "none"
                });
            });
        }
    }

    /* =========================================================
       VANILLA TILT EFFECT (Efeito 3D ao passar o mouse)
    ========================================================= */
    const tiltCards = document.querySelectorAll(".tilt-card");
    if (tiltCards.length > 0 && typeof VanillaTilt !== 'undefined') {
        VanillaTilt.init(tiltCards, {
            max: 12,
            speed: 600,
            glare: true,
            "max-glare": 0.2,
            scale: 1.02
        });
    }

    /* =========================================================
       MOBILE MENU
    ========================================================= */
    const menuToggle = document.getElementById("menuToggle");
    const mobileMenu = document.getElementById("mobileMenu");
    if (menuToggle && mobileMenu) {
        menuToggle.addEventListener("click", () => {
            mobileMenu.classList.toggle("active");
        });
    }

    /* =========================================================
       PARTICLE SYSTEM (Apenas se o canvas existir na página)
    ========================================================= */
    const canvas = document.getElementById("particle-canvas");
    if (canvas) {
        const ctx = canvas.getContext("2d");
        let particles = [];
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        class Particle {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.size = Math.random() * 2;
                this.speedX = (Math.random() - 0.5) * 0.4;
                this.speedY = (Math.random() - 0.5) * 0.4;
                this.color = ["#00f0ff", "#8b5cf6", "#00ffbf"][Math.floor(Math.random() * 3)];
            }
            update() {
                this.x += this.speedX;
                this.y += this.speedY;
                if (this.x > canvas.width) this.x = 0;
                if (this.x < 0) this.x = canvas.width;
                if (this.y > canvas.height) this.y = 0;
                if (this.y < 0) this.y = canvas.height;
            }
            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fillStyle = this.color;
                ctx.fill();
            }
        }

        for (let i = 0; i < 40; i++) particles.push(new Particle());

        function animateParticles() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => { p.update(); p.draw(); });
            requestAnimationFrame(animateParticles);
        }
        animateParticles();
    }

    /* =========================================================
       NOTIFICATION DROPDOWN
    ========================================================= */
    const wrapper = document.getElementById("notificationWrapper");
    const btn = document.getElementById("notificationBtn");
    if (wrapper && btn) {
        btn.addEventListener("click", (e) => {
            e.stopPropagation();
            wrapper.classList.toggle("active");
        });
        document.addEventListener("click", (e) => {
            if (!wrapper.contains(e.target)) wrapper.classList.remove("active");
        });
    }
});