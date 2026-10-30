import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as adminOrgApi from '../api/admin_organization';
import { AuthProvider } from '../context/AuthContext';
import { AdminOrganizationsPage } from './AdminOrganizationsPage';
import { AdminOrganizationItem } from '../types/admin';
import { User } from '../types/auth';

vi.mock('../api/admin_organization', () => ({
  listAdminOrganizations: vi.fn(),
  updateAdminOrganizationApproval: vi.fn(),
}));

const mockAdminUser: User = {
  id: 1,
  email: 'admin@example.edu',
  full_name: 'Admin Boss',
  role: 'admin',
  is_active: true,
  created_at: '2026-10-10T10:00:00Z',
  updated_at: '2026-10-10T10:00:00Z',
};

const mockPendingOrg: AdminOrganizationItem = {
  user_id: 50,
  organization_name: 'Starlight Corp',
  contact_name: 'Stella Star',
  email: 'contact@starlight.com',
  industry: 'Aerospace',
  location: 'Nairobi',
  approval_status: 'pending',
  approval_note: null,
  reviewed_at: null,
  reviewed_by: null,
};

describe('AdminOrganizationsPage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('selects Pending filter by default and requests pending organizations', async () => {
    vi.mocked(adminOrgApi.listAdminOrganizations).mockResolvedValue({
      items: [mockPendingOrg],
      total: 1,
      limit: 10,
      offset: 0,
    });

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockAdminUser}>
          <AdminOrganizationsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    const filterSelect = screen.getByLabelText(/approval status filter/i) as HTMLSelectElement;
    expect(filterSelect.value).toBe('pending');

    await waitFor(() => {
      expect(adminOrgApi.listAdminOrganizations).toHaveBeenCalledWith(
        expect.objectContaining({ approval_status: 'pending' })
      );
    });

    expect(await screen.findByText('Starlight Corp')).toBeInTheDocument();
  });

  it('opens approval modal and submits approval with note', async () => {
    vi.mocked(adminOrgApi.listAdminOrganizations).mockResolvedValue({
      items: [mockPendingOrg],
      total: 1,
      limit: 10,
      offset: 0,
    });
    vi.mocked(adminOrgApi.updateAdminOrganizationApproval).mockResolvedValue({
      ...mockPendingOrg,
      approval_status: 'approved',
      approval_note: 'Verified legitimate business.',
      reviewed_at: '2026-10-20T12:00:00Z',
      reviewed_by: 1,
    });

    render(
      <MemoryRouter>
        <AuthProvider initialUser={mockAdminUser}>
          <AdminOrganizationsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    const approveBtn = await screen.findByRole('button', { name: 'Approve' });
    fireEvent.click(approveBtn);

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText(/Approve Starlight Corp\?/i)).toBeInTheDocument();

    const noteInput = screen.getByLabelText(/review note/i);
    fireEvent.change(noteInput, {
      target: { value: 'Verified legitimate business.' },
    });

    const confirmBtn = within(screen.getByRole('dialog')).getByRole('button', {
      name: 'Approve',
    });
    fireEvent.click(confirmBtn);

    await waitFor(() => {
      expect(adminOrgApi.updateAdminOrganizationApproval).toHaveBeenCalledWith(50, {
        approval_status: 'approved',
        approval_note: 'Verified legitimate business.',
      });
    });

    expect(
      await screen.findByText(/Organization Starlight Corp has been approved\./i)
    ).toBeInTheDocument();
  });
});
