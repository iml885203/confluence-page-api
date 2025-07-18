#!/usr/bin/env python3
"""
Vercel testing runner
Runs tests against Vercel dev server or production endpoints
"""
import subprocess
import time
import requests
import sys
import os
import signal
from contextlib import contextmanager


class VercelTestRunner:
    """Test runner for Vercel endpoints"""
    
    def __init__(self, port=3000):
        self.port = port
        self.base_url = f"http://localhost:{port}"
        self.dev_process = None
    
    @contextmanager
    def vercel_dev_server(self):
        """Context manager to start/stop vercel dev server"""
        try:
            # Start vercel dev
            print(f"Starting Vercel dev server on port {self.port}...")
            self.dev_process = subprocess.Popen(
                ['vercel', 'dev', '--listen', str(self.port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            # Wait for server to start
            self._wait_for_server()
            print(f"✅ Vercel dev server running at {self.base_url}")
            
            yield self.base_url
            
        except FileNotFoundError:
            print("❌ Vercel CLI not found. Please install with: npm i -g vercel")
            print("⚠️  Running tests without live server...")
            yield None
            
        except Exception as e:
            print(f"❌ Failed to start Vercel dev server: {e}")
            yield None
            
        finally:
            if self.dev_process:
                print("🛑 Stopping Vercel dev server...")
                os.killpg(os.getpgid(self.dev_process.pid), signal.SIGTERM)
                self.dev_process.wait()
    
    def _wait_for_server(self, timeout=30):
        """Wait for server to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.base_url}/api/image.py", timeout=5)
                if response.status_code in [200, 404]:  # Server is responding
                    return True
            except requests.exceptions.RequestException:
                time.sleep(1)
                continue
        
        raise TimeoutError(f"Server did not start within {timeout} seconds")
    
    def run_endpoint_tests(self, server_url=None):
        """Run endpoint tests"""
        if server_url:
            print(f"🧪 Running tests against {server_url}")
            return self._run_live_tests(server_url)
        else:
            print("🧪 Running mock tests (no live server)")
            return self._run_mock_tests()
    
    def _run_live_tests(self, server_url):
        """Run tests against live server"""
        print("\n📡 Testing live endpoints...")
        
        # Test basic endpoint availability
        endpoints = [
            "/api/image.py",
            "/api/proxy/pages/123456.py",
        ]
        
        success_count = 0
        
        for endpoint in endpoints:
            try:
                url = f"{server_url}{endpoint}"
                response = requests.get(url, timeout=10)
                
                if response.status_code < 500:  # Not a server error
                    print(f"✅ {endpoint} - Status: {response.status_code}")
                    success_count += 1
                else:
                    print(f"❌ {endpoint} - Status: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ {endpoint} - Error: {e}")
        
        print(f"\n📊 Live tests: {success_count}/{len(endpoints)} endpoints responding")
        return success_count == len(endpoints)
    
    def _run_mock_tests(self):
        """Run mock tests without live server"""
        print("\n🎭 Running mock tests...")
        
        # Test that we can import modules from bracketed directory
        try:
            import sys
            pageId_path = os.path.join(os.path.dirname(__file__), '..', 'api', 'pages', '[pageId]')
            
            if os.path.exists(pageId_path):
                sys.path.insert(0, pageId_path)
                
                # Test imports
                modules = ['contributors', 'index', 'version']
                imported_modules = []
                
                for module_name in modules:
                    try:
                        module = __import__(module_name)
                        if hasattr(module, 'handler'):
                            imported_modules.append(module_name)
                            print(f"✅ {module_name}.py - Handler found")
                        else:
                            print(f"❌ {module_name}.py - No handler function")
                    except ImportError as e:
                        print(f"❌ {module_name}.py - Import error: {e}")
                
                print(f"\n📊 Mock tests: {len(imported_modules)}/{len(modules)} modules imported successfully")
                return len(imported_modules) == len(modules)
            else:
                print("❌ pageId directory not found")
                return False
                
        except Exception as e:
            print(f"❌ Mock tests failed: {e}")
            return False


def main():
    """Main test runner"""
    print("🚀 Vercel Function Testing")
    print("=" * 50)
    
    runner = VercelTestRunner()
    
    # Try to run with vercel dev server
    with runner.vercel_dev_server() as server_url:
        success = runner.run_endpoint_tests(server_url)
    
    if success:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())