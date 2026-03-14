// app.js - backend mode only
(function () {
  // Keep theme if already chosen
  if (!localStorage.getItem("sist_theme")) {
    localStorage.setItem("sist_theme", "light");
  }

  // One-time cleanup of old demo-seeded localStorage data
  const CLEANUP_KEY = "sist_backend_cleanup_v1";
  if (!localStorage.getItem(CLEANUP_KEY)) {
    localStorage.removeItem("sist_users");
    localStorage.removeItem("sist_od");
    localStorage.removeItem("sist_lab");
    localStorage.removeItem("sist_hostel");
    localStorage.removeItem("sist_seeded_v1");
    localStorage.removeItem("sist_seeded_v2");
    localStorage.setItem(CLEANUP_KEY, "1");
  }
})();