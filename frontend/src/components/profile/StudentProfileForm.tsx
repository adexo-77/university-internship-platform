import React, { useEffect, useState } from 'react';
import { getStudentProfile, ProfileApiError, updateStudentProfile } from '../../api/profile';
import { formatSkills, parseSkills } from '../../lib/skills';
import { Button, Notice, Select, Textarea, TextField } from '../ui';

export const StudentProfileForm: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [serverError, setServerError] = useState<string | null>(null);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const [university, setUniversity] = useState('');
  const [department, setDepartment] = useState('');
  const [yearOfStudy, setYearOfStudy] = useState('');
  const [bio, setBio] = useState('');
  const [skillsText, setSkillsText] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    let isMounted = true;

    async function loadData() {
      setIsLoading(true);
      setLoadError(null);
      try {
        const profile = await getStudentProfile();
        if (isMounted) {
          setUniversity(profile.university ?? '');
          setDepartment(profile.department ?? '');
          setYearOfStudy(profile.year_of_study ? String(profile.year_of_study) : '');
          setBio(profile.bio ?? '');
          setSkillsText(formatSkills(profile.skills));
        }
      } catch (err) {
        if (isMounted) {
          setLoadError(err instanceof Error ? err.message : 'Failed to load profile data.');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    }

    void loadData();

    return () => {
      isMounted = false;
    };
  }, []);

  const validate = (skillsList: string[]): boolean => {
    const errors: Record<string, string> = {};

    if (skillsList.length > 20) {
      errors.skills = 'At most 20 skills are permitted.';
    }
    for (const skill of skillsList) {
      if (skill.length > 40) {
        errors.skills = 'Each skill cannot exceed 40 characters.';
        break;
      }
    }
    if (bio.length > 1000) {
      errors.bio = 'Bio cannot exceed 1000 characters.';
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setServerError(null);
    setSavedSuccess(false);

    const parsedSkills = parseSkills(skillsText);
    if (!validate(parsedSkills)) {
      return;
    }

    setIsSaving(true);
    try {
      await updateStudentProfile({
        university: university.trim() || null,
        department: department.trim() || null,
        year_of_study: yearOfStudy ? parseInt(yearOfStudy, 10) : null,
        bio: bio.trim() || null,
        skills: parsedSkills,
      });
      setSavedSuccess(true);
    } catch (err) {
      if (err instanceof ProfileApiError || err instanceof Error) {
        setServerError(err.message);
      } else {
        setServerError('Failed to save profile. Please try again.');
      }
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div
        data-testid="profile-loading-state"
        className="p-6 bg-surface border border-line rounded-control text-pencil text-sm"
      >
        Loading profile...
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {savedSuccess && (
        <div data-testid="profile-success-notice">
          <Notice variant="info">Profile saved</Notice>
        </div>
      )}

      {serverError && (
        <div data-testid="profile-server-error">
          <Notice variant="error" title="Error saving profile">
            {serverError}
          </Notice>
        </div>
      )}

      {loadError && (
        <div data-testid="profile-load-error">
          <Notice variant="error" title="Error loading profile">
            {loadError}
          </Notice>
        </div>
      )}

      <form
        onSubmit={handleSubmit}
        noValidate
        className="space-y-4 bg-surface border border-line rounded-control p-6 shadow-sm"
      >
        <TextField
          id="student-university"
          label="University"
          type="text"
          value={university}
          onChange={(e) => setUniversity(e.target.value)}
          helperText="Your enrolled university or institution name."
        />

        <TextField
          id="student-department"
          label="Department"
          type="text"
          value={department}
          onChange={(e) => setDepartment(e.target.value)}
          helperText="Academic department or faculty."
        />

        <Select
          id="student-year-of-study"
          label="Year of study"
          value={yearOfStudy}
          onChange={(e) => setYearOfStudy(e.target.value)}
          options={[
            { value: '', label: '-- Select year of study --' },
            { value: '1', label: 'Year 1' },
            { value: '2', label: 'Year 2' },
            { value: '3', label: 'Year 3' },
            { value: '4', label: 'Year 4' },
            { value: '5', label: 'Year 5' },
            { value: '6', label: 'Year 6' },
          ]}
        />

        <Textarea
          id="student-bio"
          label="Bio"
          value={bio}
          onChange={(e) => setBio(e.target.value)}
          error={fieldErrors.bio}
          helperText="Brief summary of your academic interests and career goals (up to 1000 characters)."
          rows={4}
        />

        <TextField
          id="student-skills"
          label="Skills"
          type="text"
          value={skillsText}
          onChange={(e) => setSkillsText(e.target.value)}
          error={fieldErrors.skills}
          helperText="Enter skills separated by commas (e.g. Python, SQL, React). Up to 20 skills."
        />

        <div className="pt-2">
          <Button id="profile-save-button" type="submit" variant="primary" disabled={isSaving}>
            {isSaving ? 'Saving...' : 'Save changes'}
          </Button>
        </div>
      </form>
    </div>
  );
};
