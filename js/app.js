// app.js - seeds sample data once (UPDATED flow + CC/YC split statuses)
(function(){
  const KEY = "sist_seeded_v2";
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

    // Hostel chain (NEW FLOW: Chief -> Warden -> Security)
    { id:"cw1", role:"CHIEF_WARDEN", username:"chiefwarden01", password:"password123", name:"Chief Warden", gender:"FEMALE" },
    { id:"w1", role:"WARDEN", username:"warden01", password:"password123", name:"Warden", gender:"FEMALE" },
    { id:"sec1", role:"SECURITY", username:"security01", password:"password123", name:"Security", gender:"FEMALE" }
  ];

  // OD: CC and YC have equal power (separate statuses)
  const odRequests = [
    {
      id:"od1", studentId:"stu1",
      regNo:"1456111001", studentName:"Anjali R", program:"B.E CSE AIML", section:"A2", year:3, dept:"CSE(AIML)",
      reason:"TECH EVENT - MINDCRAFT AI",
      fromDate:"2026-01-22", toDate:"2026-01-22",
      fromTime:"09:00", toTime:"15:00",
      proofName:"invite.pdf",

      statusCC:"PENDING", ccBy:null,
      statusYC:"PENDING", ycBy:null,
      statusHOD:"PENDING", hodBy:null,

      timeline:[{at:iso(now), by:"SYSTEM", action:"CREATED"}]
    }
  ];

  // LAB: Treat CC as Mentor, YC as Lab Coordinator (same equal power logic if you want later)
  const labRequests = [
    {
      id:"lab1", studentId:"stu3",
      regNo:"1456111003", studentName:"Kiran P", program:"B.E CSE AIML", section:"A1", year:3, dept:"CSE(AIML)",
      lab:"AI Lab - SCAS",
      reason:"LAB PROJECT WORK",
      fromDate:"2026-01-24", toDate:"2026-01-24",
      fromTime:"09:00", toTime:"13:00",
      proofName:"letter.jpg",

      statusMENTOR:"PENDING", mentorBy:null,
      statusHOD:"PENDING", hodBy:null,

      timeline:[{at:iso(now), by:"SYSTEM", action:"CREATED"}]
    }
  ];

  // HOSTEL: NEW FLOW Chief -> Warden -> Security
  const hostelRequests = [
    {
      id:"hos1", studentId:"stu1",
      regNo:"1456111001", studentName:"Anjali R", program:"B.E CSE AIML", section:"A2", year:3, dept:"CSE(AIML)",
      purpose:"Home visit (Parent consent required)",
      fromDate:"2026-01-23", toDate:"2026-01-23",
      fromTime:"10:00", toTime:"18:00",
      proofName:"parent_msg.png",

      statusCHIEF:"PENDING", chiefBy:null,
      statusWARDEN:"LOCKED", wardenBy:null,
      statusSECURITY:"LOCKED", securityBy:null,

      timeline:[{at:iso(now), by:"SYSTEM", action:"CREATED"}]
    }
  ];

  localStorage.setItem("sist_users", JSON.stringify(users));
  localStorage.setItem("sist_od", JSON.stringify(odRequests));
  localStorage.setItem("sist_lab", JSON.stringify(labRequests));
  localStorage.setItem("sist_hostel", JSON.stringify(hostelRequests));

  localStorage.setItem("sist_theme", "light");
  localStorage.setItem(KEY,"1");
})();
