import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { RegisterRoleSelector } from './RegisterRoleSelector';

describe('RegisterRoleSelector', () => {
  it('renders student and organization options with student selected', () => {
    const handleChange = vi.fn();
    render(<RegisterRoleSelector role="student" onChange={handleChange} />);

    const studentRadio = screen.getByLabelText('Student') as HTMLInputElement;
    const orgRadio = screen.getByLabelText('Organization') as HTMLInputElement;

    expect(studentRadio.checked).toBe(true);
    expect(orgRadio.checked).toBe(false);

    fireEvent.click(orgRadio);
    expect(handleChange).toHaveBeenCalledWith('organization');
  });

  it('renders with organization selected', () => {
    const handleChange = vi.fn();
    render(<RegisterRoleSelector role="organization" onChange={handleChange} />);

    const studentRadio = screen.getByLabelText('Student') as HTMLInputElement;
    const orgRadio = screen.getByLabelText('Organization') as HTMLInputElement;

    expect(studentRadio.checked).toBe(false);
    expect(orgRadio.checked).toBe(true);

    fireEvent.click(studentRadio);
    expect(handleChange).toHaveBeenCalledWith('student');
  });
});
