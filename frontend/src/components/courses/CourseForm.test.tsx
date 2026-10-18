import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { CourseForm } from './CourseForm';

describe('CourseForm Component', () => {
  it('validates required title and prevents submit when empty', async () => {
    const handleSubmit = vi.fn();
    render(<CourseForm onSubmit={handleSubmit} />);

    fireEvent.click(screen.getByRole('button', { name: 'Create course' }));

    expect(screen.getByText('Title is required.')).toBeInTheDocument();
    expect(handleSubmit).not.toHaveBeenCalled();
  });

  it('validates minimum and maximum title length', async () => {
    const handleSubmit = vi.fn();
    render(<CourseForm onSubmit={handleSubmit} />);

    const titleInput = screen.getByLabelText(/course title/i);

    // Min length < 3
    fireEvent.change(titleInput, { target: { value: 'ab' } });
    fireEvent.click(screen.getByRole('button', { name: 'Create course' }));
    expect(screen.getByText('Title must be at least 3 characters.')).toBeInTheDocument();
    expect(handleSubmit).not.toHaveBeenCalled();

    // Valid length
    fireEvent.change(titleInput, { target: { value: 'Valid Course Title' } });
    fireEvent.click(screen.getByRole('button', { name: 'Create course' }));
    expect(handleSubmit).toHaveBeenCalledWith({
      title: 'Valid Course Title',
      description: undefined,
      status: 'draft',
    });
  });

  it('submits valid title, description, and status', async () => {
    const handleSubmit = vi.fn();
    render(<CourseForm onSubmit={handleSubmit} />);

    fireEvent.change(screen.getByLabelText(/course title/i), {
      target: { value: 'Computer Architecture' },
    });
    fireEvent.change(screen.getByLabelText(/course description/i), {
      target: { value: 'Study of processor design and pipelining.' },
    });
    fireEvent.change(screen.getByLabelText(/publication status/i), {
      target: { value: 'published' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Create course' }));

    expect(handleSubmit).toHaveBeenCalledWith({
      title: 'Computer Architecture',
      description: 'Study of processor design and pipelining.',
      status: 'published',
    });
  });

  it('locks status selector when editing an already published course', () => {
    const handleSubmit = vi.fn();
    render(
      <CourseForm
        initialData={{
          id: 1,
          title: 'Published Course',
          status: 'published',
        }}
        isEdit={true}
        onSubmit={handleSubmit}
      />
    );

    expect(screen.getByText(/published courses cannot be reverted to draft/i)).toBeInTheDocument();
    expect(screen.queryByLabelText(/publication status/i)).not.toBeInTheDocument();
  });
});
