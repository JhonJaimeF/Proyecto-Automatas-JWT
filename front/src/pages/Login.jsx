import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { FaUser, FaLock } from 'react-icons/fa';
import styles from '../styles/Login.module.css'; 

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    if (login(username, password)) {
      const role = username === 'admin' ? '/admin' : '/user';
      navigate(role, { replace: true });
    } else {
      setError('Credenciales inválidas. Prueba: user/123 o admin/123');
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.formCard}>
        <div className={styles.header}>
          <FaUser className={styles.iconLarge} />
          <h2 className={styles.title}>Iniciar Sesión</h2>
        </div>
        <form onSubmit={handleSubmit}>
          <div className={styles.inputGroup}>
            <FaUser className={styles.inputIcon} />
            <input
              type="text"
              placeholder="Usuario (user o admin)"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className={styles.input}
              required
            />
          </div>
          <div className={styles.inputGroup}>
            <FaLock className={styles.inputIcon} />
            <input
              type="password"
              placeholder="Contraseña"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={styles.input}
              required
            />
          </div>
          {error && <p className={styles.error}>{error}</p>}
          <button type="submit" className={styles.submitBtn}>
            Iniciar Sesión
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;