// common.js - auth, theme, rendering helpers, approvals, exports

(function(){
  // Apply theme ASAP
  const theme = localStorage.getItem("sist_theme") || "light";
  document.documentElement.setAttribute("data-theme", theme);
})();

const DB = {
  users: () => JSON.parse(localStorage.getItem("sist_users")||"[]"),
  od: () => JSON.parse(localStorage.getItem("sist_od")||"[]"),
  lab: () => JSON.parse(localStorage.getItem("sist_lab")||"[]"),
  hostel: () => JSON.parse(localStorage.getItem("sist_hostel")||"[]"),

  saveOD: (arr)=> localStorage.setItem("sist_od", JSON.stringify(arr)),
  saveLab:(arr)=> localStorage.setItem("sist_lab", JSON.stringify(arr)),
  saveHostel:(arr)=> localStorage.setItem("sist_hostel", JSON.stringify(arr)),
};

function setTheme(next){
  localStorage.setItem("sist_theme", next);
  document.documentElement.setAttribute("data-theme", next);
  updateThemeButtonText();
}

function toggleTheme(){
  const cur = localStorage.getItem("sist_theme") || "light";
  setTheme(cur === "light" ? "dark" : "light");
}

function updateThemeButtonText(){
  const cur = localStorage.getItem("sist_theme") || "light";
  const btn = document.querySelector("[data-theme-toggle]");
  if(btn){
    btn.textContent = cur === "light" ? "Dark mode" : "Light mode";
  }
}

function session(){
  try { return JSON.parse(localStorage.getItem("sist_session")||"null"); } catch { return null; }
}

function currentUser(){
  const s = session();
  if(!s) return null;
  return DB.users().find(u => u.id === s.userId) || null;
}

function requireAuth(){
  const u = currentUser();
  if(!u){
    window.location.href = "login.html";
    return null;
  }
  return u;
}

function signOut(){
  localStorage.removeItem("sist_session");
  window.location.href = "login.html";
}

function statusClass(status){
  const s = (status||"").toUpperCase();
  if(s === "APPROVED") return "approved";
  if(s === "REJECTED") return "rejected";
  if(s === "LOCKED") return "locked";
  return "pending";
}

function badge(status){
  const s = (status||"PENDING").toUpperCase();
  return `<span class="badge ${statusClass(s)}">${s}</span>`;
}

function formatDT(date, time){
  const d = date || "-";
  const t = time || "-";
  return `${d} ${t}`;
}

// CC/YC derived status rule: reject wins, else any approved wins, else pending
function deriveCCYC(rec){
  const a = (rec.statusCC||"PENDING").toUpperCase();
  const b = (rec.statusYC||"PENDING").toUpperCase();
  if(a==="REJECTED" || b==="REJECTED") return "REJECTED";
  if(a==="APPROVED" || b==="APPROVED") return "APPROVED";
  return "PENDING";
}

function canHodApproveOD(rec){
  const ccyc = deriveCCYC(rec);
  return ccyc === "APPROVED" && (rec.statusHOD||"PENDING") === "PENDING";
}

function visibleToApprover(user, student){
  // Approvers must only see their scope
  if(user.role === "CLASS_COORDINATOR"){
    return student.program === user.program && student.section === user.section && student.year === user.year;
  }
  if(user.role === "YEAR_COORDINATOR"){
    return student.program === user.program && student.year === user.year;
  }
  if(user.role === "HOD"){
    return student.dept === user.dept;
  }
  // hostel roles see hostellers only in their scope (keep simple)
  return true;
}

function findUserNameById(id){
  const u = DB.users().find(x => x.id === id);
  return u ? u.name : "—";
}

function printHTML(title, html){
  const w = window.open("", "_blank");
  w.document.write(`
  <html>
    <head>
      <title>${title}</title>
      <meta charset="utf-8"/>
      <style>
        body{ font-family: Arial, sans-serif; padding: 24px; }
        h1{ font-size: 18px; margin: 0 0 14px; }
        .muted{ color:#555; font-size: 12px; }
        table{ width:100%; border-collapse: collapse; margin-top: 14px;}
        th,td{ border:1px solid #ddd; padding:10px; font-size: 12px; text-align:left; }
        th{ background:#f4f4f4; }
        .sig{ margin-top: 18px; display:flex; justify-content:space-between; gap: 24px; }
        .sig > div{ flex:1; border-top: 1px dashed #aaa; padding-top: 10px; font-size: 12px; }
      </style>
    </head>
    <body>
      ${html}
      <script>
        window.onload = ()=> { window.print(); };
      </script>
    </body>
  </html>`);
  w.document.close();
}

// ---- Student approval letter PDFs (print-to-pdf) ----
function downloadODLetter(rec){
  const ccycNames = [];
  if(rec.ccBy) ccycNames.push(findUserNameById(rec.ccBy));
  if(rec.ycBy) ccycNames.push(findUserNameById(rec.ycBy));
  const hodName = rec.hodBy ? findUserNameById(rec.hodBy) : "—";

  const html = `
    <h1>SIST MANAGEMENT SYSTEM — OD Approval Letter</h1>
    <div class="muted">Digitally generated. Save as PDF.</div>
    <p>Dear Student,</p>
    <p>Your <b>On-Duty (OD)</b> request has been digitally approved.</p>

    <table>
      <tr><th>Register No</th><td>${rec.regNo}</td></tr>
      <tr><th>Name</th><td>${rec.studentName}</td></tr>
      <tr><th>Program</th><td>${rec.program}</td></tr>
      <tr><th>Section</th><td>${rec.section}</td></tr>
      <tr><th>Reason</th><td>${rec.reason}</td></tr>
      <tr><th>From</th><td>${formatDT(rec.fromDate, rec.fromTime)}</td></tr>
      <tr><th>To</th><td>${formatDT(rec.toDate, rec.toTime)}</td></tr>
    </table>

    <div class="sig">
      <div><b>CC/YC Approved By:</b><br/>${ccycNames.length ? ccycNames.join(", ") : "—"}</div>
      <div><b>HOD Approved By:</b><br/>${hodName}</div>
    </div>
  `;
  printHTML("OD Approval Letter", html);
}

function downloadLabLetter(rec){
  const mentorName = rec.mentorBy ? findUserNameById(rec.mentorBy) : "—";
  const hodName = rec.hodBy ? findUserNameById(rec.hodBy) : "—";
  const html = `
    <h1>SIST MANAGEMENT SYSTEM — Lab Access Approval Letter</h1>
    <div class="muted">Digitally generated. Save as PDF.</div>
    <p>Your <b>Lab Access</b> request has been digitally approved.</p>

    <table>
      <tr><th>Register No</th><td>${rec.regNo}</td></tr>
      <tr><th>Name</th><td>${rec.studentName}</td></tr>
      <tr><th>Program</th><td>${rec.program}</td></tr>
      <tr><th>Section</th><td>${rec.section}</td></tr>
      <tr><th>Lab</th><td>${rec.lab}</td></tr>
      <tr><th>Reason</th><td>${rec.reason}</td></tr>
      <tr><th>From</th><td>${formatDT(rec.fromDate, rec.fromTime)}</td></tr>
      <tr><th>To</th><td>${formatDT(rec.toDate, rec.toTime)}</td></tr>
    </table>

    <div class="sig">
      <div><b>Mentor Approved By:</b><br/>${mentorName}</div>
      <div><b>HOD Approved By:</b><br/>${hodName}</div>
    </div>
  `;
  printHTML("Lab Access Approval Letter", html);
}

function downloadHostelLetter(rec){
  const chief = rec.chiefBy ? findUserNameById(rec.chiefBy) : "—";
  const warden = rec.wardenBy ? findUserNameById(rec.wardenBy) : "—";
  const security = rec.securityBy ? findUserNameById(rec.securityBy) : "—";

  const html = `
    <h1>SIST MANAGEMENT SYSTEM — Hostel Outpass Approval Letter</h1>
    <div class="muted">Digitally generated. Save as PDF.</div>
    <p>Your <b>Hostel Outpass</b> request has been digitally approved.</p>

    <table>
      <tr><th>Register No</th><td>${rec.regNo}</td></tr>
      <tr><th>Name</th><td>${rec.studentName}</td></tr>
      <tr><th>Program</th><td>${rec.program}</td></tr>
      <tr><th>Section</th><td>${rec.section}</td></tr>
      <tr><th>Purpose</th><td>${rec.purpose}</td></tr>
      <tr><th>From</th><td>${formatDT(rec.fromDate, rec.fromTime)}</td></tr>
      <tr><th>To</th><td>${formatDT(rec.toDate, rec.toTime)}</td></tr>
    </table>

    <div class="sig">
      <div><b>Chief Warden:</b><br/>${chief}</div>
      <div><b>Warden:</b><br/>${warden}</div>
      <div><b>Security:</b><br/>${security}</div>
    </div>
  `;
  printHTML("Hostel Outpass Approval Letter", html);
}

// ---- Admin exports ----
function exportApprovedOD(user, filters){
  const users = DB.users();
  const od = DB.od();

  const approved = od
    .filter(r => (r.statusHOD||"") === "APPROVED" && deriveCCYC(r)==="APPROVED")
    .filter(r => {
      const stu = users.find(x => x.id === r.studentId);
      return stu && visibleToApprover(user, stu);
    })
    .filter(r => {
      const okYear = !filters.year || String(r.year) === String(filters.year);
      const okProg = !filters.program || (r.program||"").toLowerCase().includes(filters.program.toLowerCase());
      const okSec  = !filters.section || (r.section||"").toLowerCase().includes(filters.section.toLowerCase());
      return okYear && okProg && okSec;
    });

  const rows = approved.map(r=>`
    <tr>
      <td>${r.regNo}</td><td>${r.studentName}</td><td>${r.program}</td><td>${r.section}</td>
      <td>${r.reason}</td>
      <td>${formatDT(r.fromDate,r.fromTime)}</td>
      <td>${formatDT(r.toDate,r.toTime)}</td>
      <td>${(r.ccBy?findUserNameById(r.ccBy):"")}${(r.ycBy?(", "+findUserNameById(r.ycBy)):"")}</td>
      <td>${r.hodBy?findUserNameById(r.hodBy):""}</td>
    </tr>
  `).join("");

  const html = `
    <h1>Approved OD List</h1>
    <div class="muted">Filtered export. Save as PDF.</div>
    <table>
      <tr>
        <th>Reg No</th><th>Name</th><th>Program</th><th>Section</th>
        <th>Reason</th><th>From</th><th>To</th><th>CC/YC</th><th>HOD</th>
      </tr>
      ${rows || `<tr><td colspan="9">No approved records for selected filters.</td></tr>`}
    </table>
  `;
  printHTML("Approved OD List", html);
}

function exportApprovedLab(user, filters){
  const users = DB.users();
  const lab = DB.lab();

  const approved = lab
    .filter(r => (r.statusHOD||"") === "APPROVED" && (r.statusMENTOR||"") === "APPROVED")
    .filter(r => {
      const stu = users.find(x => x.id === r.studentId);
      return stu && visibleToApprover(user, stu);
    })
    .filter(r => {
      const okYear = !filters.year || String(r.year) === String(filters.year);
      const okProg = !filters.program || (r.program||"").toLowerCase().includes(filters.program.toLowerCase());
      const okSec  = !filters.section || (r.section||"").toLowerCase().includes(filters.section.toLowerCase());
      return okYear && okProg && okSec;
    });

  const rows = approved.map(r=>`
    <tr>
      <td>${r.regNo}</td><td>${r.studentName}</td><td>${r.program}</td><td>${r.section}</td>
      <td>${r.lab}</td><td>${r.reason}</td>
      <td>${formatDT(r.fromDate,r.fromTime)}</td><td>${formatDT(r.toDate,r.toTime)}</td>
      <td>${r.mentorBy?findUserNameById(r.mentorBy):""}</td>
      <td>${r.hodBy?findUserNameById(r.hodBy):""}</td>
    </tr>
  `).join("");

  const html = `
    <h1>Approved Lab Access List</h1>
    <div class="muted">Filtered export. Save as PDF.</div>
    <table>
      <tr>
        <th>Reg No</th><th>Name</th><th>Program</th><th>Section</th>
        <th>Lab</th><th>Reason</th><th>From</th><th>To</th><th>Mentor</th><th>HOD</th>
      </tr>
      ${rows || `<tr><td colspan="10">No approved records for selected filters.</td></tr>`}
    </table>
  `;
  printHTML("Approved Lab Access List", html);
}

function exportApprovedHostel(user, filters){
  const users = DB.users();
  const hostel = DB.hostel();

  const approved = hostel
    .filter(r => (r.statusCHIEF||"") === "APPROVED" && (r.statusWARDEN||"") === "APPROVED" && (r.statusSECURITY||"") === "APPROVED")
    .filter(r => {
      const stu = users.find(x => x.id === r.studentId);
      return stu && visibleToApprover(user, stu);
    })
    .filter(r => {
      const okYear = !filters.year || String(r.year) === String(filters.year);
      const okProg = !filters.program || (r.program||"").toLowerCase().includes(filters.program.toLowerCase());
      const okSec  = !filters.section || (r.section||"").toLowerCase().includes(filters.section.toLowerCase());
      return okYear && okProg && okSec;
    });

  const rows = approved.map(r=>`
    <tr>
      <td>${r.regNo}</td><td>${r.studentName}</td><td>${r.program}</td><td>${r.section}</td>
      <td>${r.purpose}</td>
      <td>${formatDT(r.fromDate,r.fromTime)}</td><td>${formatDT(r.toDate,r.toTime)}</td>
      <td>${r.chiefBy?findUserNameById(r.chiefBy):""}</td>
      <td>${r.wardenBy?findUserNameById(r.wardenBy):""}</td>
      <td>${r.securityBy?findUserNameById(r.securityBy):""}</td>
    </tr>
  `).join("");

  const html = `
    <h1>Approved Hostel Outpass List</h1>
    <div class="muted">Filtered export. Save as PDF.</div>
    <table>
      <tr>
        <th>Reg No</th><th>Name</th><th>Program</th><th>Section</th>
        <th>Purpose</th><th>From</th><th>To</th><th>Chief</th><th>Warden</th><th>Security</th>
      </tr>
      ${rows || `<tr><td colspan="10">No approved records for selected filters.</td></tr>`}
    </table>
  `;
  printHTML("Approved Hostel Outpass List", html);
}
