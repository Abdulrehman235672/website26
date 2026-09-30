// ==========================================
// HIGH PEAK SPORTS
// Main JavaScript
// ==========================================


// MOBILE MENU
function toggleMenu() {

    const menu = document.getElementById("mobileMenu");

    menu.classList.toggle("active");

}


// CLOSE MOBILE MENU
function closeMenu() {

    const menu = document.getElementById("mobileMenu");

    menu.classList.remove("active");

}


// CLOSE MENU WHEN CLICKING OUTSIDE
document.addEventListener("click", function (event) {

    const menu = document.getElementById("mobileMenu");

    const button = document.querySelector(".menu-button");

    if (!menu || !button) return;

    if (
        menu.classList.contains("active") &&
        !menu.contains(event.target) &&
        !button.contains(event.target)
    ) {

        menu.classList.remove("active");

    }

});


// ==========================================
// SCROLL REVEAL ANIMATION
// ==========================================

const revealElements = document.querySelectorAll(
    ".intro, .products, .statement, .stats, .process, .about"
);


const observer = new IntersectionObserver(

    function (entries) {

        entries.forEach(function (entry) {

            if (entry.isIntersecting) {

                entry.target.classList.add("visible");

                observer.unobserve(entry.target);

            }

        });

    },

    {
        threshold: 0.08
    }

);


revealElements.forEach(function (element) {

    element.classList.add("reveal");

    observer.observe(element);

});


// ==========================================
// SMOOTH SCROLL
// ==========================================

document.querySelectorAll('a[href^="#"]').forEach(function (link) {

    link.addEventListener("click", function (event) {

        const targetId = this.getAttribute("href");

        if (targetId === "#") return;

        const target = document.querySelector(targetId);

        if (!target) return;

        event.preventDefault();

        target.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    });

});


// ==========================================
// HEADER SCROLL EFFECT
// ==========================================

const header = document.querySelector(".header");


window.addEventListener("scroll", function () {

    if (!header) return;

    if (window.scrollY > 50) {

        header.classList.add("scrolled");

    } else {

        header.classList.remove("scrolled");

    }

});



// Automatically update copyright year
document.addEventListener("DOMContentLoaded", () => {
  const yearSpan = document.querySelector("[data-year]");
  if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear();
  }
});




// Automatically update copyright year
document.addEventListener("DOMContentLoaded", () => {
    const yearSpan = document.querySelector("[data-year]");
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }
});
const menuBtn = document.querySelector('.menu-button');
const closeBtn = document.getElementById('closeMenu');
const mobileMenu = document.getElementById('mobileMenu');
const mobileLinks = document.querySelectorAll('.mobile-menu a');

if (menuBtn && mobileMenu) {
    menuBtn.addEventListener('click', () => {
        mobileMenu.classList.add('active');
    });
}

if (closeBtn && mobileMenu) {
    closeBtn.addEventListener('click', () => {
        mobileMenu.classList.remove('active');
    });
}

if (mobileMenu) {
    mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
        });
    });
}
