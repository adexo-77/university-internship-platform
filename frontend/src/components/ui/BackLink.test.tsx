import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { BackLink } from './BackLink';

const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('BackLink Component', () => {
  it('renders resolved back target and label for a detail page', () => {
    render(
      <MemoryRouter initialEntries={['/courses/10']}>
        <BackLink />
      </MemoryRouter>
    );

    const backButton = screen.getByRole('button', { name: 'Back to Courses' });
    expect(backButton).toBeInTheDocument();
  });

  it('navigates back in history when user arrived from another page (idx > 0)', () => {
    mockNavigate.mockClear();
    window.history.replaceState({ idx: 1 }, '', '/courses/10');

    render(
      <MemoryRouter initialEntries={['/courses/10']}>
        <BackLink />
      </MemoryRouter>
    );

    const backButton = screen.getByRole('button', { name: 'Back to Courses' });
    fireEvent.click(backButton);
    expect(mockNavigate).toHaveBeenCalledWith(-1);
  });

  it('navigates to fallback parent route when loaded directly (idx is 0 or absent)', () => {
    mockNavigate.mockClear();
    window.history.replaceState({ idx: 0 }, '', '/courses/10');

    render(
      <MemoryRouter initialEntries={['/courses/10']}>
        <BackLink />
      </MemoryRouter>
    );

    const backButton = screen.getByRole('button', { name: 'Back to Courses' });
    fireEvent.click(backButton);
    expect(mockNavigate).toHaveBeenCalledWith('/courses');
  });

  it('uses custom label and to path when provided as props', () => {
    mockNavigate.mockClear();
    window.history.replaceState({}, '', '/courses/10');

    render(
      <MemoryRouter initialEntries={['/courses/10']}>
        <BackLink to="/custom-parent" label="Return to Directory" />
      </MemoryRouter>
    );

    const backButton = screen.getByRole('button', { name: 'Return to Directory' });
    expect(backButton).toBeInTheDocument();
    fireEvent.click(backButton);
    expect(mockNavigate).toHaveBeenCalledWith('/custom-parent');
  });
});
