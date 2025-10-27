import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import styles from '../styles/Admin.module.css';  // Reusa estilos, pero puedes crear Login.module.css si prefieres

function Generar() {
  const navigate = useNavigate();

  const handleGenerate = () => {
    // Placeholder: En un futuro, usa una lib como jsonwebtoken (instala: npm i jsonwebtoken)
    // Ej: const token = jwt.sign({ payload: 'data' }, 'secret');
    alert('JWT generado! (Implementa la lógica real aquí)');
  };

  const handleBack = () => {
    navigate('/', { replace: true });  // Vuelve a home/login
  };

  return (
    <div className={styles.adminLayout}>
      <Navbar />      
      <main className={styles.mainContent}>
        <div className={styles.pagePattern}>
          <div className={styles.inner}>
            <h1 className={styles.gradientTitle}>Decodificar JWT</h1>
            <p>Aquí va el formulario para generar tokens JWT...</p>
            
            {/* Ejemplo de formulario básico */}
            <div style={{ marginBottom: 20 }}>
              <textarea
                placeholder="Payload JSON (ej: { &quot;userId&quot;: 123 })"
                rows={4}
                cols={50}
                style={{ width: '100%', marginBottom: 10 }}
              />
              <button onClick={handleGenerate} style={{ marginRight: 10 }}>
                Generar JWT
              </button>
            </div>
            
            <div style={{ marginTop: 20 }}>
              <button onClick={handleBack} className={styles.logoutBtn}>  {/* Reusa estilo como "volver" */}
                Volver al Inicio
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Generar;