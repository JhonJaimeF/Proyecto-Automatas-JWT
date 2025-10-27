import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { FaUserCheck, FaSignOutAlt } from 'react-icons/fa';
import styles from '../styles/User.module.css';  // ← Import desde styles/

function User() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  return (
    <div className={styles.container}>
      <div className={styles.dashboardCard}>
        <div className={styles.header}>
          <FaUserCheck className={styles.iconLarge} />
          <h2 className={styles.title}>Dashboard de Usuario</h2>
        </div>
        <p className={styles.welcomeText}>¡Bienvenido! Aquí puedes ver tu contenido personalizado como usuario normal.</p>
        
        <div className={styles.optionsList}>
          <h3 className={styles.optionsTitle}>
            <FaUserCheck className="mr-2" /> Tus Opciones:
          </h3>
          <ul>
            <li className={styles.optionItem}>
              <FaUserCheck className={styles.optionIcon} /> Ver perfil
            </li>
            <li className={styles.optionItem}>
              <FaUserCheck className={styles.optionIcon} /> Actualizar datos
            </li>
            <li className={styles.optionItem}>
              <FaUserCheck className={styles.optionIcon} /> Configuraciones básicas
            </li>
          </ul>
        </div>
        
        <button onClick={handleLogout} className={styles.logoutBtn}>
          <FaSignOutAlt className="mr-2" /> Cerrar Sesión
        </button>
      </div>
    </div>
  );
}

export default User;