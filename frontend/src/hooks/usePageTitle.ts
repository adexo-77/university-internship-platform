import { useEffect } from 'react';

const PLATFORM_NAME = 'University Platform';

/**
 * Sets the document tab title to the specified page title with the platform suffix.
 * Example: usePageTitle('Courses') sets document.title to "Courses - University Platform".
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
