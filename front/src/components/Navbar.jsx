import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaKey, FaCheck, FaCode, FaSearch, FaSitemap, FaBrain, FaSignOutAlt } from 'react-icons/fa';
import styles from '../styles/Navbar.module.css';
import { useAuth } from '../context/AuthContext';

function Navbar() {
  const [isExpanded, setIsExpanded] = useState(false);
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const navItems = [
    { icon: <FaKey />, title: 'Generar', path: '/generar' },
    { icon: <FaCheck />, title: 'Verificar', path: '/verificar' },
    { icon: <FaCode />, title: 'Decodificar', path: '/decodificar' },
    { icon: <FaSearch />, title: 'Análisis Léxico', path: '/analisis-lexico' },
    { icon: <FaSitemap />, title: 'Análisis Sintáctico', path: '/analisis-sintactico' },
    { icon: <FaBrain />, title: 'Análisis Semántico', path: '/analisis-semantico' },
  ];

  return (
    <nav 
      className={`${styles.navbar} ${isExpanded ? styles.expanded : ''}`}
      onMouseEnter={() => setIsExpanded(true)}
      onMouseLeave={() => setIsExpanded(false)}
    >
      <button
        type="button"
        className={styles.logo}
        onClick={() => navigate('/admin')}
        aria-label="Ir al panel admin"
      >
        <h2>JWT</h2>
      </button>

      <ul className={styles.navList}>
        {navItems.map((item) => (
          <li key={item.path}>
            <button 
              className={styles.navItem} 
              onClick={() => navigate(item.path)}
            >
              <span className={styles.icon}>{item.icon}</span>
              <span className={styles.title}>{isExpanded ? item.title : ''}</span>
            </button>
          </li>
        ))}
      </ul>

      <button 
        className={styles.logoutButton}
        onClick={handleLogout}
      >
        <span className={styles.icon}><FaSignOutAlt /></span>
        <span className={styles.title}>{isExpanded ? 'Cerrar Sesión' : ''}</span>
      </button>
    </nav>
  );
}

export default Navbar;