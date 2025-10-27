"""
Suite de pruebas completa para el proyecto JWT
Aplica conceptos de autómatas finitos en la validación
"""

import unittest
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automatas.afd_base import AFD, crear_afd_jwt_estructura, crear_afd_base64url
from automatas.afn_base import AFN
from automatas.minimizador import MinimizadorAFD
from automatas.clausula import ConstructorThompson
from analisis_semantico.validador_semantico import ValidadorSemanticoJWT
from decodificacion.decodificador_jwt import DecodificadorBase64URL, ParserJWT
from codificacion.generador_jwt import GeneradorJWT


class TestAutomatas(unittest.TestCase):
    """
    Tests para autómatas finitos
    """
    
    def test_afd_estructura_jwt_valida(self):
        """AFD acepta estructura JWT válida"""
        afd = crear_afd_jwt_estructura()
        aceptado, _ = afd.procesar("header.payload.signature")
        self.assertTrue(aceptado)
    
    def test_afd_estructura_jwt_invalida(self):
        """AFD rechaza estructura JWT inválida"""
        afd = crear_afd_jwt_estructura()
        
        # Solo 2 partes
        aceptado, _ = afd.procesar("header.payload")
        self.assertFalse(aceptado)
        
        # 4 partes
        aceptado, _ = afd.procesar("a.b.c.d")
        self.assertFalse(aceptado)
    
    def test_afd_base64url(self):
        """AFD valida caracteres Base64URL"""
        afd = crear_afd_base64url()
        
        # Válido
        aceptado, _ = afd.procesar("abc123-_")
        self.assertTrue(aceptado)
        
        # Inválido (+ no es Base64URL)
        aceptado, _ = afd.procesar("abc+def")
        self.assertFalse(aceptado)
    
    def test_minimizacion_afd(self):
        """Minimización produce AFD equivalente"""
        from automatas.minimizador import crear_afd_no_minimo
        
        afd = crear_afd_no_minimo()
        minimizador = MinimizadorAFD(afd)
        afd_minimo = minimizador.minimizar()
        
        # Verificar que aceptan el mismo lenguaje
        casos = ["ab", "aab", "bab", "a", "b"]
        for caso in casos:
            res_orig, _ = afd.procesar(caso)
            res_min, _ = afd_minimo.procesar(caso)
            self.assertEqual(res_orig, res_min, f"Diferencia en: {caso}")
    
    def test_construccion_thompson(self):
        """Construcción de Thompson convierte ER a AFN"""
        constructor = ConstructorThompson()
        
        # Símbolo simple
        afn = constructor.simbolo('a')
        aceptado, _ = afn.procesar('a')
        self.assertTrue(aceptado)
        
        # Concatenación
        afn_ab = constructor.desde_expresion_simple('ab')
        aceptado, _ = afn_ab.procesar('ab')
        self.assertTrue(aceptado)


class TestValidacionSemantica(unittest.TestCase):
    """
    Tests para análisis semántico (Fase 3)
    """
    
    def setUp(self):
        self.validador = ValidadorSemanticoJWT()
        self.tiempo_actual = int(datetime.now().timestamp())
    
    def test_header_valido(self):
        """Header con algoritmo válido"""
        header = {"alg": "HS256", "typ": "JWT"}
        resultado = self.validador.validar_header(header)
        self.assertTrue(resultado)
    
    def test_header_sin_algoritmo(self):
        """Header sin campo 'alg' es inválido"""
        header = {"typ": "JWT"}
        resultado = self.validador.validar_header(header)
        self.assertFalse(resultado)
        self.assertGreater(len(self.validador.errores), 0)
    
    def test_payload_tipos_correctos(self):
        """Payload con tipos de datos correctos"""
        payload = {
            "iss": "auth.example.com",
            "sub": "user123",
            "exp": self.tiempo_actual + 3600,
            "iat": self.tiempo_actual
        }
        resultado = self.validador.validar_payload(payload, self.tiempo_actual)
        self.assertTrue(resultado)
    
    def test_payload_tipos_incorrectos(self):
        """Payload con tipos incorrectos es rechazado"""
        payload = {
            "iss": 12345,  # Debe ser string
            "exp": "invalid"  # Debe ser int
        }
        resultado = self.validador.validar_payload(payload, self.tiempo_actual)
        self.assertFalse(resultado)
    
    def test_token_expirado(self):
        """Token expirado es detectado"""
        payload = {
            "exp": self.tiempo_actual - 1000
        }
        self.validador.validar_payload(payload, self.tiempo_actual)
        self.assertGreater(len(self.validador.errores), 0)
    
    def test_coherencia_temporal(self):
        """Detecta incoherencias temporales"""
        payload = {
            "iat": self.tiempo_actual,
            "exp": self.tiempo_actual - 100  # exp < iat (inválido)
        }
        self.validador.validar_tabla_simbolos(payload)
        self.assertGreater(len(self.validador.errores), 0)


class TestDecodificacion(unittest.TestCase):
    """
    Tests para decodificación (Fase 4)
    """
    
    def setUp(self):
        self.decodificador = DecodificadorBase64URL()
        self.parser = ParserJWT()
    
    def test_codificar_decodificar(self):
        """Codificar y decodificar produce el original"""
        original = "Hello, World!"
        codificado = self.decodificador.codificar(original)
        decodificado = self.decodificador.decodificar(codificado)
        self.assertEqual(original, decodificado.decode('utf-8'))
    
    def test_base64url_sin_padding(self):
        """Base64URL no incluye padding '='"""
        codificado = self.decodificador.codificar("test")
        self.assertNotIn('=', codificado)
    
    def test_parser_jwt_valido(self):
        """Parser extrae componentes de JWT válido"""
        # JWT de ejemplo
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        componentes = self.parser.parsear(jwt)
        
        self.assertIn('header', componentes)
        self.assertIn('payload', componentes)
        self.assertIn('signature', componentes)
        self.assertEqual(componentes['header']['alg'], 'HS256')
        self.assertEqual(componentes['payload']['sub'], '1234567890')


class TestCodificacion(unittest.TestCase):
    """
    Tests para codificación y firma (Fase 5)
    """
    
    def setUp(self):
        self.generador = GeneradorJWT(algoritmo='HS256')
        self.clave = "clave_secreta_test"
    
    def test_generar_token(self):
        """Generar token produce JWT válido"""
        payload = {
            "sub": "user123",
            "iat": int(datetime.now().timestamp())
        }
        
        token = self.generador.generar_token(payload, self.clave)
        
        # Verificar estructura
        partes = token.split('.')
        self.assertEqual(len(partes), 3)
    
    def test_verificar_firma_valida(self):
        """Firma válida es verificada correctamente"""
        payload = {"sub": "test"}
        token = self.generador.generar_token(payload, self.clave)
        
        es_valida = self.generador.verificar_firma(token, self.clave)
        self.assertTrue(es_valida)
    
    def test_verificar_firma_invalida(self):
        """Firma inválida es rechazada"""
        payload = {"sub": "test"}
        token = self.generador.generar_token(payload, self.clave)
        
        clave_incorrecta = "otra_clave"
        es_valida = self.generador.verificar_firma(token, clave_incorrecta)
        self.assertFalse(es_valida)
    
    def test_diferentes_algoritmos(self):
        """Soporta múltiples algoritmos HMAC"""
        payload = {"sub": "test", "iat": int(datetime.now().timestamp())}
        
        for alg in ['HS256', 'HS384', 'HS512']:
            gen = GeneradorJWT(algoritmo=alg)
            token = gen.generar_token(payload, self.clave)
            
            # Verificar que se generó
            self.assertIsNotNone(token)
            
            # Verificar que es válido
            es_valida = gen.verificar_firma(token, self.clave)
            self.assertTrue(es_valida, f"Fallo con {alg}")


class TestIntegracion(unittest.TestCase):
    """
    Tests de integración completa
    """
    
    def test_flujo_completo(self):
        """Genera, codifica, decodifica y valida JWT"""
        # Generar
        generador = GeneradorJWT()
        payload = generador.crear_payload(
            issuer="test.com",
            subject="user1",
            expiracion_minutos=60
        )
        clave = "secret"
        token = generador.generar_token(payload, clave)
        
        # Decodificar
        parser = ParserJWT()
        componentes = parser.parsear(token)
        
        # Validar semántica
        validador = ValidadorSemanticoJWT()
        validador.validar_header(componentes['header'])
        validador.validar_payload(componentes['payload'])
        
        # Verificar firma
        firma_valida = generador.verificar_firma(token, clave)
        
        self.assertTrue(firma_valida)
        self.assertEqual(len(validador.errores), 0)


def suite_completa():
    """
    Suite completa de tests
    """
    suite = unittest.TestSuite()
    
    # Agregar todos los tests
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAutomatas))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestValidacionSemantica))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDecodificacion))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestCodificacion))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestIntegracion))
    
    return suite


if __name__ == '__main__':
    print("="*80)
    print(" "*20 + "SUITE DE PRUEBAS - Proyecto JWT")
    print(" "*15 + "Aplicando Teoría de Lenguajes Formales")
    print("="*80)
    print()
    
    runner = unittest.TextTestRunner(verbosity=2)
    resultado = runner.run(suite_completa())
    
    print("\n" + "="*80)
    print("RESUMEN DE PRUEBAS")
    print("="*80)
    print(f"Tests ejecutados: {resultado.testsRun}")
    print(f"Éxitos: {resultado.testsRun - len(resultado.failures) - len(resultado.errors)}")
    print(f"Fallos: {len(resultado.failures)}")
    print(f"Errores: {len(resultado.errors)}")
    print("="*80)
