import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import * as resourceApi from '../../api/course_resource';
import { CourseResource } from '../../types/course';
import { CourseResourcesSection } from './CourseResourcesSection';

const mockResources: CourseResource[] = [
  {
    id: 1,
    course_id: 10,
    title: 'Python Official Tutorial',
    url: 'https://docs.python.org/3/tutorial/',
    description: 'Comprehensive Python language reference and basics.',
    created_at: '2026-10-18T10:00:00Z',
    updated_at: '2026-10-18T10:00:00Z',
  },
  {
    id: 2,
    course_id: 10,
    title: 'PostgreSQL Manual',
    url: 'https://www.postgresql.org/docs/current/',
    description: 'Official PostgreSQL SQL and administration guide.',
    created_at: '2026-10-18T11:00:00Z',
    updated_at: '2026-10-18T11:00:00Z',
  },
];

describe('CourseResourcesSection Component', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('renders learning resources with titles, descriptions, and safe external links', async () => {
    vi.spyOn(resourceApi, 'getCourseResources').mockResolvedValue(mockResources);

    render(<CourseResourcesSection courseId={10} isOwner={false} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading resources...')).not.toBeInTheDocument();
    });

    expect(screen.getByText('Learning resources (2)')).toBeInTheDocument();
    expect(screen.getByText('Python Official Tutorial')).toBeInTheDocument();
    expect(screen.getByText('PostgreSQL Manual')).toBeInTheDocument();

    const link = screen.getByRole('link', { name: /python official tutorial/i });
    expect(link).toHaveAttribute('href', 'https://docs.python.org/3/tutorial/');
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', 'noopener noreferrer');

    // Non-owners should not see edit/delete or add buttons
    expect(screen.queryByRole('button', { name: 'Add resource' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Edit' })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Delete' })).not.toBeInTheDocument();
  });

  it('renders clear empty states for owners vs non-owners', async () => {
    vi.spyOn(resourceApi, 'getCourseResources').mockResolvedValue([]);

    // 1. Owner empty state
    const { rerender } = render(<CourseResourcesSection courseId={10} isOwner={true} />);

    await waitFor(() => {
      expect(screen.getByText('No learning resources yet')).toBeInTheDocument();
    });
    expect(screen.getByText(/Add links to syllabus materials/i)).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: 'Add resource' }).length).toBeGreaterThan(0);

    // 2. Non-owner empty state
    rerender(<CourseResourcesSection courseId={10} isOwner={false} />);
    expect(
      screen.getByText('The course instructor has not added any learning resources yet.')
    ).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: 'Add resource' })).not.toBeInTheDocument();
  });

  it('allows owner to add a new resource with form modal', async () => {
    vi.spyOn(resourceApi, 'getCourseResources').mockResolvedValue([]);
    const createdResource: CourseResource = {
      id: 3,
      course_id: 10,
      title: 'MDN Web Docs',
      url: 'https://developer.mozilla.org/',
      description: 'Web standards guide',
      created_at: '2026-10-18T12:00:00Z',
      updated_at: '2026-10-18T12:00:00Z',
    };
    const createSpy = vi
      .spyOn(resourceApi, 'createCourseResource')
      .mockResolvedValue(createdResource);

    render(<CourseResourcesSection courseId={10} isOwner={true} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading resources...')).not.toBeInTheDocument();
    });

    const addButtons = screen.getAllByRole('button', { name: 'Add resource' });
    fireEvent.click(addButtons[0]);

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Add learning resource' })).toBeInTheDocument();

    const dialog = screen.getByRole('dialog');
    fireEvent.change(screen.getByLabelText('Resource title'), {
      target: { value: 'MDN Web Docs' },
    });
    fireEvent.change(screen.getByLabelText('Resource URL'), {
      target: { value: 'https://developer.mozilla.org/' },
    });
    fireEvent.change(screen.getByLabelText('Description (optional)'), {
      target: { value: 'Web standards guide' },
    });

    fireEvent.click(within(dialog).getByRole('button', { name: 'Add resource' }));

    await waitFor(() => {
      expect(createSpy).toHaveBeenCalledWith(10, {
        title: 'MDN Web Docs',
        url: 'https://developer.mozilla.org/',
        description: 'Web standards guide',
      });
    });

    expect(await screen.findByText('MDN Web Docs')).toBeInTheDocument();
  });

  it('validates form inputs and rejects empty titles and dangerous URLs', async () => {
    vi.spyOn(resourceApi, 'getCourseResources').mockResolvedValue([]);
    const createSpy = vi.spyOn(resourceApi, 'createCourseResource');

    render(<CourseResourcesSection courseId={10} isOwner={true} />);

    await waitFor(() => {
      expect(screen.queryByText('Loading resources...')).not.toBeInTheDocument();
    });

    fireEvent.click(screen.getAllByRole('button', { name: 'Add resource' })[0]);

    const dialog = screen.getByRole('dialog');
    // Submit with empty inputs
    fireEvent.click(within(dialog).getByRole('button', { name: 'Add resource' }));
    expect(await screen.findByText('Title is required.')).toBeInTheDocument();
    expect(screen.getByText('URL is required.')).toBeInTheDocument();
    expect(createSpy).not.toHaveBeenCalled();

    // Enter dangerous javascript: URL
    fireEvent.change(screen.getByLabelText('Resource title'), { target: { value: 'Script' } });
    fireEvent.change(screen.getByLabelText('Resource URL'), {
      target: { value: 'javascript:alert(1)' },
    });
    fireEvent.click(within(dialog).getByRole('button', { name: 'Add resource' }));

    expect(
      await screen.findByText('Dangerous URL schemes like javascript: or data: are not allowed.')
    ).toBeInTheDocument();
    expect(createSpy).not.toHaveBeenCalled();
  });

  it('allows owner to edit an existing resource', async () => {
    vi.spyOn(resourceApi, 'getCourseResources').mockResolvedValue([...mockResources]);
    const updatedResource: CourseResource = {
      ...mockResources[0],
      title: 'Python 3 Tutorial (Updated)',
      url: 'https://docs.python.org/3/tutorial/index.html',
    };
    const updateSpy = vi
      .spyOn(resourceApi, 'updateCourseResource')
      .mockResolvedValue(updatedResource);

    render(<CourseResourcesSection courseId={10} isOwner={true} />);

    await waitFor(() => {
      expect(screen.getByText('Python Official Tutorial')).toBeInTheDocument();
    });

    const editButtons = screen.getAllByRole('button', { name: 'Edit' });
    fireEvent.click(editButtons[0]);

    expect(screen.getByRole('heading', { name: 'Edit learning resource' })).toBeInTheDocument();
    expect(screen.getByLabelText('Resource title')).toHaveValue('Python Official Tutorial');

    fireEvent.change(screen.getByLabelText('Resource title'), {
      target: { value: 'Python 3 Tutorial (Updated)' },
    });
    fireEvent.change(screen.getByLabelText('Resource URL'), {
      target: { value: 'https://docs.python.org/3/tutorial/index.html' },
    });

    fireEvent.click(screen.getByRole('button', { name: 'Save changes' }));

    await waitFor(() => {
      expect(updateSpy).toHaveBeenCalledWith(1, {
        title: 'Python 3 Tutorial (Updated)',
        url: 'https://docs.python.org/3/tutorial/index.html',
        description: 'Comprehensive Python language reference and basics.',
      });
    });

    expect(await screen.findByText('Python 3 Tutorial (Updated)')).toBeInTheDocument();
  });

  it('allows owner to delete a resource via ConfirmModal', async () => {
    vi.spyOn(resourceApi, 'getCourseResources').mockResolvedValue([...mockResources]);
    const deleteSpy = vi.spyOn(resourceApi, 'deleteCourseResource').mockResolvedValue();

    render(<CourseResourcesSection courseId={10} isOwner={true} />);

    await waitFor(() => {
      expect(screen.getByText('Python Official Tutorial')).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByRole('button', { name: 'Delete' });
    fireEvent.click(deleteButtons[0]);

    // ConfirmModal should appear
    expect(screen.getByRole('heading', { name: 'Delete learning resource' })).toBeInTheDocument();
    expect(
      screen.getByText(/Are you sure you want to delete "Python Official Tutorial"/i)
    ).toBeInTheDocument();

    // Confirm deletion
    fireEvent.click(screen.getByRole('button', { name: 'Delete resource' }));

    await waitFor(() => {
      expect(deleteSpy).toHaveBeenCalledWith(1);
    });

    await waitFor(() => {
      expect(screen.queryByText('Python Official Tutorial')).not.toBeInTheDocument();
    });
    expect(screen.getByText('PostgreSQL Manual')).toBeInTheDocument();
  });
});
