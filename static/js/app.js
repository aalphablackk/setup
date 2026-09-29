const themeToggle = document.getElementById("themeToggle");
const html = document.documentElement;

const savedTheme = localStorage.getItem("workbeam-theme");

if (savedTheme) {
    html.setAttribute("data-bs-theme", savedTheme);
}

themeToggle?.addEventListener("click", () => {
    const currentTheme = html.getAttribute("data-bs-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";

    html.setAttribute("data-bs-theme", newTheme);

    localStorage.setItem("workbeam-theme", newTheme);

    const icon = themeToggle.querySelector("i");

    if (icon) {
        icon.className =
            newTheme === "dark"
                ? "bi bi-sun"
                : "bi bi-moon";
    }
});