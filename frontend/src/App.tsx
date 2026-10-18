import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { ProtectedRoute } from './components/routes/ProtectedRoute';
import { RoleRoute } from './components/routes/RoleRoute';
import { getHomePath } from './config/navigation';
import { AuthProvider } from './context/AuthContext';
import { useAuth } from './hooks/useAuth';
import { AccountPage } from './pages/AccountPage';
import { ApplicationDetailPage } from './pages/ApplicationDetailPage';
import { AssignmentCreatePage } from './pages/AssignmentCreatePage';
import { AssignmentDetailPage } from './pages/AssignmentDetailPage';
import { AssignmentEditPage } from './pages/AssignmentEditPage';
import { CourseCreatePage } from './pages/CourseCreatePage';
import { CourseDetailPage } from './pages/CourseDetailPage';
import { CourseEditPage } from './pages/CourseEditPage';
import { CoursesPage } from './pages/CoursesPage';
import { InternshipCreatePage } from './pages/InternshipCreatePage';
import { InternshipDetailPage } from './pages/InternshipDetailPage';
import { InternshipEditPage } from './pages/InternshipEditPage';
import { InternshipsPage } from './pages/InternshipsPage';
import { LoginPage } from './pages/LoginPage';
import { MyApplicationsPage } from './pages/MyApplicationsPage';
import { MyCoursesPage } from './pages/MyCoursesPage';
import { MyInternshipsPage } from './pages/MyInternshipsPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { ProfilePage } from './pages/ProfilePage';
import { RegisterPage } from './pages/RegisterPage';
import { SubmissionGradePage } from './pages/SubmissionGradePage';
import { SystemStatusPage } from './pages/SystemStatusPage';

/**
 * Root index redirect: sends unauthenticated users to /login
 * and authenticated users to their role's home page.
 */
const RootRedirect: React.FC = () => {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  return <Navigate to={getHomePath(user.role)} replace />;
};

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Root redirect — no page of its own */}
      <Route path="/" element={<RootRedirect />} />

      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Protected routes */}
      <Route element={<ProtectedRoute />}>
        <Route path="/account" element={<AccountPage />} />

        {/* Profile: student and organization roles only */}
        <Route element={<RoleRoute allowedRoles={['student', 'organization']} />}>
          <Route path="/profile" element={<ProfilePage />} />
        </Route>

        {/* Course catalogue: student and admin */}
        <Route element={<RoleRoute allowedRoles={['student', 'admin']} />}>
          <Route path="/courses" element={<CoursesPage />} />
          <Route path="/internships" element={<InternshipsPage />} />
        </Route>

        {/* My courses: student and instructor */}
        <Route element={<RoleRoute allowedRoles={['student', 'instructor']} />}>
          <Route path="/my-courses" element={<MyCoursesPage />} />
        </Route>

        {/* Student applications */}
        <Route element={<RoleRoute allowedRoles={['student']} />}>
          <Route path="/my-applications" element={<MyApplicationsPage />} />
        </Route>

        {/* Organization internship management */}
        <Route element={<RoleRoute allowedRoles={['organization']} />}>
          <Route path="/my-internships" element={<MyInternshipsPage />} />
          <Route path="/internships/new" element={<InternshipCreatePage />} />
          <Route path="/internships/:id/edit" element={<InternshipEditPage />} />
        </Route>

        {/* Create course: instructor only */}
        <Route element={<RoleRoute allowedRoles={['instructor']} />}>
          <Route path="/courses/new" element={<CourseCreatePage />} />
          <Route path="/courses/:courseId/assignments/new" element={<AssignmentCreatePage />} />
          <Route path="/assignments/:id/edit" element={<AssignmentEditPage />} />
          <Route
            path="/assignments/:assignmentId/submissions/:submissionId/grade"
            element={<SubmissionGradePage />}
          />
        </Route>

        {/* Edit course: instructor and admin */}
        <Route element={<RoleRoute allowedRoles={['instructor', 'admin']} />}>
          <Route path="/courses/:id/edit" element={<CourseEditPage />} />
        </Route>

        {/* Details: any signed-in user (role permissions handled in pages) */}
        <Route path="/courses/:id" element={<CourseDetailPage />} />
        <Route path="/assignments/:id" element={<AssignmentDetailPage />} />
        <Route path="/internships/:id" element={<InternshipDetailPage />} />
        <Route path="/applications/:id" element={<ApplicationDetailPage />} />

        {/* System status: admin role only */}
        <Route element={<RoleRoute allowedRoles={['admin']} />}>
          <Route path="/status" element={<SystemStatusPage />} />
        </Route>
      </Route>

      {/* Not found fallback */}
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
