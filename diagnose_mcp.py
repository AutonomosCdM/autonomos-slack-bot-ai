#!/usr/bin/env python3
"""
Script de diagnóstico rápido para MCP - para usar en producción
"""

import os
import subprocess
import sys
import logging
from pathlib import Path

# Configurar logging simple
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    print("🔧 DIAGNÓSTICO RÁPIDO MCP")
    print("=" * 40)
    
    # 1. Check current directory
    cwd = os.getcwd()
    print(f"📁 Working directory: {cwd}")
    
    # 2. Check Python
    print(f"🐍 Python: {sys.version}")
    
    # 3. Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, check=True)
        print(f"✅ Node.js: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Node.js error: {e}")
        return False
    
    # 4. Check MCP directory
    mcp_path = Path(cwd) / "dona-mcp-toolbox"
    print(f"📂 MCP path: {mcp_path}")
    print(f"📂 MCP exists: {mcp_path.exists()}")
    
    if not mcp_path.exists():
        print("❌ MCP directory missing!")
        return False
    
    # 5. Check package.json
    package_json = mcp_path / "package.json"
    if package_json.exists():
        print("✅ package.json found")
    else:
        print("❌ package.json missing!")
        return False
    
    # 6. Check node_modules
    node_modules = mcp_path / "node_modules"
    if node_modules.exists():
        print("✅ node_modules found")
    else:
        print("❌ node_modules missing!")
        return False
    
    # 7. Test Node.js execution
    try:
        test_script = 'console.log("Node.js test OK");'
        result = subprocess.run(
            ['node', '-e', test_script],
            cwd=str(mcp_path),
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ Node.js execution test passed")
        else:
            print(f"❌ Node.js execution failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Node.js execution error: {e}")
        return False
    
    # 8. Test MCP import
    try:
        from mcp_integration import mcp_integration
        print("✅ MCP integration import successful")
    except Exception as e:
        print(f"❌ MCP integration import failed: {e}")
        return False
    
    # 9. Test MCP initialization
    try:
        result = mcp_integration.initialize()
        if result:
            print("✅ MCP initialization successful")
        else:
            print("❌ MCP initialization failed")
            return False
    except Exception as e:
        print(f"❌ MCP initialization error: {e}")
        return False
    
    print("\n🎉 MCP DIAGNOSIS PASSED!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)