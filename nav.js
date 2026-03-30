document.addEventListener("DOMContentLoaded", function () {
    fetch("nav.html")
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.text();
        })
        .then(data => {
            document.getElementById("navbar-container").innerHTML = data;

            // Highlight active page
            const links = document.querySelectorAll("nav a");
            const currentPage = window.location.pathname.split("/").pop() || "index.html";
            links.forEach(link => {
                if (link.getAttribute("href") === currentPage) {
                    link.classList.add("active");
                }
            });

            // Hamburger toggle
            const toggle = document.querySelector(".nav-toggle");
            const menu = document.querySelector(".nav-menu");
            toggle.addEventListener("click", function () {
                const isOpen = menu.classList.toggle("nav-open");
                toggle.setAttribute("aria-expanded", isOpen);
                toggle.textContent = isOpen ? "\u2715" : "\u2261";
            });

            // Close menu when a link is clicked
            menu.querySelectorAll("a").forEach(link => {
                link.addEventListener("click", () => {
                    menu.classList.remove("nav-open");
                    toggle.setAttribute("aria-expanded", false);
                    toggle.textContent = "\u2261";
                });
            });
        })
        .catch(error => console.error("Error loading navigation:", error));
});
