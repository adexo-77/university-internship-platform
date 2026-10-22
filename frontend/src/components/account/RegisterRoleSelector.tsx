import React from 'react';
import { cn } from '../../lib/cn';
import { PublicRegisterRole } from '../../types/auth';

export interface RegisterRoleSelectorProps {
  role: PublicRegisterRole;
  onChange: (role: PublicRegisterRole) => void;
}

export const RegisterRoleSelector: React.FC<RegisterRoleSelectorProps> = ({ role, onChange }) => {
  return (
    <fieldset className="space-y-1.5">
      <legend className="block text-xs font-medium text-ink">Account role</legend>
      <div className="grid grid-cols-2 gap-3 pt-1">
        <label
          htmlFor="register-role-student"
          className={cn(
            'flex items-center gap-3 p-3 rounded-control border cursor-pointer transition-colors duration-150',
            role === 'student'
              ? 'border-petrol bg-surface ring-1 ring-petrol'
              : 'border-line bg-surface hover:bg-chalk'
          )}
        >
          <input
            type="radio"
            id="register-role-student"
            name="role"
            value="student"
            checked={role === 'student'}
            onChange={() => onChange('student')}
            className="h-4 w-4 text-petrol focus:ring-petrol border-line accent-petrol"
          />
          <span className="text-sm font-medium text-ink">Student</span>
        </label>

        <label
          htmlFor="register-role-organization"
          className={cn(
            'flex items-center gap-3 p-3 rounded-control border cursor-pointer transition-colors duration-150',
            role === 'organization'
              ? 'border-petrol bg-surface ring-1 ring-petrol'
              : 'border-line bg-surface hover:bg-chalk'
          )}
        >
          <input
            type="radio"
            id="register-role-organization"
            name="role"
            value="organization"
            checked={role === 'organization'}
            onChange={() => onChange('organization')}
            className="h-4 w-4 text-petrol focus:ring-petrol border-line accent-petrol"
          />
          <span className="text-sm font-medium text-ink">Organization</span>
        </label>
      </div>
    </fieldset>
  );
};
