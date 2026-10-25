import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import adminFixture from '../../test/fixtures/dashboard_admin.json';
import coordinatorFixture from '../../test/fixtures/dashboard_coordinator.json';
import instructorFixture from '../../test/fixtures/dashboard_instructor.json';
import organizationFixture from '../../test/fixtures/dashboard_organization.json';
import studentFixture from '../../test/fixtures/dashboard_student.json';
import {
  AdminDashboardResponse,
  CoordinatorDashboardResponse,
  InstructorDashboardResponse,
  OrganizationDashboardResponse,
  StudentDashboardResponse,
} from '../../types/dashboard';
import { AdminDashboard } from './AdminDashboard';
import { CoordinatorDashboard } from './CoordinatorDashboard';
import { InstructorDashboard } from './InstructorDashboard';
import { OrganizationDashboard } from './OrganizationDashboard';
import { StudentDashboard } from './StudentDashboard';

// Type-check fixtures against canonical TypeScript definitions
const studentData: StudentDashboardResponse = studentFixture;
const instructorData: InstructorDashboardResponse = instructorFixture;
const organizationData: OrganizationDashboardResponse = organizationFixture;
const adminData: AdminDashboardResponse = adminFixture;
const coordinatorData: CoordinatorDashboardResponse = coordinatorFixture;

describe('Dashboards with canonical backend JSON fixtures', () => {
  it('renders student dashboard with exact contract fixture', () => {
    render(
      <MemoryRouter>
        <StudentDashboard data={studentData} />
      </MemoryRouter>
    );
    expect(screen.getByText('Vector Clocks')).toBeInTheDocument();
    expect(screen.getByText('Raft Consensus')).toBeInTheDocument();
    expect(screen.getAllByText('Distributed Systems').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('Dr. Turing')).toBeInTheDocument();
    expect(screen.getByText('Cloud Infrastructure Intern')).toBeInTheDocument();
    expect(screen.getByText(/Nexus Labs/)).toBeInTheDocument();
  });

  it('renders instructor dashboard with exact contract fixture', () => {
    render(
      <MemoryRouter>
        <InstructorDashboard data={instructorData} />
      </MemoryRouter>
    );
    expect(screen.getByText('Distributed Systems')).toBeInTheDocument();
    expect(screen.getByText('Jane Student')).toBeInTheDocument();
    expect(screen.getByText('Late')).toBeInTheDocument();
    expect(screen.getByText('1 pending')).toBeInTheDocument();
  });

  it('renders organization dashboard with exact contract fixture', () => {
    render(
      <MemoryRouter>
        <OrganizationDashboard data={organizationData} />
      </MemoryRouter>
    );
    expect(screen.getByText('Open postings')).toBeInTheDocument();
    expect(screen.getByText('Total postings')).toBeInTheDocument();
    expect(screen.getByText(/Cloud Infrastructure Intern/)).toBeInTheDocument();
    expect(screen.getByText(/Jane Student/)).toBeInTheDocument();
  });

  it('renders admin dashboard with exact contract fixture', () => {
    render(
      <MemoryRouter>
        <AdminDashboard data={adminData} />
      </MemoryRouter>
    );
    expect(screen.getByText('19 active')).toBeInTheDocument();
    expect(screen.getByText('1 pending')).toBeInTheDocument();
    expect(screen.getByText('2 pending')).toBeInTheDocument();
    expect(screen.getByText('Open internships')).toBeInTheDocument();
    expect(screen.getByText('Users by role')).toBeInTheDocument();
  });

  it('renders coordinator dashboard with exact contract fixture', () => {
    render(
      <MemoryRouter>
        <CoordinatorDashboard data={coordinatorData} />
      </MemoryRouter>
    );
    expect(screen.getByText('1 pending')).toBeInTheDocument();
    expect(screen.getByText('2 pending')).toBeInTheDocument();
    expect(screen.getByText('Open internships')).toBeInTheDocument();
    expect(screen.getByText('Completed by you')).toBeInTheDocument();
    expect(screen.getByText('Review work queues')).toBeInTheDocument();
  });
});
