#!/usr/bin/env python3
"""
Script de diagnóstico para MCP en producción
"""

import os
import subprocess
import json
import logging
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_environment():
    """Probar el entorno de producción"""
    print("🔍 DIAGNÓSTICO MCP PRODUCCIÓN")
    print("=" * 50)
    
    # 1. Verificar Python
    print(f"🐍 Python version: {subprocess.check_output(['python', '--version'], text=True).strip()}")
    
    # 2. Verificar Node.js
    try:
        node_version = subprocess.check_output(['node', '--version'], text=True).strip()
        print(f"📦 Node.js version: {node_version}")
    except FileNotFoundError:
        print("❌ Node.js NOT FOUND")
        return False
    
    # 3. Verificar npm
    try:
        npm_version = subprocess.check_output(['npm', '--version'], text=True).strip()
        print(f"📦 npm version: {npm_version}")
    except FileNotFoundError:
        print("❌ npm NOT FOUND")
        return False
    
    # 4. Verificar directorio MCP
    mcp_path = os.path.join(os.getcwd(), "dona-mcp-toolbox")
    print(f"📁 MCP path: {mcp_path}")
    print(f"📁 MCP exists: {os.path.exists(mcp_path)}")
    
    if os.path.exists(mcp_path):
        # Listar contenido
        contents = os.listdir(mcp_path)
        print(f"📁 MCP contents: {contents}")
        
        # Verificar package.json
        package_json = os.path.join(mcp_path, "package.json")
        if os.path.exists(package_json):
            print("✅ package.json found")
        else:
            print("❌ package.json NOT FOUND")
            return False
        
        # Verificar node_modules
        node_modules = os.path.join(mcp_path, "node_modules")
        if os.path.exists(node_modules):
            print("✅ node_modules found")
        else:
            print("❌ node_modules NOT FOUND - running npm install...")
            try:
                subprocess.run(['npm', 'install'], cwd=mcp_path, check=True)
                print("✅ npm install completed")
            except subprocess.CalledProcessError as e:
                print(f"❌ npm install failed: {e}")
                return False
    else:
        print("❌ MCP directory not found")
        return False
    
    # 5. Probar MCP directamente
    print("\n🧪 TESTING MCP DIRECTLY")
    print("-" * 30)
    
    try:
        script = """
        const DonaMCP = require('./src/DonaMCP');
        (async () => {
            try {
                console.log('Creating DonaMCP instance...');
                const dona = new DonaMCP();
                console.log('Initializing...');
                await dona.initialize();
                console.log('Getting status...');
                const status = dona.getSystemStatus();
                console.log('Disposing...');
                await dona.dispose();
                console.log(JSON.stringify({success: true, status}));
            } catch (error) {
                console.error('MCP Error:', error.message);
                console.log(JSON.stringify({success: false, error: error.message, stack: error.stack}));
            }
        })();
        """
        
        result = subprocess.run(
            ['node', '-e', script],
            cwd=mcp_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        if result.returncode == 0:
            try:
                # Buscar la línea con JSON
                lines = result.stdout.strip().split('\n')
                json_line = None
                for line in lines:
                    if line.strip().startswith('{'):
                        json_line = line.strip()
                        break
                
                if json_line:
                    parsed = json.loads(json_line)
                    if parsed.get("success"):
                        print("✅ MCP test successful!")
                        return True
                    else:
                        print(f"❌ MCP test failed: {parsed.get('error')}")
                        return False
                else:
                    print("❌ No JSON output found")
                    return False
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                return False
        else:
            print("❌ MCP test failed with non-zero exit code")
            return False
    
    except Exception as e:
        print(f"❌ Error testing MCP: {e}")
        return False

def test_mcp_integration():
    """Probar mcp_integration.py"""
    print("\n🔗 TESTING MCP INTEGRATION")
    print("-" * 30)
    
    try:
        from mcp_integration import mcp_integration
        
        print("Initializing MCP integration...")
        result = mcp_integration.initialize()
        print(f"Initialize result: {result}")
        
        if result:
            print("Testing ArXiv search...")
            papers = mcp_integration.search_papers('machine learning', max_results=2)
            print(f"Papers result: {papers}")
            
            if papers.get('success'):
                print("✅ MCP integration working!")
                return True
            else:
                print(f"❌ ArXiv search failed: {papers.get('error')}")
                return False
        else:
            print("❌ MCP integration initialization failed")
            return False
    
    except Exception as e:
        print(f"❌ Error testing MCP integration: {e}")
        return False

if __name__ == "__main__":
    env_ok = test_environment()
    integration_ok = test_mcp_integration() if env_ok else False
    
    print(f"\n📊 RESULTS")
    print(f"Environment: {'✅' if env_ok else '❌'}")
    print(f"Integration: {'✅' if integration_ok else '❌'}")
    
    if env_ok and integration_ok:
        print("\n🎉 MCP is ready for production!")
    else:
        print("\n🚨 MCP has issues in production environment")