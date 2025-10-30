import { useState, useEffect } from 'react'; // 👈 Agrega useEffect aquí
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import styles from '../styles/Admin.module.css';
import genStyles from '../styles/Generar.module.css';

function Decodificar() {
  const navigate = useNavigate();
  const [jwtInput, setJwtInput] = useState('');
  const [decodedData, setDecodedData] = useState({
    usuario: '',
    role: '',
    iat: '',
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  // 👈 NUEVO: Resetea datos y mensaje cada vez que cambie el JWT en el textarea
  useEffect(() => {
    setDecodedData({ usuario: '', role: '', iat: '' });
    setMessage(null);
  }, [jwtInput]); // Se ejecuta cada vez que jwtInput cambie

  // Update the endpoint URL to match your backend
  const BACKEND_URL = 'http://localhost:3001';

  const handleDecode = async () => {
    if (!jwtInput.trim()) {
      setMessage({ success: false, text: 'Por favor ingresa un JWT para decodificar.' });
      return;
    }
    
    setLoading(true);
    setMessage(null);
    
    try {
      const decodeResponse = await fetch(`${BACKEND_URL}/decode`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jwt: jwtInput }),
      });
      
      if (!decodeResponse.ok) {
        const errorData = await decodeResponse.json();
        throw new Error(errorData.error || 'Error al decodificar.');
      }
      
      const decoded = await decodeResponse.json();
      setDecodedData({
        usuario: decoded.usuario || '',
        role: decoded.role || '',
        iat: decoded.iat || '',
      });
      setMessage({ success: true, text: 'JWT verificado y decodificado exitosamente' }); // 👈 Mensaje más claro
    } catch (error) {
      setMessage({ success: false, text: `Error: ${error.message}` });
      setDecodedData({ usuario: '', role: '', iat: '' });
    }
    
    setLoading(false);
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
            <h1 className={styles.gradientTitle}>Decodificar JWT</h1>
            
            
              <h3>Pega tu JWT aquí</h3>
              <div className={genStyles.jwtSection}>
                <textarea
                  value={jwtInput}
                  onChange={(e) => setJwtInput(e.target.value)}
                  placeholder="Pega aquí el JWT que quieres decodificar"
                  className={genStyles.jwtTextarea}
                  rows={4}
                />
                <button 
                  onClick={handleDecode} 
                  disabled={loading || !jwtInput.trim()}
                  className={genStyles.generateBtn}
                >
                  {loading ? 'Verificando...' : 'Verificar JWT'} {/* 👈 Ajuste opcional */}
                </button>
              </div>
           
            {/* Mostrar los datos decodificados siempre que haya una respuesta */}
            <div className={genStyles.generateForm}>
              <h3>Datos Decodificados</h3>
              <div className={genStyles.inputGrid}>
                <div className={`${genStyles.input} ${genStyles.readOnlyInput}`}>
                  <label>Usuario:</label>
                  <input
                    type="text"
                    value={decodedData.usuario}
                    readOnly
                    className={genStyles.input}
                  />
                </div>
                <div className={`${genStyles.input} ${genStyles.readOnlyInput}`}>
                  <label>Role:</label>
                  <input
                    type="text"
                    value={decodedData.role}
                    readOnly
                    className={genStyles.input}
                  />
                </div>
                <div className={`${genStyles.input} ${genStyles.readOnlyInput}`}>
                  <label>IAT:</label>
                  <input
                    type="text"
                    value={decodedData.iat}
                    readOnly
                    className={genStyles.input}
                  />
                </div>
              </div>
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

export default Decodificar;