import { fireEvent, render, screen } from '@testing-library/react';
import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ErrorBoundary } from './ErrorBoundary';

const FaultyComponent: React.FC<{ shouldThrow?: boolean }> = ({ shouldThrow }) => {
  if (shouldThrow) {
    throw new Error('Test crash in child component');
  }
  return <div>Component rendered safely</div>;
};

describe('ErrorBoundary', () => {
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  it('renders children when no error is thrown', () => {
    render(
      <ErrorBoundary>
        <FaultyComponent shouldThrow={false} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Component rendered safely')).toBeInTheDocument();
  });

  it('catches render errors and displays ErrorMessage with reload button', () => {
    render(
      <ErrorBoundary>
        <FaultyComponent shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong while rendering this page.')).toBeInTheDocument();
    expect(
      screen.getByText('An unexpected client error occurred. Please reload the page to try again.')
    ).toBeInTheDocument();

    const reloadButton = screen.getByRole('button', { name: 'Reload page' });
    expect(reloadButton).toBeInTheDocument();

    // Verify clicking reload calls window.location.reload
    const reloadMock = vi.fn();
    Object.defineProperty(window, 'location', {
      configurable: true,
      value: { ...window.location, reload: reloadMock },
    });

    fireEvent.click(reloadButton);
    expect(reloadMock).toHaveBeenCalled();
  });
});
