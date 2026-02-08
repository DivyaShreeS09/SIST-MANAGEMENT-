/* =========================================
   COMMON.JS - shared utilities
   Keeps your keys:
   - sist_theme
   - sist_lang
   Theme label: Light mode / Dark mode
========================================= */

function toast(msg){
  const t = document.getElementById("toast");
  if(!t) return;
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(window.__toastT);
  window.__toastT = setTimeout(()=>t.classList.remove("show"), 1600);
}

/* ---------- Theme (uses sist_theme) ---------- */
function applyTheme(mode){
  const isDark = mode === "dark";
  document.body.classList.toggle("dark", isDark);
  localStorage.setItem("sist_theme", mode);
  updateThemeButtonLabel();
}
function updateThemeButtonLabel(){
  const btn = document.querySelector("[data-theme-toggle]");
  if(!btn) return;
  const isDark = document.body.classList.contains("dark");
  btn.textContent = isDark ? "Light mode" : "Dark mode";
}
function initThemeToggle(){
  const saved = localStorage.getItem("sist_theme") || "light";
  applyTheme(saved);

  const btn = document.querySelector("[data-theme-toggle]");
  if(btn){
    btn.addEventListener("click", ()=>{
      const isDark = document.body.classList.contains("dark");
      applyTheme(isDark ? "light" : "dark");
    });
  }
}

/* ---------- Session ---------- */
function getSession(){
  const raw = localStorage.getItem("session");
  return raw ? JSON.parse(raw) : null;
}
function setSession(sess){
  localStorage.setItem("session", JSON.stringify(sess));
}
function clearSession(){
  localStorage.removeItem("session");
}
function requireAuth(allowedRoles){
  const s = getSession();
  if(!s || !allowedRoles.includes(s.role)){
    window.location.href = "login.html";
    throw new Error("Unauthorized");
  }
  return s;
}
function headerBind(){
  const s = getSession();
  const who = document.querySelector("[data-who]");
  if(who) who.textContent = s ? s.name : "-";

  const role = document.querySelector("[data-role]");
  if(role) role.textContent = s ? s.role.replaceAll("_"," ") : "-";

  const signout = document.querySelector("[data-signout]");
  if(signout){
    signout.addEventListener("click", ()=>{
      clearSession();
      window.location.href = "login.html";
    });
  }
}

/* ---------- Status pills ---------- */
function statusPill(status){
  const s = (status||"PENDING").toUpperCase();
  if(s==="APPROVED") return `<span class="pill ok">APPROVED</span>`;
  if(s==="REJECTED") return `<span class="pill bad">REJECTED</span>`;
  return `<span class="pill wait">PENDING</span>`;
}

/* ---------- Local storage wrappers (keep your keys) ---------- */
const Store = {
  users: ()=> JSON.parse(localStorage.getItem("sist_users")||"[]"),
  od:    ()=> JSON.parse(localStorage.getItem("sist_od")||"[]"),
  lab:   ()=> JSON.parse(localStorage.getItem("sist_lab")||"[]"),
  hostel:()=> JSON.parse(localStorage.getItem("sist_hostel")||"[]"),

  setUsers: (v)=> localStorage.setItem("sist_users", JSON.stringify(v)),
  setOD:    (v)=> localStorage.setItem("sist_od", JSON.stringify(v)),
  setLab:   (v)=> localStorage.setItem("sist_lab", JSON.stringify(v)),
  setHostel:(v)=> localStorage.setItem("sist_hostel", JSON.stringify(v)),
};

/* ---------- Simple scope rules ---------- */
function scopeODForApprover(sess, odList){
  // HOD sees all in dept
  if(sess.role==="HOD") return odList;

  // CC sees only their section
  if(sess.role==="CLASS_COORDINATOR"){
    return odList.filter(r => r.section === sess.section);
  }

  // YC sees only their year
  if(sess.role==="YEAR_COORDINATOR"){
    return odList.filter(r => String(sess.year) === String(Store.users().find(u=>u.id===r.studentId)?.year));
  }

  // default none
  return [];
}

function scopeLabForApprover(sess, labList){
  // "admin_lab_cc.html" treated as FACULTY/INCHARGE for this demo (same scope as CC section)
  if(sess.role==="CLASS_COORDINATOR"){
    return labList.filter(r => r.section === sess.section);
  }
  if(sess.role==="YEAR_COORDINATOR"){
    return labList.filter(r => String(sess.year) === String(Store.users().find(u=>u.id===r.studentId)?.year));
  }
  if(sess.role==="HOD") return labList;
  return [];
}

function scopeHostelForApprover(sess, hosList){
  if(sess.role==="WARDEN") return hosList.filter(r => r.statusWARDEN === "PENDING");
  if(sess.role==="CHIEF_WARDEN") return hosList.filter(r => r.statusWARDEN === "APPROVED" && r.statusCHIEF === "PENDING");
  if(sess.role==="SECURITY") return hosList.filter(r => r.statusCHIEF === "APPROVED" && (r.statusSECURITY === "LOCKED" || r.statusSECURITY==="PENDING"));
  return [];
}

/* ---------- PDF export helper (admin) ---------- */
function exportPdfFromRows(title, headers, rows){
  // uses CDN in admin pages
  const { jsPDF } = window.jspdf || {};
  if(!jsPDF){ toast("PDF library missing"); return; }

  const doc = new jsPDF({orientation:"landscape"});
  doc.setFont("helvetica","bold");
  doc.setFontSize(14);
  doc.text(title, 14, 16);

  doc.setFont("helvetica","normal");
  doc.setFontSize(10);
  doc.text("Generated: " + new Date().toLocaleString(), 14, 24);

  doc.autoTable({
    head: [headers],
    body: rows,
    startY: 30,
    styles: { fontSize: 8 },
    headStyles: { fillColor: [255, 59, 0] }
  });

  doc.save(title.replaceAll(" ","_") + ".pdf");
}
