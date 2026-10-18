import React, { useEffect, useState } from 'react';
import {
  getOrganizationProfile,
  ProfileApiError,
  updateOrganizationProfile,
} from '../../api/profile';
import { Button, Notice, Textarea, TextField } from '../ui';

export const OrganizationProfileForm: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [serverError, setServerError] = useState<string | null>(null);
  const [savedSuccess, setSavedSuccess] = useState(false);

  const [organizationName, setOrganizationName] = useState('');
  const [industry, setIndustry] = useState('');
  const [location, setLocation] = useState('');
  const [website, setWebsite] = useState('');
  const [description, setDescription] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    let isMounted = true;

    async function loadData() {
      setIsLoading(true);
      setLoadError(null);
      try {
        const profile = await getOrganizationProfile();
        if (isMounted) {
          setOrganizationName(profile.organization_name ?? '');
          setIndustry(profile.industry ?? '');
          setLocation(profile.location ?? '');
          setWebsite(profile.website ?? '');
          setDescription(profile.description ?? '');
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

  const validate = (): boolean => {
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setServerError(null);
    setSavedSuccess(false);

    if (!validate()) {
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
    </div>
  );
};
