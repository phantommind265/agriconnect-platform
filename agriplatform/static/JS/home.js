async function fetchNotifications() {
    try {
        let response = await fetch('/notifications');
        if (!response.ok) throw new Error('Failed to fetch');

        let data = await response.json();
        let countElement = document.getElementById("notificationCount");
        let dropdown = document.getElementById("notificationDropdown");

        if (data.notifications.length > 0) {
            countElement.style.display = "inline";
            countElement.textContent = data.notifications.length;

            // Fill dropdown with notifications
            dropdown.innerHTML = "";
            data.notifications.forEach(n => {
                let item = document.createElement("div");
                item.style.padding = "8px";
                item.style.borderBottom = "1px solid #eee";
                item.innerHTML = `<a href="${n.link || '#'}">${n.message}</a><br>
                                  <small>${n.created_at}</small>`;
                dropdown.appendChild(item);
            });
        } else {
            countElement.style.display = "none";
            dropdown.innerHTML = "<div style='padding:8px; text-align:center;'>No new notifications</div>";
        }
    } catch (err) {
        console.error(err);
    }
}

// Auto-refresh every 10+00 seconds
setInterval(fetchNotifications, 1000000);
fetchNotifications();

// Toggle dropdown on click
document.getElementById("notificationBell").addEventListener("click", function(e) {
    e.preventDefault();
    let dropdown = document.getElementById("notificationDropdown");
    dropdown.style.display = dropdown.style.display === "none" ? "block" : "none";
});

//ANIMATION SECTION
document.addEventListener("DOMContentLoaded", () => {
    const elements = document.querySelectorAll("[data-animate]");

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("active");
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });

    elements.forEach(el => observer.observe(el));
});
