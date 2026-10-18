import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Button } from './Button';

describe('Button Component', () => {
  it('renders primary variant with expected design token classes', () => {
    render(<Button variant="primary">Primary Action</Button>);
    const button = screen.getByRole('button', { name: 'Primary Action' });
    expect(button).toHaveClass('bg-petrol');
    expect(button).toHaveClass('text-surface');
    expect(button).toHaveClass('border-petrol');
    expect(button).toHaveClass('hover:bg-petrol-hover');
  });

  it('renders secondary variant with expected design token classes', () => {
    render(<Button variant="secondary">Secondary Action</Button>);
    const button = screen.getByRole('button', { name: 'Secondary Action' });
    expect(button).toHaveClass('bg-surface');
    expect(button).toHaveClass('text-ink');
    expect(button).toHaveClass('border-line');
    expect(button).toHaveClass('hover:bg-chalk');
  });

  it('renders quiet variant with expected design token classes', () => {
    render(<Button variant="quiet">Quiet Action</Button>);
    const button = screen.getByRole('button', { name: 'Quiet Action' });
    expect(button).toHaveClass('bg-transparent');
    expect(button).toHaveClass('text-pencil');
    expect(button).toHaveClass('border-transparent');
    expect(button).toHaveClass('hover:text-ink');
  });

  it('renders danger variant with expected design token classes', () => {
    render(<Button variant="danger">Danger Action</Button>);
    const button = screen.getByRole('button', { name: 'Danger Action' });
    expect(button).toHaveClass('bg-surface');
    expect(button).toHaveClass('text-brick');
    expect(button).toHaveClass('border-brick');
    expect(button).toHaveClass('hover:bg-chalk');
  });

  it('renders disabled state with legible pencil text on line-tinted chalk background without opacity reduction', () => {
    render(
      <Button variant="primary" disabled>
        Disabled Action
      </Button>
    );
    const button = screen.getByRole('button', { name: 'Disabled Action' });
    expect(button).toBeDisabled();
    expect(button).toHaveClass('disabled:cursor-not-allowed');
    expect(button).toHaveClass('disabled:bg-chalk');
    expect(button).toHaveClass('disabled:text-pencil');
    expect(button).toHaveClass('disabled:border-line');
    expect(button).not.toHaveClass('disabled:opacity-50');
  });

  it('applies small size tokens when size is sm', () => {
    render(<Button size="sm">Small</Button>);
    const button = screen.getByRole('button', { name: 'Small' });
    expect(button).toHaveClass('px-3');
    expect(button).toHaveClass('py-1.5');
    expect(button).toHaveClass('text-xs');
  });

  it('applies medium size tokens by default', () => {
    render(<Button>Medium</Button>);
    const button = screen.getByRole('button', { name: 'Medium' });
    expect(button).toHaveClass('px-4');
    expect(button).toHaveClass('py-2');
  });
});
