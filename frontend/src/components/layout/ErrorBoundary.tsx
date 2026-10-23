import { Component, ErrorInfo, ReactNode } from 'react';
import { Button, ErrorMessage } from '../ui';

export interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('ErrorBoundary caught rendering error:', error, errorInfo);
  }

  handleReload = (): void => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div className="min-h-[50vh] flex items-center justify-center p-6">
          <div className="max-w-md w-full">
            <ErrorMessage
              whatHappened="Something went wrong while rendering this page."
              howToFix="An unexpected client error occurred. Please reload the page to try again."
              action={
                <Button variant="secondary" onClick={this.handleReload}>
                  Reload page
                </Button>
              }
            />
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
