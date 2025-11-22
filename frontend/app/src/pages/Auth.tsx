import { useAuth } from '../hooks/useAuth';
import AuthForm from '../components/auth/auth-form';
import { Navigate } from 'react-router-dom';

export default function User() {
  const [user, isLoading] = useAuth();

  if (isLoading) {
    return <div> Hold on tight...</div>;
  }
  if (!user) {
    return <AuthForm />;
  }
  return <Navigate to="/URLLink" />;
}
