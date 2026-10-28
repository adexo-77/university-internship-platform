import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { StudentPreferencesFields } from './StudentPreferencesFields';

describe('StudentPreferencesFields Component', () => {
  it('renders work mode checkboxes and preferred location input', () => {
    const onToggle = vi.fn();
    const onChangeLoc = vi.fn();

    render(
      <StudentPreferencesFields
        preferredWorkModes={['remote']}
        onToggleWorkMode={onToggle}
        preferredLocation="Addis Ababa"
        onLocationChange={onChangeLoc}
      />
    );

    expect(screen.getByLabelText('Remote')).toBeChecked();
    expect(screen.getByLabelText('On-site')).not.toBeChecked();
    expect(screen.getByLabelText('Hybrid')).not.toBeChecked();
    expect(screen.getByLabelText('Preferred Location')).toHaveValue('Addis Ababa');
  });

  it('triggers onToggleWorkMode when a checkbox is clicked', () => {
    const onToggle = vi.fn();
    const onChangeLoc = vi.fn();

    render(
      <StudentPreferencesFields
        preferredWorkModes={[]}
        onToggleWorkMode={onToggle}
        preferredLocation=""
        onLocationChange={onChangeLoc}
      />
    );

    fireEvent.click(screen.getByLabelText('Hybrid'));
    expect(onToggle).toHaveBeenCalledWith('hybrid');
  });

  it('displays location error when provided', () => {
    render(
      <StudentPreferencesFields
        preferredWorkModes={[]}
        onToggleWorkMode={vi.fn()}
        preferredLocation="Way too long location"
        onLocationChange={vi.fn()}
        locationError="Preferred location cannot exceed 80 characters."
      />
    );

    expect(screen.getByText('Preferred location cannot exceed 80 characters.')).toBeInTheDocument();
  });
});
