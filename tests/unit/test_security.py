#!/usr/bin/env python3
"""
Script para testar as medidas de segurança do WebGIS
"""

import requests
import json
import sys
from urllib.parse import urljoin

class SecurityTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    def log_test(self, test_name, passed, details=""):
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if details:
            print(f"   Detalhes: {details}")
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'details': details
        })
    
    def test_authentication_required(self):
        """Testar se autenticação é obrigatória"""
        try:
            response = self.session.get(urljoin(self.base_url, "/"))
            passed = response.status_code == 302 or "login" in response.url.lower()
            self.log_test("Autenticação obrigatória", passed)
        except Exception as e:
            self.log_test("Autenticação obrigatória", False, str(e))
    
    def test_login_injection(self):
        """Testar injeção de SQL no login"""
        payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "admin'--",
            "<script>alert('xss')</script>"
        ]
        
        for payload in payloads:
            try:
                data = {
                    'username': payload,
                    'password': 'test'
                }
                response = self.session.post(urljoin(self.base_url, "/login"), data=data)
                # Se retornou erro de validação, é bom
                passed = response.status_code in [400, 401] or "incorretos" in response.text.lower()
                self.log_test(f"Login injection: {payload[:20]}...", passed)
            except Exception as e:
                self.log_test(f"Login injection: {payload[:20]}...", False, str(e))
    
    def test_xss_protection(self):
        """Testar proteção contra XSS"""
        try:
            # Tentar acessar com payload XSS
            xss_payload = "<script>alert('xss')</script>"
            response = self.session.get(urljoin(self.base_url, f"/?q={xss_payload}"))
            
            # Verificar se o payload foi escapado ou removido
            content = response.text.lower()
            passed = "alert('xss')" not in content or "<script>" not in content
            self.log_test("Proteção XSS", passed)
        except Exception as e:
            self.log_test("Proteção XSS", False, str(e))
    
    def test_security_headers(self):
        """Testar headers de segurança"""
        try:
            response = self.session.get(urljoin(self.base_url, "/login"))
            headers = response.headers
            
            security_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block'
            }
            
            all_passed = True
            for header, expected_value in security_headers.items():
                if header in headers:
                    actual_value = headers[header]
                    passed = expected_value.lower() in actual_value.lower()
                    self.log_test(f"Header {header}", passed, f"Esperado: {expected_value}, Obtido: {actual_value}")
                    if not passed:
                        all_passed = False
                else:
                    self.log_test(f"Header {header}", False, "Header não encontrado")
                    all_passed = False
            
            self.log_test("Headers de segurança", all_passed)
        except Exception as e:
            self.log_test("Headers de segurança", False, str(e))
    
    def test_file_upload_security(self):
        """Testar segurança de upload de arquivos"""
        # Primeiro fazer login
        try:
            login_data = {
                'username': 'admin_super',
                'password': 'isis/2020'
            }
            response = self.session.post(urljoin(self.base_url, "/login"), data=login_data)
            if response.status_code != 200:
                self.log_test("Upload security", False, "Não foi possível fazer login")
                return
        except Exception as e:
            self.log_test("Upload security", False, f"Erro no login: {str(e)}")
            return
        
        # Testar upload de arquivo malicioso
        malicious_files = [
            ('test.php', '<?php echo "malicious"; ?>'),
            ('test.html', '<script>alert("xss")</script>'),
            ('test.exe', 'fake executable content'),
            ('../../../etc/passwd', 'malicious content')
        ]
        
        for filename, content in malicious_files:
            try:
                files = {'file': (filename, content, 'text/plain')}
                response = self.session.post(urljoin(self.base_url, "/api/upload/kml"), files=files)
                
                # Deve rejeitar arquivos não-KML
                passed = response.status_code in [400, 403] or "permitido" in response.text.lower()
                self.log_test(f"Upload malicioso: {filename}", passed)
            except Exception as e:
                self.log_test(f"Upload malicioso: {filename}", False, str(e))
    
    def test_path_traversal(self):
        """Testar proteção contra path traversal"""
        traversal_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        for path in traversal_paths:
            try:
                response = self.session.get(urljoin(self.base_url, f"/api/files/{path}"))
                # Deve retornar 404 ou 403
                passed = response.status_code in [404, 403]
                self.log_test(f"Path traversal: {path[:20]}...", passed)
            except Exception as e:
                self.log_test(f"Path traversal: {path[:20]}...", False, str(e))
    
    def test_csrf_protection(self):
        """Testar proteção CSRF"""
        try:
            # Tentar fazer requisição POST sem token CSRF
            data = {'username': 'test', 'password': 'test'}
            response = self.session.post(urljoin(self.base_url, "/login"), data=data)
            
            # Se retornou erro de CSRF, é bom
            passed = response.status_code in [400, 403] or "csrf" in response.text.lower()
            self.log_test("Proteção CSRF", passed)
        except Exception as e:
            self.log_test("Proteção CSRF", False, str(e))
    
    def run_all_tests(self):
        """Executar todos os testes"""
        print("🔒 Iniciando testes de segurança do WebGIS...")
        print("=" * 50)
        
        self.test_authentication_required()
        self.test_login_injection()
        self.test_xss_protection()
        self.test_security_headers()
        self.test_file_upload_security()
        self.test_path_traversal()
        self.test_csrf_protection()
        
        print("=" * 50)
        self.print_summary()
    
    def print_summary(self):
        """Imprimir resumo dos testes"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 Resumo dos Testes:")
        print(f"Total: {total_tests}")
        print(f"✅ Passaram: {passed_tests}")
        print(f"❌ Falharam: {failed_tests}")
        print(f"Taxa de sucesso: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n⚠️ Testes que falharam:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test']}: {result['details']}")
        else:
            print(f"\n🎉 Todos os testes passaram! O sistema está seguro.")

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    tester = SecurityTester(base_url)
    tester.run_all_tests() 