import React, { useEffect, useState } from 'react';
import {
  getOrganizationProfile,
  getStudentProfile,
  ProfileApiError,
  updateOrganizationProfile,
  updateStudentProfile,
} from '../api/profile';
import { AppShell } from '../components/layout/AppShell';
import { Button, Notice, PageHeader, Select, Textarea, TextField } from '../components/ui';
import { useAuth } from '../hooks/useAuth';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [serverError, setServerError] = useState<string | null>(null);
  const [savedSuccess, setSavedSuccess] = useState(false);

  // Student form state
  const [university, setUniversity] = useState('');
  const [department, setDepartment] = useState('');
  const [yearOfStudy, setYearOfStudy] = useState('');
  const [bio, setBio] = useState('');
  const [skillsText, setSkillsText] = useState('');

  // Organization form state
  const [organizationName, setOrganizationName] = useState('');
  const [industry, setIndustry] = useState('');
  const [location, setLocation] = useState('');
  const [website, setWebsite] = useState('');
  const [description, setDescription] = useState('');

  // Client validation errors
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    let isMounted = true;

    async function loadData() {
      setIsLoading(true);
      setLoadError(null);
      try {
        if (user?.role === 'student') {
          const profile = await getStudentProfile();
          if (isMounted) {
            setUniversity(profile.university ?? '');
            setDepartment(profile.department ?? '');
            setYearOfStudy(profile.year_of_study ? String(profile.year_of_study) : '');
            setBio(profile.bio ?? '');
            setSkillsText(profile.skills.join(', '));
          }
        } else if (user?.role === 'organization') {
          const profile = await getOrganizationProfile();
          if (isMounted) {
            setOrganizationName(profile.organization_name ?? '');
            setIndustry(profile.industry ?? '');
            setLocation(profile.location ?? '');
            setWebsite(profile.website ?? '');
            setDescription(profile.description ?? '');
          }
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

    if (user?.role === 'student' || user?.role === 'organization') {
      void loadData();
    } else {
      setIsLoading(false);
    }

    return () => {
      isMounted = false;
    };
  }, [user?.role]);

  if (!user) {
    return null;
  }

  const validateStudent = (skillsList: string[]): boolean => {
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

  const validateOrganization = (): boolean => {
    const errors: Record<string, string> = {};

    if (!organizationName.trim()) {
      errors.organizationName = 'Organization name cannot be blank.';
    }

    const trimmedWebsite = website.trim();
    if (trimmedWebsite) {
      try {
        const parsed = new URL(trimmedWebsite);
        if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
          errors.website = 'Website must be a valid http or https URL.';
        }
      } catch {
        errors.website = 'Website must be a valid http or https URL.';
      }
    }

    if (description.length > 1000) {
      errors.description = 'Description cannot exceed 1000 characters.';
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleStudentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setServerError(null);
    setSavedSuccess(false);

    const parsedSkills = skillsText
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);

    if (!validateStudent(parsedSkills)) {
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

  const handleOrganizationSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setServerError(null);
    setSavedSuccess(false);

    if (!validateOrganization()) {
      return;
    }

    setIsSaving(true);
    try {
      await updateOrganizationProfile({
        organization_name: organizationName.trim(),
        industry: industry.trim() || null,
        location: location.trim() || null,
        website: website.trim() || null,
        description: description.trim() || null,
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

  return (
    <AppShell>
      <div className="space-y-6 max-w-2xl">
        <PageHeader
          title="Profile"
          description={
            user.role === 'student'
              ? 'Manage your academic details, skills, and background for internship applications.'
              : 'Manage your organization profile, sector, and company description.'
          }
        />

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

        {isLoading ? (
          <div
            data-testid="profile-loading-state"
            className="p-6 bg-surface border border-line rounded-control text-pencil text-sm"
          >
            Loading profile...
          </div>
        ) : user.role === 'student' ? (
          <form
            onSubmit={handleStudentSubmit}
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
        ) : user.role === 'organization' ? (
          <form
            onSubmit={handleOrganizationSubmit}
            noValidate
            className="space-y-4 bg-surface border border-line rounded-control p-6 shadow-sm"
          >
            <TextField
              id="org-name"
              label="Organization name"
              type="text"
              value={organizationName}
              onChange={(e) => setOrganizationName(e.target.value)}
              error={fieldErrors.organizationName}
              required
            />

            <TextField
              id="org-industry"
              label="Industry"
              type="text"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              helperText="Industry or business sector."
            />

            <TextField
              id="org-location"
              label="Location"
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              helperText="City, country, or primary office address."
            />

            <TextField
              id="org-website"
              label="Website"
              type="url"
              value={website}
              onChange={(e) => setWebsite(e.target.value)}
              error={fieldErrors.website}
              helperText="Official company URL starting with http:// or https://"
            />

            <Textarea
              id="org-description"
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              error={fieldErrors.description}
              helperText="Company overview, mission, and internship culture (up to 1000 characters)."
              rows={4}
            />

            <div className="pt-2">
              <Button id="profile-save-button" type="submit" variant="primary" disabled={isSaving}>
                {isSaving ? 'Saving...' : 'Save changes'}
              </Button>
            </div>
          </form>
        ) : null}
      </div>
    </AppShell>
  );
};
