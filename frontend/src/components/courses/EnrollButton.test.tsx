import { act, fireEvent, render, screen } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { EnrollButton } from './EnrollButton';

describe('EnrollButton Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders "Enroll in course" and calls enroll API on click', async () => {
    const handleEnrollmentChange = vi.fn();
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ message: 'Enrolled successfully' }), {
        status: 201,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    render(
      <EnrollButton courseId={42} enrolled={false} onEnrollmentChange={handleEnrollmentChange} />
    );

    const button = screen.getByRole('button', { name: 'Enroll in course' });
    expect(button).toBeInTheDocument();

    await act(async () => {
      fireEvent.click(button);
    });

    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/courses/42/enrollment',
      expect.objectContaining({ method: 'POST' })
    );
    expect(handleEnrollmentChange).toHaveBeenCalledWith(true);
  });

  it('renders "Leave course" and calls leave API on click', async () => {
    const handleEnrollmentChange = vi.fn();
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Unenrolled successfully' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    render(
      <EnrollButton courseId={42} enrolled={true} onEnrollmentChange={handleEnrollmentChange} />
    );

    const button = screen.getByRole('button', { name: 'Leave course' });
    expect(button).toBeInTheDocument();

    await act(async () => {
      fireEvent.click(button);
    });

    expect(fetchSpy).toHaveBeenCalledWith(
      '/api/courses/42/enrollment',
      expect.objectContaining({ method: 'DELETE' })
    );
    expect(handleEnrollmentChange).toHaveBeenCalledWith(false);
  });

  it('renders error message when API call fails', async () => {
    const handleEnrollmentChange = vi.fn();
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Already enrolled in this course' }), {
        status: 409,
        headers: { 'Content-Type': 'application/json' },
      })
    );

    render(
      <EnrollButton courseId={42} enrolled={false} onEnrollmentChange={handleEnrollmentChange} />
    );

    const button = screen.getByRole('button', { name: 'Enroll in course' });
    await act(async () => {
      fireEvent.click(button);
    });

    expect(screen.getByText('Already enrolled in this course')).toBeInTheDocument();
    expect(handleEnrollmentChange).not.toHaveBeenCalled();
  });
});
