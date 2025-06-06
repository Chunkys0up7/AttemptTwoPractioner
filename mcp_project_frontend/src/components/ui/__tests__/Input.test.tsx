import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Input } from '../Input';

describe('Input', () => {
  it('renders with default props', () => {
    render(<Input placeholder="Enter text" />);
    const input = screen.getByPlaceholderText('Enter text');
    expect(input).toBeInTheDocument();
    expect(input).toHaveClass('border-input');
  });

  it('renders with label', () => {
    render(<Input label="Username" />);
    expect(screen.getByLabelText('Username')).toBeInTheDocument();
  });

  it('renders with helper text', () => {
    render(<Input helperText="This is a helper text" />);
    expect(screen.getByText('This is a helper text')).toBeInTheDocument();
  });

  it('renders with error state', () => {
    render(<Input error="This field is required" />);
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(screen.getByText('This field is required')).toBeInTheDocument();
    expect(screen.getByText('This field is required')).toHaveClass('text-destructive');
  });

  it('renders with different variants', () => {
    const { rerender } = render(<Input variant="default" />);
    expect(screen.getByRole('textbox')).toHaveClass('border-input');

    rerender(<Input variant="success" />);
    expect(screen.getByRole('textbox')).toHaveClass('border-success');
  });

  it('renders with different sizes', () => {
    const { rerender } = render(<Input inputSize="sm" />);
    expect(screen.getByRole('textbox')).toHaveClass('h-9');

    rerender(<Input inputSize="default" />);
    expect(screen.getByRole('textbox')).toHaveClass('h-10');

    rerender(<Input inputSize="lg" />);
    expect(screen.getByRole('textbox')).toHaveClass('h-11');
  });

  it('renders with left and right elements', () => {
    const leftElement = <span data-testid="left">←</span>;
    const rightElement = <span data-testid="right">→</span>;

    render(
      <Input
        leftElement={leftElement}
        rightElement={rightElement}
      />
    );

    expect(screen.getByTestId('left')).toBeInTheDocument();
    expect(screen.getByTestId('right')).toBeInTheDocument();
    expect(screen.getByRole('textbox')).toHaveClass('pl-10 pr-10');
  });

  it('handles disabled state', () => {
    render(<Input disabled />);
    const input = screen.getByRole('textbox');
    expect(input).toBeDisabled();
    expect(input).toHaveClass('disabled:opacity-50');
  });

  it('handles value changes', () => {
    const handleChange = jest.fn();
    render(<Input onChange={handleChange} />);
    
    fireEvent.change(screen.getByRole('textbox'), {
      target: { value: 'test' },
    });
    
    expect(handleChange).toHaveBeenCalledTimes(1);
  });

  it('applies custom className', () => {
    render(<Input className="custom-class" />);
    expect(screen.getByRole('textbox')).toHaveClass('custom-class');
  });

  it('applies container className', () => {
    render(<Input containerClassName="container-class" />);
    expect(screen.getByRole('textbox').parentElement?.parentElement).toHaveClass('container-class');
  });
}); 