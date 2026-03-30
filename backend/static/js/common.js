// common.js - auth, theme, rendering helpers, approvals, exports

(function () {
  const theme = localStorage.getItem("sist_theme") || "light";
  document.documentElement.setAttribute("data-theme", theme);
})();

const DB = {
  users: () => JSON.parse(localStorage.getItem("sist_users") || "[]"),
  od: () => JSON.parse(localStorage.getItem("sist_od") || "[]"),
  lab: () => JSON.parse(localStorage.getItem("sist_lab") || "[]"),
  hostel: () => JSON.parse(localStorage.getItem("sist_hostel") || "[]"),

  saveOD: (arr) => localStorage.setItem("sist_od", JSON.stringify(arr)),
  saveLab: (arr) => localStorage.setItem("sist_lab", JSON.stringify(arr)),
  saveHostel: (arr) => localStorage.setItem("sist_hostel", JSON.stringify(arr)),
};

function goTo(path) {
  const finalPath = path.startsWith("/") ? path : `/${path}`;
  window.location.replace(finalPath);
}

function setTheme(next) {
  localStorage.setItem("sist_theme", next);
  document.documentElement.setAttribute("data-theme", next);
  updateThemeButtonText();
}

function toggleTheme() {
  const cur = localStorage.getItem("sist_theme") || "light";
  setTheme(cur === "light" ? "dark" : "light");
}

function updateThemeButtonText() {
  const cur = localStorage.getItem("sist_theme") || "light";
  const btn = document.querySelector("[data-theme-toggle]");
  if (btn) {
    btn.textContent = cur === "light" ? "Dark mode" : "Light mode";
  }
}

function session() {
  try {
    return JSON.parse(localStorage.getItem("sist_session") || "null");
  } catch {
    return null;
  }
}

function currentUser() {
  try {
    const raw = localStorage.getItem("sist_current_user");
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function requireAuth() {
  const rawSession = localStorage.getItem("sist_session");
  const rawCurrentUser = localStorage.getItem("sist_current_user");

  if (!rawSession || !rawCurrentUser) {
    goTo("/login.html");
    return null;
  }

  try {
    const sess = JSON.parse(rawSession);
    const user = JSON.parse(rawCurrentUser);

    if (!sess || !user || !sess.userId || !user.id) {
      localStorage.removeItem("sist_session");
      localStorage.removeItem("sist_current_user");
      localStorage.removeItem("sist_current_role");
      goTo("/login.html");
      return null;
    }

    if (String(sess.userId) !== String(user.id)) {
      localStorage.removeItem("sist_session");
      localStorage.removeItem("sist_current_user");
      localStorage.removeItem("sist_current_role");
      goTo("/login.html");
      return null;
    }

    return user;
  } catch (err) {
    console.error("Session parse error:", err);
    localStorage.removeItem("sist_session");
    localStorage.removeItem("sist_current_user");
    localStorage.removeItem("sist_current_role");
    goTo("/login.html");
    return null;
  }
}

function signOut() {
  localStorage.removeItem("sist_session");
  localStorage.removeItem("sist_current_user");
  localStorage.removeItem("sist_current_role");
  goTo("/login.html");
}

function statusClass(status) {
  const s = (status || "").toUpperCase();
  if (s === "APPROVED") return "approved";
  if (s === "REJECTED") return "rejected";
  if (s === "LOCKED") return "locked";
  return "pending";
}

function badge(status) {
  const s = (status || "PENDING").toUpperCase();
  return `<span class="badge ${statusClass(s)}">${s}</span>`;
}

function formatDT(date, time) {
  const d = date || "-";
  const t = time || "-";
  return `${d} ${t}`;
}

function formatDisplayDate(dateStr) {
  if (!dateStr) return "-";
  const d = new Date(dateStr);
  if (Number.isNaN(d.getTime())) return dateStr;
  return d.toLocaleDateString("en-GB");
}

function formatNowDate() {
  return new Date().toLocaleDateString("en-GB");
}

function deriveCCYC(rec) {
  const a = (rec.statusCC || "PENDING").toUpperCase();
  const b = (rec.statusYC || "PENDING").toUpperCase();
  if (a === "REJECTED" || b === "REJECTED") return "REJECTED";
  if (a === "APPROVED" || b === "APPROVED") return "APPROVED";
  return "PENDING";
}

function canHodApproveOD(rec) {
  const ccyc = deriveCCYC(rec);
  return ccyc === "APPROVED" && (rec.statusHOD || "PENDING") === "PENDING";
}

function visibleToApprover(user, student) {
  if (user.role === "CLASS_COORDINATOR") {
    return student.program === user.program && student.section === user.section && student.year === user.year;
  }
  if (user.role === "YEAR_COORDINATOR") {
    return student.program === user.program && student.year === user.year;
  }
  if (user.role === "HOD") {
    return student.dept === user.dept || student.department === user.department;
  }
  return true;
}

function findUserNameById(id) {
  const u = DB.users().find(x => String(x.id) === String(id));
  if (u) return u.name || u.full_name || u.username || "—";

  const current = currentUser();
  if (current && String(current.id) === String(id)) {
    return current.name || current.full_name || current.username || "—";
  }

  return "—";
}

function escapeHtml(str) {
  return String(str || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function getLetterHeaderHTML() {
  return `
    <div class="letter-header">
      <img src="/static/assets/sathyabama_logo.png" alt="Sathyabama Logo" class="logo" />
      <div class="header-text">
        <div class="uni-name">SATHYABAMA</div>
        <div class="uni-sub">INSTITUTE OF SCIENCE AND TECHNOLOGY</div>
        <div class="uni-sub">(DEEMED TO BE UNIVERSITY)</div>
      </div>
    </div>
      <div class="header-line"></div>
  `;
}

function printHTML(title, html) {
  const w = window.open("", "_blank");
  w.document.write(`
  <html>
    <head>
      <title>${escapeHtml(title)}</title>
      <meta charset="utf-8"/>
      <style>
        @page {
          size: A4;
          margin: 18mm;
        }

        body{
          font-family: Arial, sans-serif;
          color:#111;
          padding: 0;
          margin: 0;
          line-height: 1.45;
        }

        .page{
          padding: 8px 10px;
        }

        .letter-header{
          display:flex;
          align-items:center;
          gap:16px;
          margin-bottom: 8px;
        }

        .logo{
          width: 110px;
          height: auto;
          object-fit: contain;
        }

        .header-text{
          flex:1;
        }

        .uni-name{
          font-size: 34px;
          font-weight: 800;
          color:#0d47a1;
          letter-spacing: 2px;
          line-height: 1.05;
        }

        .uni-sub{
          font-size: 16px;
          font-weight: 700;
          color:#0d47a1;
          letter-spacing: 1px;
          margin-top: 4px;
        }

        .header-line{
          border-top: 3px solid #0d47a1;
          margin: 6px 0 20px;
        }

        .doc-title{
          text-align:center;
          font-size: 20px;
          font-weight: 800;
          margin: 8px 0 4px;
        }

        .muted{
          color:#555;
          font-size: 12px;
          text-align:right;
          margin-bottom: 10px;
        }

        .status-box{
          margin: 12px 0 18px;
          padding: 12px 14px;
          border: 1px solid #cfd8dc;
          background:#f8fafc;
          font-size: 14px;
        }

        p{
          font-size: 14px;
          margin: 10px 0;
        }

        table{
          width:100%;
          border-collapse: collapse;
          margin-top: 14px;
        }

        th,td{
          border:1px solid #cfd8dc;
          padding:10px 12px;
          font-size: 13px;
          text-align:left;
          vertical-align: top;
        }

        th{
          background:#f1f5f9;
          width: 34%;
          font-weight: 700;
        }

        .approval-grid{
          margin-top: 24px;
          display:grid;
          grid-template-columns: repeat(2, 1fr);
          gap:16px;
        }

        .approval-grid.three{
          grid-template-columns: repeat(3, 1fr);
        }

        .approval-box{
          border-top: 1px dashed #888;
          padding-top: 10px;
          min-height: 54px;
          font-size: 13px;
        }

        .approval-box b{
          display:block;
          margin-bottom: 5px;
        }

        .footer-note{
          margin-top: 18px;
          font-size: 12px;
          color:#555;
        }

        .final-note{
          margin-top: 20px;
          font-size: 14px;
        }
      </style>
    </head>
    <body>
      <div class="page">
        ${html}
      </div>
      <script>
        window.onload = ()=> { window.print(); };
      <\/script>
    </body>
  </html>`);
  w.document.close();
}

function downloadODLetter(rec) {
  const ccName = rec.ccByName || (rec.ccBy ? findUserNameById(rec.ccBy) : "—");
  const ycName = rec.ycByName || (rec.ycBy ? findUserNameById(rec.ycBy) : "—");
  const hodName = rec.hodByName || (rec.hodBy ? findUserNameById(rec.hodBy) : "—");

  const html = `
    ${getLetterHeaderHTML()}
    <div class="doc-title">ON-DUTY APPROVAL LETTER</div>
    <div class="muted">Date: ${formatNowDate()}</div>

    <div class="status-box">
      This is to certify that the following <b>On-Duty (OD)</b> request has been digitally approved through the SIST Management System.
    </div>

    <table>
      <tr><th>Register Number</th><td>${escapeHtml(rec.regNo)}</td></tr>
      <tr><th>Student Name</th><td>${escapeHtml(rec.studentName)}</td></tr>
      <tr><th>Program</th><td>${escapeHtml(rec.program)}</td></tr>
      <tr><th>Section</th><td>${escapeHtml(rec.section)}</td></tr>
      <tr><th>Reason / Subject</th><td>${escapeHtml(rec.reason)}</td></tr>
      <tr><th>From</th><td>${escapeHtml(formatDT(rec.fromDate, rec.fromTime))}</td></tr>
      <tr><th>To</th><td>${escapeHtml(formatDT(rec.toDate, rec.toTime))}</td></tr>
    </table>

    <div class="approval-grid">
      <div class="approval-box">
        <b>Class Coordinator Approved By</b>
        ${escapeHtml(ccName)}
      </div>
      <div class="approval-box">
        <b>Year Coordinator Approved By</b>
        ${escapeHtml(ycName)}
      </div>
    </div>

    <div class="approval-grid" style="margin-top:16px;">
      <div class="approval-box">
        <b>HOD Approved By</b>
        ${escapeHtml(hodName)}
      </div>
      <div class="approval-box">
        <b>Final Status</b>
        APPROVED
      </div>
    </div>

    <div class="final-note">
      The student is permitted to avail On-Duty for the above-mentioned period and purpose, subject to institutional rules and verification.
    </div>

    <div class="footer-note">
      Digitally generated by SIST Management System.
    </div>
  `;
  printHTML("OD Approval Letter", html);
}

function downloadLabLetter(rec) {
  const mentorName = rec.mentorByName || (rec.mentorBy ? findUserNameById(rec.mentorBy) : "—");
  const hodName = rec.hodByName || (rec.hodBy ? findUserNameById(rec.hodBy) : "—");

  const html = `
    ${getLetterHeaderHTML()}
    <div class="doc-title">LAB ACCESS APPROVAL LETTER</div>
    <div class="muted">Date: ${formatNowDate()}</div>

    <div class="status-box">
      This is to certify that the following <b>Lab Access Request</b> has been digitally approved through the SIST Management System.
    </div>

    <table>
      <tr><th>Register Number</th><td>${escapeHtml(rec.regNo)}</td></tr>
      <tr><th>Student Name</th><td>${escapeHtml(rec.studentName)}</td></tr>
      <tr><th>Program</th><td>${escapeHtml(rec.program)}</td></tr>
      <tr><th>Section</th><td>${escapeHtml(rec.section)}</td></tr>
      <tr><th>Lab</th><td>${escapeHtml(rec.lab)}</td></tr>
      <tr><th>Reason</th><td>${escapeHtml(rec.reason)}</td></tr>
      <tr><th>From</th><td>${escapeHtml(formatDT(rec.fromDate, rec.fromTime))}</td></tr>
      <tr><th>To</th><td>${escapeHtml(formatDT(rec.toDate, rec.toTime))}</td></tr>
    </table>

    <div class="approval-grid">
      <div class="approval-box">
        <b>Mentor Approved By</b>
        ${escapeHtml(mentorName)}
      </div>
      <div class="approval-box">
        <b>HOD Approved By</b>
        ${escapeHtml(hodName)}
      </div>
    </div>

    <div class="final-note">
      The student is permitted to access the specified laboratory for the approved duration, subject to lab rules and supervision.
    </div>

    <div class="footer-note">
      Digitally generated by SIST Management System.
    </div>
  `;
  printHTML("Lab Access Approval Letter", html);
}

function downloadHostelLetter(rec) {
  const chief = rec.chiefByName || (rec.chiefBy ? findUserNameById(rec.chiefBy) : "—");
  const warden = rec.wardenByName || (rec.wardenBy ? findUserNameById(rec.wardenBy) : "—");
  const security = rec.securityByName || (rec.securityBy ? findUserNameById(rec.securityBy) : "—");

  const html = `
    ${getLetterHeaderHTML()}
    <div class="doc-title">HOSTEL OUTPASS APPROVAL LETTER</div>
    <div class="muted">Date: ${formatNowDate()}</div>

    <div class="status-box">
      This is to certify that the following <b>Hostel Outpass Request</b> has been digitally approved through the SIST Management System.
    </div>

    <table>
      <tr><th>Register Number</th><td>${escapeHtml(rec.regNo)}</td></tr>
      <tr><th>Student Name</th><td>${escapeHtml(rec.studentName)}</td></tr>
      <tr><th>Program</th><td>${escapeHtml(rec.program)}</td></tr>
      <tr><th>Section</th><td>${escapeHtml(rec.section)}</td></tr>
      <tr><th>Purpose</th><td>${escapeHtml(rec.purpose)}</td></tr>
      <tr><th>From</th><td>${escapeHtml(formatDT(rec.fromDate, rec.fromTime))}</td></tr>
      <tr><th>To</th><td>${escapeHtml(formatDT(rec.toDate, rec.toTime))}</td></tr>
    </table>

    <div class="approval-grid three">
      <div class="approval-box">
        <b>Chief Warden Approved By</b>
        ${escapeHtml(chief)}
      </div>
      <div class="approval-box">
        <b>Warden Approved By</b>
        ${escapeHtml(warden)}
      </div>
      <div class="approval-box">
        <b>Security Approved By</b>
        ${escapeHtml(security)}
      </div>
    </div>

    <div class="final-note">
      The student is permitted to leave and return during the approved outpass period, subject to hostel and campus security rules.
    </div>

    <div class="footer-note">
      Digitally generated by SIST Management System.
    </div>
  `;
  printHTML("Hostel Outpass Approval Letter", html);
}

function exportApprovedOD(data, filters = {}) {
  let list = (data || []).filter(r => (r.finalStatus || "").toUpperCase() === "APPROVED");

  if (filters.program) {
    const p = filters.program.trim().toLowerCase();
    list = list.filter(r => (r.program || "").toLowerCase().includes(p));
  }

  if (filters.section) {
    const s = filters.section.trim().toLowerCase();
    list = list.filter(r => (r.section || "").toLowerCase().includes(s));
  }

  if (filters.year) {
    list = list.filter(r => String(r.year || "") === String(filters.year));
  }

  if (filters.fromDate || filters.toDate) {
    const rangeStart = filters.fromDate || "0000-01-01";
    const rangeEnd   = filters.toDate   || "9999-12-31";
    list = list.filter(r => r.fromDate <= rangeEnd && r.toDate >= rangeStart);
  }

  const rows = list.map((r, i) => `
    <tr>
      <td>${i + 1}</td>
      <td>${escapeHtml(r.regNo || "-")}</td>
      <td>${escapeHtml(r.studentName || "-")}</td>
      <td>${escapeHtml(r.program || "-")}</td>
      <td>${escapeHtml(r.section || "-")}</td>
      <td>${escapeHtml(r.reason || "-")}</td>
      <td>${escapeHtml(formatDT(r.fromDate, r.fromTime))}</td>
      <td>${escapeHtml(formatDT(r.toDate, r.toTime))}</td>
      <td>${escapeHtml(r.ccByName || "—")}</td>
      <td>${escapeHtml(r.ycByName || "—")}</td>
      <td>${escapeHtml(r.hodByName || "—")}</td>
    </tr>
  `).join("");

  const html = `
    ${getLetterHeaderHTML()}
    <div class="doc-title">APPROVED OD LIST</div>
    <div class="muted">Generated on: ${formatNowDate()}</div>

    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Reg No</th>
          <th>Name</th>
          <th>Program</th>
          <th>Section</th>
          <th>Reason</th>
          <th>From</th>
          <th>To</th>
          <th>CC</th>
          <th>YC</th>
          <th>HOD</th>
        </tr>
      </thead>
      <tbody>
        ${rows || `<tr><td colspan="11">No approved OD records found.</td></tr>`}
      </tbody>
    </table>

    <div class="footer-note">
      Digitally generated by SIST Management System.
    </div>
  `;

  printHTML("Approved OD List", html);
}

function exportApprovedLab(_user, filters = {}) {
  let list = DB.lab().filter(r => (r.statusHOD || "").toUpperCase() === "APPROVED");

  if (filters.program) {
    const p = filters.program.trim().toLowerCase();
    list = list.filter(r => (r.program || "").toLowerCase().includes(p));
  }

  if (filters.section) {
    const s = filters.section.trim().toLowerCase();
    list = list.filter(r => (r.section || "").toLowerCase().includes(s));
  }

  if (filters.year) {
    list = list.filter(r => String(r.year || "") === String(filters.year));
  }

  const rows = list.map((r, i) => `
    <tr>
      <td>${i + 1}</td>
      <td>${escapeHtml(r.regNo || "-")}</td>
      <td>${escapeHtml(r.studentName || "-")}</td>
      <td>${escapeHtml(r.program || "-")}</td>
      <td>${escapeHtml(r.section || "-")}</td>
      <td>${escapeHtml(r.lab || "-")}</td>
      <td>${escapeHtml(r.reason || "-")}</td>
      <td>${escapeHtml(formatDT(r.fromDate, r.fromTime))}</td>
      <td>${escapeHtml(formatDT(r.toDate, r.toTime))}</td>
      <td>${escapeHtml(findUserNameById(r.mentorBy))}</td>
      <td>${escapeHtml(findUserNameById(r.hodBy))}</td>
    </tr>
  `).join("");

  const html = `
    ${getLetterHeaderHTML()}
    <div class="doc-title">APPROVED LAB ACCESS LIST</div>
    <div class="muted">Generated on: ${formatNowDate()}</div>

    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Reg No</th>
          <th>Name</th>
          <th>Program</th>
          <th>Section</th>
          <th>Lab</th>
          <th>Reason</th>
          <th>From</th>
          <th>To</th>
          <th>Mentor</th>
          <th>HOD</th>
        </tr>
      </thead>
      <tbody>
        ${rows || `<tr><td colspan="11">No approved Lab records found.</td></tr>`}
      </tbody>
    </table>

    <div class="footer-note">
      Digitally generated by SIST Management System.
    </div>
  `;

  printHTML("Approved Lab List", html);
}

function exportApprovedHostel(_user, filters = {}) {
  let list = DB.hostel().filter(r => (r.statusSECURITY || "").toUpperCase() === "APPROVED");

  if (filters.program) {
    const p = filters.program.trim().toLowerCase();
    list = list.filter(r => (r.program || "").toLowerCase().includes(p));
  }

  if (filters.section) {
    const s = filters.section.trim().toLowerCase();
    list = list.filter(r => (r.section || "").toLowerCase().includes(s));
  }

  if (filters.year) {
    list = list.filter(r => String(r.year || "") === String(filters.year));
  }

  const rows = list.map((r, i) => `
    <tr>
      <td>${i + 1}</td>
      <td>${escapeHtml(r.regNo || "-")}</td>
      <td>${escapeHtml(r.studentName || "-")}</td>
      <td>${escapeHtml(r.program || "-")}</td>
      <td>${escapeHtml(r.section || "-")}</td>
      <td>${escapeHtml(r.purpose || "-")}</td>
      <td>${escapeHtml(formatDT(r.fromDate, r.fromTime))}</td>
      <td>${escapeHtml(formatDT(r.toDate, r.toTime))}</td>
      <td>${escapeHtml(findUserNameById(r.chiefBy))}</td>
      <td>${escapeHtml(findUserNameById(r.wardenBy))}</td>
      <td>${escapeHtml(findUserNameById(r.securityBy))}</td>
    </tr>
  `).join("");

  const html = `
    ${getLetterHeaderHTML()}
    <div class="doc-title">APPROVED HOSTEL OUTPASS LIST</div>
    <div class="muted">Generated on: ${formatNowDate()}</div>

    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Reg No</th>
          <th>Name</th>
          <th>Program</th>
          <th>Section</th>
          <th>Purpose</th>
          <th>From</th>
          <th>To</th>
          <th>Chief Warden</th>
          <th>Warden</th>
          <th>Security</th>
        </tr>
        </thead>
      <tbody>
        ${rows || `<tr><td colspan="11">No approved Hostel records found.</td></tr>`}
      </tbody>
    </table>

    <div class="footer-note">
      Digitally generated by SIST Management System.
    </div>
  `;

  printHTML("Approved Hostel List", html);
}