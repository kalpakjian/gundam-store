document.addEventListener('DOMContentLoaded', function () {
    var yearEl = document.querySelector(".year");
    if (yearEl) yearEl.innerHTML = new Date().getFullYear();

    var msgEl = document.getElementById("message");
    if (msgEl && typeof $ !== 'undefined') {
        setTimeout(() => $("#message").fadeOut("slow"), 3000);
    }
});
