import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import styles from '../styles/Admin.module.css';
import Navbar from '../components/Navbar';

function Admin() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const cards = [
  { title: 'Generar', desc: 'Genera tokens JWT personalizados con payload y firma.', path: '/generar' },
  { title: 'Verificar', desc: 'Valida la firma y la integridad de un JWT dado.', path: '/verificar' },
  { title: 'Decodificar', desc: 'Decodifica header y payload para inspeccionar datos.', path: '/decodificar' },
  { title: 'Análisis léxico', desc: 'Realiza el análisis léxico sobre la estructura del token.', path: '/analisis-lexico' },
  { title: 'Análisis sintáctico', desc: 'Evalúa el significado y consistencia de los claims.', path: '/analisis-sintactico' },
  { title: 'Análisis semántico', desc: 'Herramienta adicional de análisis semántico.', path: '/analisis-semantico' },
];

  return (
    <div className={styles.adminLayout}>
      <Navbar />
      <main className={styles.mainContent}>
        <div className={styles.pagePattern}>
          <div className={styles.inner}>
            <h1 className={styles.gradientTitle}>JWT Tools</h1>
            <h5 className={styles.header}>Sistema diseñado para comprobar JWT a partir de automatas y expresiones regulares</h5>
            <div className={styles.cardGrid}>
              {cards.map((c) => (
                <div key={c.title + c.path} className={styles.card}>
                  <div>
                    <h3 className={styles.cardTitle}>{c.title}</h3>
                    <p className={styles.cardDesc}>{c.desc}</p>
                  </div>
                  <div>
                    <button
                      onClick={() => navigate(c.path)}
                      className={styles.cardBtn}
                    >
                      Ir a {c.title}
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div style={{ marginTop: 20 }}>
              <button onClick={handleLogout} className={styles.logoutBtn}>
                Cerrar Sesión
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Admin;