import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import {
  AdminDashboardResponse,
  InstructorDashboardResponse,
  OrganizationDashboardResponse,
  StudentDashboardResponse,
} from '../../types/dashboard';
import { AdminDashboard } from './AdminDashboard';
import { InstructorDashboard } from './InstructorDashboard';
import { OrganizationDashboard } from './OrganizationDashboard';
import { StudentDashboard } from './StudentDashboard';

const studentBackendFixture: StudentDashboardResponse = {
  due_next: [
    {
      assignment_id: 2,
      course_id: 1,
      course_title: 'Distributed Systems',
      title: 'Vector Clocks',
      due_at: '2026-10-27T05:30:00Z',
      max_points: 50,
    },
  ],
  recent_grades: [
    {
      submission_id: 1,
      assignment_id: 1,
      assignment_title: 'Raft Consensus',
      course_title: 'Distributed Systems',
      grade: 95,
      max_points: 100,
      graded_at: '2026-10-22T05:30:00Z',
    },
  ],
  courses: [
    {
      course_id: 1,
      title: 'Distributed Systems',
      instructor_name: 'Dr. Turing',
      assignments_total: 2,
      assignments_submitted: 1,
      progress_percent: 50.0,
      average_grade_percent: 95.0,
    },
  ],
  applications: {
    counts_by_status: {
      submitted: 0,
      shortlisted: 1,
      accepted: 0,
      rejected: 0,
      withdrawn: 0,
    },
    counts: {
      submitted: 0,
      shortlisted: 1,
      accepted: 0,
      rejected: 0,
      withdrawn: 0,
    },
    recent: [
      {
        id: 1,
        application_id: 1,
        posting_id: 1,
        posting_title: 'Cloud Infrastructure Intern',
        organization_name: 'Nexus Labs',
        status: 'shortlisted',
        applied_at: '2026-10-23T05:30:00Z',
      },
    ],
  },
  profile_complete: true,
};

const instructorBackendFixture: InstructorDashboardResponse = {
  courses: [
    {
      course_id: 1,
      title: 'Distributed Systems',
      status: 'published',
      enrolled_count: 1,
      assignments_count: 2,
      submissions_awaiting_grading: 1,
      awaiting_grading_count: 1,
      average_grade_percent: 95.0,
    },
  ],
  needs_grading: [
    {
      submission_id: 2,
      assignment_id: 2,
      assignment_title: 'Vector Clocks',
      course_id: 1,
      course_title: 'Distributed Systems',
      student_name: 'Jane Student',
      submitted_at: '2026-10-23T05:30:00Z',
      late: true,
      is_late: true,
    },
  ],
};

const organizationBackendFixture: OrganizationDashboardResponse = {
  approval_status: 'approved',
  approval_note: null,
  postings: {
    counts_by_status: {
      draft: 1,
      pending_review: 1,
      open: 1,
      rejected: 0,
      closed: 0,
    },
    total: 3,
  },
  posting_counts: {
    draft: 1,
    pending_review: 1,
    open: 1,
    rejected: 0,
    closed: 0,
  },
  applications_awaiting_decision: 1,
  recent_applications: [
    {
      application_id: 1,
      posting_id: 1,
      posting_title: 'Cloud Infrastructure Intern',
      applicant_name: 'Jane Student',
      applicant_email: 'jane@test.edu',
      status: 'submitted',
      applied_at: '2026-10-23T05:30:00Z',
    },
  ],
};

const adminBackendFixture: AdminDashboardResponse = {
  users_by_role: {
    student: 10,
    instructor: 4,
    organization: 3,
    admin: 2,
  },
  users_active_count: 19,
  active_users_count: 19,
  users_total_count: 19,
  organizations_pending_approval: 1,
  postings_pending_review: 2,
  internships_pending_review: 2,
  open_internships: 5,
  courses_by_status: {
    draft: 1,
    published: 8,
    archived: 0,
  },
  applications_by_status: {
    submitted: 6,
    shortlisted: 3,
    accepted: 2,
    rejected: 1,
    withdrawn: 0,
  },
};

describe('Dashboards with real backend response fixtures', () => {
  it('renders student dashboard with exact backend response fixture', () => {
    render(
      <MemoryRouter>
        <StudentDashboard data={studentBackendFixture} />
      </MemoryRouter>
    );
    expect(screen.getByText('Vector Clocks')).toBeInTheDocument();
    expect(screen.getByText('Raft Consensus')).toBeInTheDocument();
    expect(screen.getAllByText('Distributed Systems').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Dr. Turing')).toBeInTheDocument();
    expect(screen.getByText('Cloud Infrastructure Intern')).toBeInTheDocument();
    expect(screen.getByText(/Nexus Labs/)).toBeInTheDocument();
  });

  it('renders instructor dashboard with exact backend response fixture', () => {
    render(
      <MemoryRouter>
        <InstructorDashboard data={instructorBackendFixture} />
      </MemoryRouter>
    );
    expect(screen.getByText('Distributed Systems')).toBeInTheDocument();
    expect(screen.getByText('Jane Student')).toBeInTheDocument();
    expect(screen.getByText('Late')).toBeInTheDocument();
    expect(screen.getByText('1 pending')).toBeInTheDocument();
  });

  it('renders organization dashboard with exact backend response fixture', () => {
    render(
      <MemoryRouter>
        <OrganizationDashboard data={organizationBackendFixture} />
      </MemoryRouter>
    );
    expect(screen.getByText('Open postings')).toBeInTheDocument();
    expect(screen.getByText('Total postings')).toBeInTheDocument();
    expect(screen.getByText(/Cloud Infrastructure Intern/)).toBeInTheDocument();
    expect(screen.getByText(/Jane Student/)).toBeInTheDocument();
  });

  it('renders admin dashboard with exact backend response fixture', () => {
    render(
      <MemoryRouter>
        <AdminDashboard data={adminBackendFixture} />
      </MemoryRouter>
    );
    expect(screen.getByText('19 active')).toBeInTheDocument();
    expect(screen.getByText('1 pending')).toBeInTheDocument();
    expect(screen.getByText('2 pending')).toBeInTheDocument();
    expect(screen.getByText('Open internships')).toBeInTheDocument();
    expect(screen.getByText('Users by role')).toBeInTheDocument();
  });
});
