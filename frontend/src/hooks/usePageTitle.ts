import { useEffect } from 'react';

const PLATFORM_NAME = 'UNIVERSITY';

/**
 * Sets the document tab title to the specified page title with the platform suffix.
 * Example: usePageTitle('Courses') sets document.title to "Courses - UNIVERSITY".
 */
export function usePageTitle(title?: string): void {
  useEffect(() => {
    if (title && title.trim().length > 0) {
      document.title = `${title.trim()} - ${PLATFORM_NAME}`;
    } else {
      document.title = PLATFORM_NAME;
    }
  }, [title]);
}
