# Job Portal System with Startup Ideas & Voting Module

## Project Overview
- **Project Name**: JobPortal - Startup Ideas Platform
- **Type**: Full-stack Web Application
- **Core Functionality**: A job portal system that combines job searching/applications with a startup idea validation platform where users can submit, vote, and discuss startup ideas
- **Target Users**: Job Seekers, Recruiters, Admins, Startup Entrepreneurs

## Tech Stack
- **Frontend**: HTML, CSS, JavaScript, React.js, Tailwind CSS, jQuery
- **Backend**: Python, Django, Django REST Framework
- **Database**: MySQL
- **Authentication**: JWT (JSON Web Tokens)

## UI/UX Specification

### Color Palette
- **Primary**: #2563EB (Blue-600)
- **Primary Dark**: #1D4ED8 (Blue-700)
- **Secondary**: #10B981 (Emerald-500)
- **Accent**: #F59E0B (Amber-500)
- **Background**: #F8FAFC (Slate-50)
- **Card Background**: #FFFFFF
- **Text Primary**: #1E293B (Slate-800)
- **Text Secondary**: #64748B (Slate-500)
- **Error**: #EF4444 (Red-500)
- **Success**: #22C55E (Green-500)
- **Border**: #E2E8F0 (Slate-200)

### Typography
- **Primary Font**: 'Inter', sans-serif
- **Headings**: 'Poppins', sans-serif
- **Font Sizes**:
  - H1: 2.5rem (40px)
  - H2: 2rem (32px)
  - H3: 1.5rem (24px)
  - H4: 1.25rem (20px)
  - Body: 1rem (16px)
  - Small: 0.875rem (14px)

### Layout Structure
- **Navbar**: Fixed top, 64px height, logo left, navigation center, user actions right
- **Sidebar**: 280px width for dashboard, collapsible on mobile
- **Main Content**: Fluid with max-width 1400px, centered
- **Cards**: 16px padding, 12px border-radius, subtle shadow
- **Grid**: 12-column grid, 24px gap

### Responsive Breakpoints
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

### Visual Effects
- Card shadows: 0 1px 3px rgba(0,0,0,0.1)
- Hover transitions: 200ms ease-in-out
- Button hover: scale(1.02) with shadow increase
- Loading animations: Pulse effect
- Page transitions: Fade in 300ms

## Functionality Specification

### User Roles & Authentication

#### Admin
- Login/Logout with JWT
- Dashboard with analytics
- User management (view, block/unblock)
- Job approval (approve/reject)
- Startup idea approval (approve/reject)
- Remove reported ideas
- View all analytics charts

#### Recruiter
- Registration with company details
- Login/Logout with JWT
- Post job openings (title, description, requirements, salary, location, job type)
- Edit/Delete own jobs
- View job approval status
- View applicants with AI match scores
- Post startup ideas

#### Job Seeker
- Registration with profile
- Login/Logout with JWT
- Browse approved jobs
- Search & filter jobs (skills, location, salary, job type)
- Apply for jobs with resume upload (PDF)
- Track application status
- View AI job recommendations
- View/vote/comment/bookmark startup ideas
- Submit startup ideas

### Job Management

#### Job Creation (Recruiter)
- Title (required)
- Description (required, rich text)
- Requirements/skills (tags)
- Location (city, remote option)
- Salary range (min/max)
- Job type (Full-time, Part-time, Contract, Internship)
- Application deadline
- Number of positions

#### Job Approval Workflow
- Status: Pending → Approved/Rejected
- Admin can add rejection reason
- Approved jobs visible to seekers

### Application Management

#### Application Submission
- Select job from list
- Upload resume (PDF, max 5MB)
- Cover letter (optional)
- Submit application

#### Application Tracking
- Status: Applied → Under Review → Shortlisted → Rejected/Offered
- Timeline view of status changes

#### AI Resume-Job Matching
- Extract skills from resume
- Match with job requirements
- Generate match percentage (0-100%)
- Rank candidates for recruiters

### Search & Filter System

#### Jobs Search
- Keyword search (title, description)
- Filter by skills (multi-select)
- Filter by location (city)
- Filter by salary range (slider)
- Filter by job type (checkboxes)
- Sort by: Newest, Salary, Relevance

#### Startup Ideas Search
- Search by title/description
- Filter by category
- Sort by: Most voted, Newest, Trending

### Startup Ideas Module

#### Idea Submission
- Title (required)
- Problem statement (required)
- Proposed solution (required)
- Target audience (required)
- Business model (optional)
- Category/domain (required)
- Auto-generate AI insights on submission

#### Voting System
- Upvote/Downvote buttons
- One vote per user per idea
- Can change vote (up↔down)
- Total vote count displayed
- Vote score = upvotes - downvotes

#### Idea Interactions
- View full idea details
- Comment on ideas
- Report inappropriate ideas
- Bookmark ideas for later

#### AI Idea Insights (Auto-generated)
- Idea summary (2-3 sentences)
- Strengths analysis
- Weaknesses analysis
- Market potential score (1-10)
- Trend analysis in domain

### Admin Dashboard

#### Analytics Metrics
- Total users (seekers, recruiters)
- Total jobs (active, pending, rejected)
- Total applications
- Total startup ideas (approved, pending)
- Most-voted startup ideas (top 10)
- Trending startup domains
- Skill demand analytics
- Monthly activity charts

### Security Requirements

#### Authentication
- JWT-based authentication
- Token refresh mechanism
- Password hashing (bcrypt)

#### Authorization
- Role-based access control (RBAC)
- Admin, Recruiter, Seeker roles
- Protected API endpoints

#### Security Measures
- Input validation & sanitization
- Rate limiting on auth endpoints
- Secure file upload validation
- CORS configuration
- SQL injection prevention (ORM)

## API Endpoints

### Authentication
- POST /api/auth/register/
- POST /api/auth/login/
- POST /api/auth/refresh/
- GET /api/auth/user/

### Jobs
- GET /api/jobs/ (list approved jobs)
- POST /api/jobs/ (create job - recruiter)
- GET /api/jobs/{id}/
- PUT /api/jobs/{id}/ (update job)
- DELETE /api/jobs/{id}/ (delete job)
- GET /api/jobs/pending/ (admin - pending jobs)
- PUT /api/jobs/{id}/approve/ (admin)
- PUT /api/jobs/{id}/reject/ (admin)

### Applications
- GET /api/applications/ (my applications - seeker)
- POST /api/applications/ (apply for job)
- GET /api/applications/{id}/
- GET /api/applications/job/{job_id}/ (recruiter - applicants)
- PUT /api/applications/{id}/status/ (update status)

### Startup Ideas
- GET /api/ideas/ (list approved ideas)
- POST /api/ideas/ (submit idea)
- GET /api/ideas/{id}/
- PUT /api/ideas/{id}/ (update idea)
- DELETE /api/ideas/{id}/
- GET /api/ideas/pending/ (admin)
- PUT /api/ideas/{id}/approve/ (admin)
- PUT /api/ideas/{id}/reject/ (admin)

### Voting
- POST /api/ideas/{id}/vote/ (upvote/downvote)
- DELETE /api/ideas/{id}/vote/ (remove vote)

### Comments
- GET /api/ideas/{id}/comments/
- POST /api/ideas/{id}/comments/
- DELETE /api/comments/{id}/

### Bookmarks
- GET /api/bookmarks/
- POST /api/bookmarks/
- DELETE /api/bookmarks/{id}/

### Analytics (Admin)
- GET /api/analytics/users/
- GET /api/analytics/jobs/
- GET /api/analytics/applications/
- GET /api/analytics/ideas/
- GET /api/analytics/skills/

### AI Features
- POST /api/ai/match-resume/ (resume-job matching)
- POST /api/ai/recommend-jobs/ (job recommendations)
- POST /api/ai/analyze-idea/ (startup idea analysis)

## Database Models

### User
- id, username, email, password, role, is_active, created_at

### Profile
- user (FK), first_name, last_name, phone, resume, skills, experience

### Company (for Recruiters)
- user (FK), name, description, website, logo, location

### Job
- id, recruiter (FK), title, description, requirements, skills, location, salary_min, salary_max, job_type, status, created_at

### Application
- id, job (FK), seeker (FK), resume, cover_letter, status, match_score, applied_at

### StartupIdea
- id, user (FK), title, problem_statement, solution, target_audience, business_model, category, status, vote_score, created_at

### Vote
- id, idea (FK), user (FK), vote_type (up/down), created_at

### Comment
- id, idea (FK), user (FK), content, created_at

### Bookmark
- id, idea (FK), user (FK), created_at

## Acceptance Criteria

### Authentication
- [ ] Users can register with appropriate role
- [ ] Users can login and receive JWT token
- [ ] Protected routes require valid token
- [ ] Role-based access works correctly

### Job Management
- [ ] Recruiters can create/edit/delete jobs
- [ ] Jobs require admin approval
- [ ] Seekers can browse and search jobs
- [ ] Filters work correctly

### Applications
- [ ] Seekers can apply with resume upload
- [ ] Recruiters can view applicants
- [ ] AI match scores displayed
- [ ] Status tracking works

### Startup Ideas
- [ ] Users can submit ideas
- [ ] Admin approval required
- [ ] Voting system works (one vote per user)
- [ ] Comments and bookmarks work
- [ ] AI insights auto-generated

### Admin Dashboard
- [ ] All analytics displayed
- [ ] Charts render correctly
- [ ] User/job/idea management works

### UI/UX
- [ ] Responsive design works
- [ ] Navigation is intuitive
- [ ] Loading states shown
- [ ] Error handling user-friendly
