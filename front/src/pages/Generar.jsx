import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import styles from '../styles/Admin.module.css';
import genStyles from '../styles/Generar.module.css';

function Generar() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    usuario: '',
    contrasena: '',
    role: '',
    iat: '',
  });
  const [jwtInput, setJwtInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const BACKEND_URL = 'http://localhost:3001';

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleGenerate = async () => {
    if (!formData.usuario || !formData.contrasena || !formData.role || formData.iat === '') {
      setMessage({ success: false, text: 'Completa todos los campos para generar.' });
      return;
    }
    setLoading(true);
    setMessage(null);
    try {
      const generateResponse = await fetch(`${BACKEND_URL}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (!generateResponse.ok) {
        const errorData = await generateResponse.json();
        throw new Error(errorData.error || 'Error en generación.');
      }
      const generateData = await generateResponse.json();
      setJwtInput(generateData.jwt);
      setMessage({ success: true, text: 'JWT generado exitosamente' });
    } catch (error) {
      setMessage({ success: false, text: `Error: ${error.message}. Verifica que el backend esté corriendo.` });
    }
    setLoading(false);
  };

  const handleCopyJWT = async () => {
    try {
      await navigator.clipboard.writeText(jwtInput);
      setMessage({ success: true, text: 'JWT copiado al portapapeles' });
    } catch (err) {
      setMessage({ success: false, text: 'Error al copiar el JWT' });
    }
  };

  const handleBack = () => {
    navigate('/', { replace: true });
  };

  return (
    <div className={styles.adminLayout}>
      <Navbar />
      <main className={styles.mainContent}>
        <div className={styles.pagePattern}>
          <div className={styles.inner}>
            <h1 className={styles.gradientTitle}>Generador JWT</h1>
            
            <div className={genStyles.generateForm}>
              <h3>Datos para Generar JWT</h3>
              <div className={genStyles.inputGrid}>
                <input
                  name="usuario"
                  value={formData.usuario}
                  onChange={handleInputChange}
                  placeholder="Usuario"
                  className={genStyles.input}
                />
                <input
                  name="contrasena"
                  type="password"
                  value={formData.contrasena}
                  onChange={handleInputChange}
                  placeholder="Contraseña"
                  className={genStyles.input}
                />
                <input
                  name="role"
                  value={formData.role}
                  onChange={handleInputChange}
                  placeholder="Role (user/admin)"
                  className={genStyles.input}
                />
                <input
                  name="iat"
                  type="number"
                  value={formData.iat}
                  onChange={handleInputChange}
                  placeholder="Tiempo de validez (iat)"
                  className={genStyles.input}
                />
              </div>
              <button 
                onClick={handleGenerate} 
                disabled={loading}
                className={genStyles.generateBtn}
              >
                {loading ? 'Generando...' : 'Generar JWT'}
              </button>
            </div>

            <div className={genStyles.jwtSection}>
              <label className={genStyles.jwtLabel}>JWT Generado:</label>
              <textarea
                value={jwtInput}
                readOnly
                placeholder="El JWT aparecerá aquí"
                className={genStyles.jwtTextarea}
                rows={4}
              />
              <button 
                onClick={handleCopyJWT} 
                disabled={!jwtInput.trim()}
                className={genStyles.copyBtn}
              >
                Copiar JWT
              </button>
            </div>
            
            {message && (
              <div className={`${genStyles.messageContainer} ${message.success ? genStyles.success : genStyles.error}`}>
                <p>{message.text}</p>
              </div>
            )}
            
            <div className={styles.buttonContainer}>
              <button onClick={handleBack} className={styles.logoutBtn}>
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