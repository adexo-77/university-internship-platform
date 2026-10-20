import React from 'react';
import { AdminOrganizationItem } from '../../types/admin';
import { Badge, Button, Column, DataTable } from '../ui';

export interface AdminOrganizationsTableProps {
  organizations: AdminOrganizationItem[];
  onApprove: (org: AdminOrganizationItem) => void;
  onReject: (org: AdminOrganizationItem) => void;
  emptyMessage?: string;
}

export const AdminOrganizationsTable: React.FC<AdminOrganizationsTableProps> = ({
  organizations,
  onApprove,
  onReject,
  emptyMessage = 'No organizations found matching your filter.',
}) => {
  const getStatusVariant = (status: string): 'success' | 'attention' | 'error' | 'neutral' => {
    switch (status) {
      case 'approved':
        return 'success';
      case 'pending':
        return 'attention';
      case 'rejected':
        return 'error';
      default:
        return 'neutral';
    }
  };

  const columns: Column<AdminOrganizationItem>[] = [
    {
      key: 'organization_name',
      header: 'Organization',
      render: (item) => (
        <div>
          <span className="font-medium text-ink block">{item.organization_name}</span>
          {item.location && <span className="text-xs text-pencil">{item.location}</span>}
        </div>
      ),
    },
    {
      key: 'contact_name',
      header: 'Contact',
      render: (item) => <span className="text-ink">{item.contact_name}</span>,
    },
    {
      key: 'email',
      header: 'Email',
      render: (item) => <span className="font-mono text-xs text-pencil">{item.email}</span>,
    },
    {
      key: 'approval_status',
      header: 'Status',
      render: (item) => (
        <Badge variant={getStatusVariant(item.approval_status)}>{item.approval_status}</Badge>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (item) => (
        <div className="flex items-center gap-2">
          {item.approval_status !== 'approved' && (
            <Button type="button" variant="quiet" size="sm" onClick={() => onApprove(item)}>
              Approve
            </Button>
          )}
          {item.approval_status !== 'rejected' && (
            <Button type="button" variant="quiet" size="sm" onClick={() => onReject(item)}>
              Reject
            </Button>
          )}
        </div>
      ),
    },
  ];

  return (
    <DataTable
      columns={columns}
      data={organizations}
      keyExtractor={(item) => String(item.user_id)}
      emptyMessage={emptyMessage}
    />
  );
};
