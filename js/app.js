// app.js - seeds sample data once
(function(){
  const KEY = "sist_seeded_v1";
  if(localStorage.getItem(KEY)) return;

  const now = new Date();
  const iso = (d)=> new Date(d).toISOString();

  const users = [
    // Students
    { id:"stu1", role:"STUDENT", username:"1456111001", password:"password123", name:"Anjali R", program:"B.E CSE AIML", section:"A2", year:3, dept:"CSE(AIML)", hosteller:true },
    { id:"stu2", role:"STUDENT", username:"1456111002", password:"password123", name:"Ravi Kumar", program:"B.E CSE AIML", section:"A2", year:3, dept:"CSE(AIML)", hosteller:false },
    { id:"stu3", role:"STUDENT", username:"1456111003", password:"password123", name:"Kiran P", program:"B.E CSE AIML", section:"A1", year:3, dept:"CSE(AIML)", hosteller:true },

    // Approvers
    { id:"cc1", role:"CLASS_COORDINATOR", username:"cc01", password:"password123", name:"Class Coordinator", program:"B.E CSE AIML", section:"A2", year:3, dept:"CSE(AIML)" },
    { id:"yc1", role:"YEAR_COORDINATOR", username:"yc01", password:"password123", name:"Year Coordinator", program:"B.E CSE AIML", section:"*", year:3, dept:"CSE(AIML)" },
    { id:"hod1", role:"HOD", username:"hod01", password:"password123", name:"HOD - CSE(AIML)", program:"*", section:"*", year:"*", dept:"CSE(AIML)" },

    // Hostel chain
    { id:"w1", role:"WARDEN", username:"warden01", password:"password123", name:"Warden", gender:"FEMALE" },
    { id:"cw1", role:"CHIEF_WARDEN", username:"chiefwarden01", password:"password123", name:"Chief Warden", gender:"FEMALE" },
    { id:"sec1", role:"SECURITY", username:"security01", password:"password123", name:"Security", gender:"FEMALE" }
  ];

  const odRequests = [
    {
      id:"od1", studentId:"stu1",
      regNo:"1456111001", studentName:"Anjali R", program:"B.E CSE AIML", section:"A2",
      reason:"TECH EVENT - MINDCRAFT AI",
      fromDate:"2026-01-22", toDate:"2026-01-22",
      fromTime:"09:00", toTime:"15:00",
      proofName:"invite.pdf",
      statusCCYC:"PENDING", statusHOD:"PENDING",
      finalStatus:"PENDING",
      ccOrYcBy:null, hodBy:null,
      timeline:[{at:iso(now), by:"SYSTEM", action:"CREATED"}]
    }
  ];

  const labRequests = [
    {
      id:"lab1", studentId:"stu3",
      regNo:"1456111003", studentName:"Kiran P", program:"B.E CSE AIML", section:"A1",
      lab:"AI Lab - SCAS",
      reason:"LAB PROJECT WORK",
      fromDate:"2026-01-24", toDate:"2026-01-24",
      fromTime:"09:00", toTime:"13:00",
      proofName:"letter.jpg",
      statusFACULTY:"PENDING", statusHOD:"PENDING",
      finalStatus:"PENDING",
      facultyBy:null, hodBy:null,
      timeline:[{at:iso(now), by:"SYSTEM", action:"CREATED"}]
    }
  ];

  const hostelRequests = [
    {
      id:"hos1", studentId:"stu1",
      regNo:"1456111001", studentName:"Anjali R", program:"B.E CSE AIML", section:"A2",
      purpose:"Home visit (Parent consent required)",
      fromDate:"2026-01-23", toDate:"2026-01-23",
      fromTime:"10:00", toTime:"18:00",
      proofName:"parent_msg.png",
      statusWARDEN:"PENDING", statusCHIEF:"PENDING", statusSECURITY:"LOCKED",
      finalStatus:"PENDING",
      wardenBy:null, chiefBy:null, securityBy:null,
      timeline:[{at:iso(now), by:"SYSTEM", action:"CREATED"}]
    }
  ];

  localStorage.setItem("sist_users", JSON.stringify(users));
  localStorage.setItem("sist_od", JSON.stringify(odRequests));
  localStorage.setItem("sist_lab", JSON.stringify(labRequests));
  localStorage.setItem("sist_hostel", JSON.stringify(hostelRequests));
  localStorage.setItem("sist_lang", "en");
  localStorage.setItem("sist_theme", "light");
  localStorage.setItem(KEY,"1");
})();

/* =========================================
   AUTH (used by login.html)
========================================= */
window.APP_LOGIN = function(role, username, password){
  const users = JSON.parse(localStorage.getItem("sist_users")||"[]");
  const u = users.find(x => x.role===role && x.username===username && x.password===password);
  if(!u) return null;

  // session object used across pages
  return {
    id: u.id,
    role: u.role,
    username: u.username,
    name: u.name,
    program: u.program || "",
    section: u.section || "",
    year: u.year || "",
    dept: u.dept || "",
    hosteller: !!u.hosteller
  };
};

/* =========================================
   HELPERS
========================================= */
function uid(prefix){
  return prefix + "_" + Math.random().toString(16).slice(2) + "_" + Date.now().toString(16);
}
function pushTimeline(req, by, action){
  req.timeline = req.timeline || [];
  req.timeline.push({ at: new Date().toISOString(), by, action });
}
function finalFromStatusesOD(r){
  if(r.statusHOD==="REJECTED" || r.statusCCYC==="REJECTED") return "REJECTED";
  if(r.statusHOD==="APPROVED" && r.statusCCYC==="APPROVED") return "APPROVED";
  return "PENDING";
}
function finalFromStatusesLAB(r){
  if(r.statusHOD==="REJECTED" || r.statusFACULTY==="REJECTED") return "REJECTED";
  if(r.statusHOD==="APPROVED" && r.statusFACULTY==="APPROVED") return "APPROVED";
  return "PENDING";
}
function finalFromStatusesHOSTEL(r){
  if(r.statusWARDEN==="REJECTED" || r.statusCHIEF==="REJECTED" || r.statusSECURITY==="REJECTED") return "REJECTED";
  if(r.statusWARDEN==="APPROVED" && r.statusCHIEF==="APPROVED" && r.statusSECURITY==="APPROVED") return "APPROVED";
  return "PENDING";
}

/* =========================================
   STUDENT: create requests
========================================= */
window.createOD = function(sess, data){
  const list = Store.od();
  const req = {
    id: uid("od"),
    studentId: sess.id,
    regNo: sess.username,
    studentName: sess.name,
    program: sess.program,
    section: sess.section,
    reason: data.reason,
    fromDate: data.fromDate,
    toDate: data.toDate,
    fromTime: data.fromTime,
    toTime: data.toTime,
    proofName: data.proofName || "",
    statusCCYC: "PENDING",
    statusHOD: "PENDING",
    finalStatus: "PENDING",
    ccOrYcBy: null,
    hodBy: null,
    timeline: []
  };
  pushTimeline(req, "SYSTEM", "CREATED");
  list.unshift(req);
  Store.setOD(list);
};

window.createLAB = function(sess, data){
  const list = Store.lab();
  const req = {
    id: uid("lab"),
    studentId: sess.id,
    regNo: sess.username,
    studentName: sess.name,
    program: sess.program,
    section: sess.section,
    lab: data.lab,
    reason: data.reason,
    fromDate: data.fromDate,
    toDate: data.toDate,
    fromTime: data.fromTime,
    toTime: data.toTime,
    proofName: data.proofName || "",
    statusFACULTY: "PENDING",
    statusHOD: "PENDING",
    finalStatus: "PENDING",
    facultyBy: null,
    hodBy: null,
    timeline: []
  };
  pushTimeline(req, "SYSTEM", "CREATED");
  list.unshift(req);
  Store.setLab(list);
};

window.createHOSTEL = function(sess, data){
  const list = Store.hostel();
  const req = {
    id: uid("hos"),
    studentId: sess.id,
    regNo: sess.username,
    studentName: sess.name,
    program: sess.program,
    section: sess.section,
    purpose: data.purpose,
    fromDate: data.fromDate,
    toDate: data.toDate,
    fromTime: data.fromTime,
    toTime: data.toTime,
    proofName: data.proofName || "",
    statusWARDEN: "PENDING",
    statusCHIEF: "PENDING",
    statusSECURITY: "LOCKED",
    finalStatus: "PENDING",
    wardenBy: null,
    chiefBy: null,
    securityBy: null,
    timeline: []
  };
  pushTimeline(req, "SYSTEM", "CREATED");
  list.unshift(req);
  Store.setHostel(list);
};

/* =========================================
   APPROVERS: OD
========================================= */
window.actOD_CCYC = function(sess, id, decision){
  const list = Store.od();
  const r = list.find(x => x.id===id);
  if(!r) return;

  // only allow CC/YC to act
  if(sess.role!=="CLASS_COORDINATOR" && sess.role!=="YEAR_COORDINATOR") return;

  r.statusCCYC = decision;
  r.ccOrYcBy = sess.name;
  pushTimeline(r, sess.name, `CC/YC ${decision}`);
  r.finalStatus = finalFromStatusesOD(r);
  Store.setOD(list);
};

window.actOD_HOD = function(sess, id, decision){
  const list = Store.od();
  const r = list.find(x => x.id===id);
  if(!r) return;
  if(sess.role!=="HOD") return;

  r.statusHOD = decision;
  r.hodBy = sess.name;
  pushTimeline(r, sess.name, `HOD ${decision}`);
  r.finalStatus = finalFromStatusesOD(r);
  Store.setOD(list);
};

/* =========================================
   APPROVERS: LAB
========================================= */
window.actLAB_FACULTY = function(sess, id, decision){
  const list = Store.lab();
  const r = list.find(x => x.id===id);
  if(!r) return;

  // demo: CC/YC act as faculty/incharge
  if(sess.role!=="CLASS_COORDINATOR" && sess.role!=="YEAR_COORDINATOR") return;

  r.statusFACULTY = decision;
  r.facultyBy = sess.name;
  pushTimeline(r, sess.name, `FACULTY ${decision}`);
  r.finalStatus = finalFromStatusesLAB(r);
  Store.setLab(list);
};

window.actLAB_HOD = function(sess, id, decision){
  const list = Store.lab();
  const r = list.find(x => x.id===id);
  if(!r) return;
  if(sess.role!=="HOD") return;

  r.statusHOD = decision;
  r.hodBy = sess.name;
  pushTimeline(r, sess.name, `HOD ${decision}`);
  r.finalStatus = finalFromStatusesLAB(r);
  Store.setLab(list);
};

/* =========================================
   APPROVERS: HOSTEL
========================================= */
window.actHOSTEL_WARDEN = function(sess, id, decision){
  const list = Store.hostel();
  const r = list.find(x => x.id===id);
  if(!r) return;
  if(sess.role!=="WARDEN") return;

  r.statusWARDEN = decision;
  r.wardenBy = sess.name;
  pushTimeline(r, sess.name, `WARDEN ${decision}`);

  if(decision==="REJECTED"){
    r.finalStatus = "REJECTED";
  } else {
    r.finalStatus = finalFromStatusesHOSTEL(r);
  }
  Store.setHostel(list);
};

window.actHOSTEL_CHIEF = function(sess, id, decision){
  const list = Store.hostel();
  const r = list.find(x => x.id===id);
  if(!r) return;
  if(sess.role!=="CHIEF_WARDEN") return;

  r.statusCHIEF = decision;
  r.chiefBy = sess.name;
  pushTimeline(r, sess.name, `CHIEF_WARDEN ${decision}`);

  // unlock security only after chief approves
  if(decision==="APPROVED" && r.statusSECURITY==="LOCKED"){
    r.statusSECURITY = "PENDING";
  }

  r.finalStatus = finalFromStatusesHOSTEL(r);
  Store.setHostel(list);
};

window.actHOSTEL_SECURITY = function(sess, id, decision){
  const list = Store.hostel();
  const r = list.find(x => x.id===id);
  if(!r) return;
  if(sess.role!=="SECURITY") return;

  // security can only act if it's not locked
  if(r.statusSECURITY==="LOCKED") return;

  r.statusSECURITY = decision;
  r.securityBy = sess.name;
  pushTimeline(r, sess.name, `SECURITY ${decision}`);

  r.finalStatus = finalFromStatusesHOSTEL(r);
  Store.setHostel(list);
};
