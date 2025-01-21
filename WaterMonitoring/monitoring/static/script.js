// Role-Based Redirection
document.getElementById("loginForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const role = document.getElementById("role").value;
    let redirectURL;

    switch (role) {
        case "admin":
            redirectURL = "/admin-dashboard";
            break;
        case "vendor":
            redirectURL = "/vendor-dashboard";
            break;
        case "inspector":
            redirectURL = "/inspector-dashboard";
            break;
        default:
            redirectURL = "/";
    }

    alert(`Redirecting to: ${redirectURL}`);
    // Simulate redirection (replace with actual logic)
    window.location.href = redirectURL;
});

// Forgot Password Modal
const forgotPasswordLink = document.getElementById("forgot-password");
const forgotPasswordModal = document.getElementById("forgotPasswordModal");
const closeModal = document.getElementById("closeModal");

forgotPasswordLink.addEventListener("click", function (e) {
    e.preventDefault();
    forgotPasswordModal.style.display = "block";
});

closeModal.addEventListener("click", function () {
    forgotPasswordModal.style.display = "none";
});
