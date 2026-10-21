import React from 'react';

export interface InternshipBodySectionsProps {
  description: string;
  requirements: string;
}

export const InternshipBodySections: React.FC<InternshipBodySectionsProps> = ({
  description,
  requirements,
}) => {
  return (
    <>
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-ink">Description</h2>
        <p className="text-ink whitespace-pre-line leading-relaxed">{description}</p>
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-ink">Requirements</h2>
        <p className="text-ink whitespace-pre-line leading-relaxed">{requirements}</p>
      </div>
    </>
  );
};
