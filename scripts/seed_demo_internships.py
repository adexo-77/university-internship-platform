"""Internship postings and applications demo seed helpers."""

from datetime import datetime, timedelta

from app.models.application import Application, ApplicationStatus
from app.models.internship import Internship, InternshipStatus, InternshipWorkMode
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import Session

POSTINGS_DATA = [
    (
        "org1",
        "Junior Web Developer Intern",
        "Develop backend REST APIs with Python/FastAPI and build reactive web applications using React and TypeScript for enterprise clients. Monthly stipend: 4,500 ETB.",
        "Proficiency in Python and JavaScript/TypeScript; understanding of RESTful APIs and relational databases; familiarity with Git.",
        "Addis Ababa",
        InternshipWorkMode.HYBRID,
        12,
        timedelta(days=28),
        InternshipStatus.OPEN,
        None,
    ),
    (
        "org1",
        "Data Analysis Intern",
        "Clean, analyze, and visualize client business metrics. Build automated data extraction pipelines and interactive dashboards. Monthly stipend: 4,000 ETB.",
        "Strong SQL skills; experience with Python data libraries (pandas, matplotlib); knowledge of basic statistical methods.",
        "Addis Ababa",
        InternshipWorkMode.REMOTE,
        10,
        timedelta(days=21),
        InternshipStatus.OPEN,
        None,
    ),
    (
        "org1",
        "Mobile Application Intern",
        "Assist in developing cross-platform mobile apps for financial services. Implement responsive screens and integrate secure endpoints. Monthly stipend: 4,200 ETB.",
        "Experience with React Native or Flutter; understanding of mobile UI/UX design patterns.",
        "Addis Ababa",
        InternshipWorkMode.ONSITE,
        12,
        timedelta(days=40),
        InternshipStatus.PENDING_REVIEW,
        None,
    ),
    (
        "org1",
        "Cloud Infrastructure Intern",
        "Draft posting for internal cloud engineering internship focusing on containerization, CI/CD pipelines, and cloud monitoring. Monthly stipend: 5,000 ETB.",
        "Basic Linux administration; experience with Docker and GitHub Actions.",
        "Addis Ababa",
        InternshipWorkMode.REMOTE,
        12,
        timedelta(days=60),
        InternshipStatus.DRAFT,
        None,
    ),
    (
        "org1",
        "Unsupervised Crypto Trading Bot Intern",
        "Develop automated algorithmic trading scripts for decentralized cryptocurrency exchanges.",
        "Python algorithmic trading knowledge.",
        "Addis Ababa",
        InternshipWorkMode.REMOTE,
        8,
        timedelta(days=14),
        InternshipStatus.REJECTED,
        "The listing involves speculative financial trading without direct educational supervision or academic mentorship. Please revise the internship scope to focus on software development or financial data engineering.",
    ),
    (
        "org2",
        "Network Support Intern",
        "Support our regional network operations center in Jimma. Participate in router configuration, fiber network monitoring, and diagnostic troubleshooting. Monthly stipend: 3,800 ETB.",
        "Knowledge of TCP/IP networking, subnets, routing protocols, and hardware troubleshooting; eager to learn.",
        "Jimma",
        InternshipWorkMode.ONSITE,
        12,
        timedelta(days=35),
        InternshipStatus.OPEN,
        None,
    ),
    (
        "org2",
        "Systems Administration Intern 2025",
        "Hands-on Linux server administration, backup automation, and internal systems maintenance for telecom operations. Monthly stipend: 3,500 ETB.",
        "Familiarity with Ubuntu/Debian server environments and Bash scripting.",
        "Jimma",
        InternshipWorkMode.ONSITE,
        10,
        -timedelta(days=15),
        InternshipStatus.CLOSED,
        None,
    ),
]


def _seed_postings(
    db: Session, users: dict[str, User], now: datetime
) -> dict[str, Internship]:
    admin = users["admin"]
    postings: dict[str, Internship] = {}
    for org_k, title, desc, req, loc, mode, wks, delta, st, note in POSTINGS_DATA:
        org = users[org_k]
        p = db.scalar(
            select(Internship).where(
                Internship.organization_id == org.id, Internship.title == title
            )
        )
        if not p:
            p = Internship(
                organization_id=org.id,
                title=title,
                description=desc,
                requirements=req,
                location=loc,
                work_mode=mode,
                duration_weeks=wks,
                application_deadline=now + delta,
                status=st,
                review_note=note,
                reviewed_by=admin.id if note else None,
                reviewed_at=now - timedelta(days=2) if note else None,
            )
            db.add(p)
            db.flush()
        postings[title] = p
    return postings


def _seed_applications(
    db: Session, postings: dict[str, Internship], users: dict[str, User], now: datetime
) -> None:
    p_web = postings["Junior Web Developer Intern"]
    p_net = postings["Network Support Intern"]
    p_sys = postings["Systems Administration Intern 2025"]
    s1, s2, s3 = users["s1"], users["s2"], users["s3"]

    app_specs = [
        (
            p_web.id,
            s1.id,
            ApplicationStatus.ACCEPTED,
            "Dear Hiring Team at Kaffa Digital Solutions, as a fourth-year IT student at Jimma University experienced in Python, FastAPI, and React, I would love to contribute to your enterprise web platforms. My capstone project involved building distributed RESTful services with strict test automation.",
            "We were very impressed by your coursework and project repository. We are excited to offer you the Junior Web Developer internship position!",
            now - timedelta(days=1),
        ),
        (
            p_web.id,
            s2.id,
            ApplicationStatus.SHORTLISTED,
            "Dear Kaffa Digital team, I am writing to express my strong interest in the Junior Web Developer Intern role. Having built multiple frontend projects using React, TypeScript, and Tailwind CSS, I am excited about the prospect of learning from your engineering team in Addis Ababa.",
            "Your frontend portfolio is strong. We have shortlisted your application for a technical interview next week.",
            now - timedelta(days=1),
        ),
        (
            p_net.id,
            s1.id,
            ApplicationStatus.REJECTED,
            "I am interested in broadening my hands-on telecommunications and network configuration experience with Gibe Valley Telecom in Jimma.",
            "Thank you for applying. We have decided to advance candidates with specialized optical networking coursework for this cohort.",
            now - timedelta(days=2),
        ),
        (
            p_net.id,
            s3.id,
            ApplicationStatus.SUBMITTED,
            "Applying for the Network Support Intern position to gain practical networking and router configuration experience in Jimma.",
            None,
            None,
        ),
        (
            p_sys.id,
            s1.id,
            ApplicationStatus.WITHDRAWN,
            "I am submitting my application for the Systems Administration internship to apply my Linux server administration skills.",
            None,
            None,
        ),
    ]
    for pid, sid, st, cl, msg, dec_at in app_specs:
        if not db.scalar(
            select(Application).where(
                Application.posting_id == pid, Application.student_id == sid
            )
        ):
            db.add(
                Application(
                    posting_id=pid,
                    student_id=sid,
                    cover_letter=cl,
                    status=st,
                    decision_message=msg,
                    decided_at=dec_at,
                )
            )
    db.flush()


def seed_internships_and_apps(
    db: Session, users: dict[str, User], now: datetime
) -> None:
    postings = _seed_postings(db, users, now)
    _seed_applications(db, postings, users, now)
