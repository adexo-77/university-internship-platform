import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { ProtectedRoute } from './components/routes/ProtectedRoute';
import { RoleRoute } from './components/routes/RoleRoute';
import { getHomePath } from './config/navigation';
import { AuthProvider } from './context/AuthContext';
import { useAuth } from './hooks/useAuth';
import { AccountPage } from './pages/AccountPage';
import { CourseCreatePage } from './pages/CourseCreatePage';
import { CourseDetailPage } from './pages/CourseDetailPage';
import { CourseEditPage } from './pages/CourseEditPage';
import { CoursesPage } from './pages/CoursesPage';
import { LoginPage } from './pages/LoginPage';
import { MyCoursesPage } from './pages/MyCoursesPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { ProfilePage } from './pages/ProfilePage';
import { RegisterPage } from './pages/RegisterPage';
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
        </Route>

        {/* My courses: student and instructor */}
        <Route element={<RoleRoute allowedRoles={['student', 'instructor']} />}>
          <Route path="/my-courses" element={<MyCoursesPage />} />
        </Route>

        {/* Create course: instructor only */}
        <Route element={<RoleRoute allowedRoles={['instructor']} />}>
          <Route path="/courses/new" element={<CourseCreatePage />} />
        </Route>

        {/* Edit course: instructor and admin */}
        <Route element={<RoleRoute allowedRoles={['instructor', 'admin']} />}>
          <Route path="/courses/:id/edit" element={<CourseEditPage />} />
        </Route>

        {/* Course details: any signed-in user */}
        <Route path="/courses/:id" element={<CourseDetailPage />} />

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
