# Main Context Overview — Campus Resource Hub
## Project Summary
Campus Resource Hub is a full-stack web application that enables university departments, student organizations, and individuals to list, share, and reserve campus resources—from study rooms and AV equipment to lab instruments and tutoring sessions.

The platform supports:
- Search & booking with calendar integration
- Role-based access control (Student, Staff, Admin)
- Ratings, reviews, and messaging between users
- Administrative workflows for approvals, moderation, and analytics

This project demonstrates AI-first full-stack development using Cursor, GitHub Copilot, and context-aware repository design. It tests skills in Flask, Jinja2, SQL database modeling, security, and UX design while emphasizing human-AI collaboration in code generation and documentation

## Technical Overview
| Layer               | Description                                                                                                                                     |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Backend**         | Flask (Python 3.10+) following MVC architecture: controllers (routes), models (ORM / SQL), data access layer, and templates.                    |
| **Frontend**        | Jinja templates + Bootstrap 5 for responsive design and accessibility.                                                                          |
| **Database**        | SQLite. Includes tables for users, resources, bookings, messages, and reviews.                  |
| **Auth**            | Flask-Login or Flask-Security with bcrypt password hashing.                                                                                     |
| **Testing**         | pytest for unit and integration tests; optional AI-based validation in `/tests/ai_eval`.                                                        |
| **Version Control** | GitHub with documented AI contributions (`.prompt/dev_notes.md`).                                                                               |
| **AI Integration**  | Cursor context pack + prompt logs guide contextual code generation, AI-based testing, and optional features such as an “AI Resource Concierge.” |


## AI-First Repository Layout

This repository follows the AI-First Folder Structure, designed to support context-aware development:

```plaintext
.project-root/
├── .prompt/                # AI interaction logs & high-impact prompts
│   ├── dev_notes.md
│   └── golden_prompts.md
│
├── docs/
│   └── context/
│       ├── APA/            # Agility, Processes & Automation artifacts
│       ├── DT/             # Design Thinking artifacts (wireframes, personas)
│       ├── PM/             # Product Management materials (PRD, OKRs)
│       └── shared/         # Common reference items (glossary, ERD, this file)
│
├── src/                    # Flask app (controllers, models, views, static)
├── tests/                  # Unit/integration tests
│   └── ai_eval/            # Optional tests for AI-based components
└── README.md               # Setup, run instructions, AI integration notes
```

## Context File Directory & Purpose
/docs/context/shared/
- main-context.md ← You are here. High-level overview and glossary for AI tools.
- project-description.pdf / .docx ← The official brief outlining all requirements and grading criteria.
- ERD.pdf ← Entity-Relationship Diagram of the application’s database schema.

/docs/context/DT/
- wireframe.pdf ← Figma design of the Campus Resource Hub interface.
- prototype_code/ ← Auto-generated front-end scaffolding exported from Figma-to-Code.
- (Optional) Personas, journey maps, or usability test summaries.

/docs/context/PM/
- prd.md ← Product Requirements Document summarizing goals, scope, and success metrics.
- okrs.md ← Project objectives and key results for tracking progress.


/docs/context/APA/
- process-models/ ← BPMN or process flow diagrams.
- acceptance_tests.csv ← High-level functional acceptance criteria used for validation.
