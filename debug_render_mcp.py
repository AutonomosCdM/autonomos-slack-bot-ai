#!/usr/bin/env python3
"""
Script de debug específico para Render - permite ejecutar via Slack
"""

import os
import subprocess
import sys
import json
import logging
from pathlib import Path

def debug_environment():
    """Debug completo del environment de Render"""
    
    debug_info = {
        "environment": {},
        "filesystem": {},
        "nodejs": {},
        "mcp": {},
        "errors": []
    }
    
    try:
        # 1. Environment básico
        debug_info["environment"] = {
            "cwd": os.getcwd(),
            "python_version": sys.version,
            "platform": sys.platform,
            "path_env": os.environ.get("PATH", "").split(":"),
            "home": os.environ.get("HOME", "N/A"),
            "user": os.environ.get("USER", "N/A")
        }
        
        # 2. Filesystem
        cwd = Path(os.getcwd())
        debug_info["filesystem"] = {
            "current_dir_contents": list(os.listdir(cwd)),
            "mcp_toolbox_exists": (cwd / "dona-mcp-toolbox").exists(),
            "mcp_toolbox_contents": [],
            "permissions": {}
        }
        
        mcp_path = cwd / "dona-mcp-toolbox"
        if mcp_path.exists():
            debug_info["filesystem"]["mcp_toolbox_contents"] = list(os.listdir(mcp_path))
            debug_info["filesystem"]["permissions"] = {
                "mcp_readable": os.access(mcp_path, os.R_OK),
                "mcp_executable": os.access(mcp_path, os.X_OK),
                "package_json_exists": (mcp_path / "package.json").exists(),
                "node_modules_exists": (mcp_path / "node_modules").exists()
            }
        
        # 3. Node.js detection
        node_paths_to_try = [
            "node",
            "/usr/bin/node",
            "/usr/local/bin/node", 
            "/opt/render/project/bin/node",
            "/app/bin/node",
            "/usr/local/nodejs/bin/node",
            "/opt/nodejs/bin/node"
        ]
        
        debug_info["nodejs"] = {
            "available_paths": [],
            "working_path": None,
            "version": None,
            "npm_available": False,
            "npm_version": None
        }
        
        for node_path in node_paths_to_try:
            try:
                result = subprocess.run([node_path, "--version"], 
                                     capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    debug_info["nodejs"]["available_paths"].append({
                        "path": node_path,
                        "version": result.stdout.strip()
                    })
                    if not debug_info["nodejs"]["working_path"]:
                        debug_info["nodejs"]["working_path"] = node_path
                        debug_info["nodejs"]["version"] = result.stdout.strip()
            except Exception as e:
                debug_info["errors"].append(f"Node.js test failed for {node_path}: {e}")
        
        # Test npm
        if debug_info["nodejs"]["working_path"]:
            try:
                npm_result = subprocess.run(["npm", "--version"], 
                                         capture_output=True, text=True, timeout=5)
                if npm_result.returncode == 0:
                    debug_info["nodejs"]["npm_available"] = True
                    debug_info["nodejs"]["npm_version"] = npm_result.stdout.strip()
            except Exception as e:
                debug_info["errors"].append(f"npm test failed: {e}")
        
        # 4. MCP Test
        debug_info["mcp"] = {
            "initialization": False,
            "test_script_result": None,
            "import_success": False,
            "error_details": None
        }
        
        # Test MCP import
        try:
            sys.path.append(str(cwd))
            from mcp_integration import mcp_integration
            debug_info["mcp"]["import_success"] = True
            
            # Test initialization
            init_result = mcp_integration.initialize()
            debug_info["mcp"]["initialization"] = init_result
            
        except Exception as e:
            debug_info["mcp"]["error_details"] = str(e)
            debug_info["errors"].append(f"MCP import/init failed: {e}")
        
        # Test direct Node.js execution
        if debug_info["nodejs"]["working_path"] and mcp_path.exists():
            try:
                test_script = """
                console.log(JSON.stringify({
                    node_version: process.version,
                    platform: process.platform,
                    arch: process.arch,
                    cwd: process.cwd(),
                    execPath: process.execPath,
                    uptime: process.uptime()
                }));
                """
                
                result = subprocess.run(
                    [debug_info["nodejs"]["working_path"], "-e", test_script],
                    cwd=str(mcp_path),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    debug_info["mcp"]["test_script_result"] = json.loads(result.stdout.strip())
                else:
                    debug_info["errors"].append(f"Node.js test script failed: {result.stderr}")
                    
            except Exception as e:
                debug_info["errors"].append(f"Direct Node.js test failed: {e}")
    
    except Exception as e:
        debug_info["errors"].append(f"Overall debug failed: {e}")
    
    return debug_info

def format_debug_output(debug_info, mode="slack"):
    """Format debug info for Slack or console"""
    
    if mode == "console":
        output = "🔍 **RENDER DEBUG REPORT**\n\n"
    else:
        output = "🔍 **PRODUCTION DEBUG**\n\n"
    
    # Environment
    env = debug_info["environment"]
    output += f"**Environment:**\n"
    output += f"• CWD: `{env.get('cwd', 'N/A')}`\n"
    output += f"• Python: `{env.get('python_version', 'N/A')[:50]}...`\n"
    output += f"• Platform: `{env.get('platform', 'N/A')}`\n"
    output += f"• User: `{env.get('user', 'N/A')}`\n\n"
    
    # Filesystem
    fs = debug_info["filesystem"]
    output += f"**Filesystem:**\n"
    output += f"• MCP Toolbox Exists: {'✅' if fs.get('mcp_toolbox_exists') else '❌'}\n"
    
    if fs.get('mcp_toolbox_exists'):
        perms = fs.get('permissions', {})
        output += f"• Readable: {'✅' if perms.get('mcp_readable') else '❌'}\n"
        output += f"• Executable: {'✅' if perms.get('mcp_executable') else '❌'}\n"
        output += f"• package.json: {'✅' if perms.get('package_json_exists') else '❌'}\n"
        output += f"• node_modules: {'✅' if perms.get('node_modules_exists') else '❌'}\n"
    
    # Node.js
    nodejs = debug_info["nodejs"]
    output += f"\n**Node.js:**\n"
    output += f"• Working Path: `{nodejs.get('working_path', 'NONE FOUND')}`\n"
    output += f"• Version: `{nodejs.get('version', 'N/A')}`\n"
    output += f"• npm Available: {'✅' if nodejs.get('npm_available') else '❌'}\n"
    
    if nodejs.get("available_paths"):
        output += f"• Available Paths: {len(nodejs['available_paths'])}\n"
    
    # MCP
    mcp = debug_info["mcp"]
    output += f"\n**MCP Status:**\n"
    output += f"• Import Success: {'✅' if mcp.get('import_success') else '❌'}\n"
    output += f"• Initialization: {'✅' if mcp.get('initialization') else '❌'}\n"
    
    if mcp.get('test_script_result'):
        test = mcp['test_script_result']
        output += f"• Node.js Test: ✅ `{test.get('node_version', 'N/A')}`\n"
    
    # Errors
    if debug_info.get("errors"):
        output += f"\n**Errors ({len(debug_info['errors'])}):**\n"
        # For slack, show fewer errors and shorter text
        max_errors = 2 if mode == "slack" else 5
        max_length = 80 if mode == "slack" else 150
        
        for i, error in enumerate(debug_info["errors"][:max_errors], 1):
            output += f"{i}. `{error[:max_length]}...`\n"
            
        if len(debug_info['errors']) > max_errors:
            remaining = len(debug_info['errors']) - max_errors
            output += f"... y {remaining} errores más\n"
    
    return output

if __name__ == "__main__":
    debug_info = debug_environment()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print(json.dumps(debug_info, indent=2))
    else:
        print(format_debug_output(debug_info, mode="console"))