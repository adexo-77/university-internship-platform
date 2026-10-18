import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { EnrolledStudent } from '../../types/course';
import { StudentRosterTable } from './StudentRosterTable';

describe('StudentRosterTable Component', () => {
  it('renders student roster with names and emails', () => {
    const students: EnrolledStudent[] = [
      {
        student_id: 10,
        name: 'Alice Johnson',
        email: 'alice@uni.edu',
        enrolled_at: '2026-10-18T10:00:00Z',
      },
      {
        student_id: 11,
        name: 'Bob Smith',
        email: 'bob@uni.edu',
        enrolled_at: '2026-10-18T11:00:00Z',
      },
    ];

    render(<StudentRosterTable students={students} />);

    expect(screen.getByText('Alice Johnson')).toBeInTheDocument();
    expect(screen.getByText('alice@uni.edu')).toBeInTheDocument();
    expect(screen.getByText('Bob Smith')).toBeInTheDocument();
    expect(screen.getByText('bob@uni.edu')).toBeInTheDocument();
  });

  it('renders empty message when roster has no students', () => {
    render(<StudentRosterTable students={[]} />);
    expect(screen.getByText('No students enrolled yet.')).toBeInTheDocument();
  });
});
