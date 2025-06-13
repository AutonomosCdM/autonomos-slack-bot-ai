#!/usr/bin/env python3
"""
MCP Health Monitor - Inspirado en patrones de JSPyBridge y Azure MCP Bridge
Proporciona monitoreo continuo y auto-recuperación para el sistema MCP
"""

import os
import time
import json
import logging
import subprocess
import threading
from typing import Dict, Optional, Callable
from pathlib import Path

logger = logging.getLogger(__name__)

class MCPHealthMonitor:
    """Monitor de salud con auto-recuperación para sistema MCP"""
    
    def __init__(self, mcp_integration):
        self.mcp_integration = mcp_integration
        self.health_status = {
            "healthy": False,
            "last_check": None,
            "consecutive_failures": 0,
            "total_checks": 0,
            "uptime_start": time.time(),
            "environment_verified": False,
            "node_path": None,
            "toolbox_verified": False
        }
        self.health_callbacks = []
        self.monitoring = False
        self.monitor_thread = None
        
    def add_health_callback(self, callback: Callable[[Dict], None]):
        """Agregar callback para notificaciones de cambio de estado"""
        self.health_callbacks.append(callback)
    
    def notify_health_change(self, old_status: bool, new_status: bool):
        """Notificar cambios de estado de salud"""
        for callback in self.health_callbacks:
            try:
                callback({
                    "old_healthy": old_status,
                    "new_healthy": new_status,
                    "status": self.health_status.copy()
                })
            except Exception as e:
                logger.error(f"Error in health callback: {e}")
    
    def verify_environment(self) -> Dict:
        """Verificación completa del environment (inspirado en JSPyBridge)"""
        verification = {
            "node_available": False,
            "node_version": None,
            "node_path": None,
            "mcp_directory": False,
            "package_json": False,
            "node_modules": False,
            "permissions_ok": False,
            "test_execution": False,
            "errors": []
        }
        
        try:
            # 1. Verificar Node.js (múltiples rutas como JSPyBridge)
            node_paths = [
                "node",
                "/usr/bin/node",
                "/usr/local/bin/node",
                "/opt/render/project/bin/node",
                "/app/bin/node",
                "/usr/local/nodejs/bin/node"
            ]
            
            for node_path in node_paths:
                try:
                    result = subprocess.run(
                        [node_path, "--version"],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        verification["node_available"] = True
                        verification["node_version"] = result.stdout.strip()
                        verification["node_path"] = node_path
                        break
                except Exception as e:
                    verification["errors"].append(f"Node test {node_path}: {e}")
            
            if not verification["node_available"]:
                return verification
            
            # 2. Verificar estructura MCP (similar a Azure MCP Bridge pattern)
            mcp_path = Path(self.mcp_integration.mcp_path)
            verification["mcp_directory"] = mcp_path.exists()
            
            if verification["mcp_directory"]:
                verification["package_json"] = (mcp_path / "package.json").exists()
                verification["node_modules"] = (mcp_path / "node_modules").exists()
                verification["permissions_ok"] = (
                    os.access(mcp_path, os.R_OK) and 
                    os.access(mcp_path, os.X_OK)
                )
            
            # 3. Test ejecución básica
            if verification["node_available"] and verification["mcp_directory"]:
                try:
                    test_script = 'console.log(JSON.stringify({test: "ok", version: process.version}));'
                    result = subprocess.run(
                        [verification["node_path"], "-e", test_script],
                        cwd=str(mcp_path),
                        capture_output=True, text=True, timeout=10
                    )
                    
                    if result.returncode == 0:
                        verification["test_execution"] = True
                    else:
                        verification["errors"].append(f"Test execution failed: {result.stderr}")
                        
                except Exception as e:
                    verification["errors"].append(f"Test execution error: {e}")
            
        except Exception as e:
            verification["errors"].append(f"Environment verification error: {e}")
        
        return verification
    
    def perform_health_check(self) -> bool:
        """Realizar check de salud completo"""
        old_healthy = self.health_status["healthy"]
        
        try:
            self.health_status["total_checks"] += 1
            self.health_status["last_check"] = time.time()
            
            # 1. Verificar environment si no se ha hecho
            if not self.health_status["environment_verified"]:
                env_check = self.verify_environment()
                self.health_status["environment_verified"] = (
                    env_check["node_available"] and 
                    env_check["mcp_directory"] and 
                    env_check["test_execution"]
                )
                self.health_status["node_path"] = env_check.get("node_path")
                
                if not self.health_status["environment_verified"]:
                    logger.warning(f"Environment verification failed: {env_check['errors']}")
                    self.health_status["consecutive_failures"] += 1
                    self.health_status["healthy"] = False
                    return False
            
            # 2. Test inicialización MCP
            if self.health_status["environment_verified"]:
                try:
                    init_success = self.mcp_integration.initialize()
                    
                    if init_success:
                        self.health_status["healthy"] = True
                        self.health_status["consecutive_failures"] = 0
                        logger.info("✅ MCP health check passed")
                        return True
                    else:
                        raise Exception("MCP initialization returned False")
                        
                except Exception as e:
                    logger.warning(f"MCP initialization failed: {e}")
                    self.health_status["consecutive_failures"] += 1
                    self.health_status["healthy"] = False
                    return False
                    
        except Exception as e:
            logger.error(f"Health check error: {e}")
            self.health_status["consecutive_failures"] += 1
            self.health_status["healthy"] = False
            return False
        
        finally:
            # Notificar cambios de estado
            if old_healthy != self.health_status["healthy"]:
                self.notify_health_change(old_healthy, self.health_status["healthy"])
    
    def start_monitoring(self, interval: int = 300):  # 5 minutos
        """Iniciar monitoreo continuo (patrón de auto-recuperación)"""
        if self.monitoring:
            return
        
        self.monitoring = True
        
        def monitor_loop():
            logger.info(f"🔍 Starting MCP health monitoring (interval: {interval}s)")
            
            while self.monitoring:
                try:
                    self.perform_health_check()
                    
                    # Auto-recuperación si falla mucho
                    if self.health_status["consecutive_failures"] >= 3:
                        logger.warning("🔧 Attempting MCP auto-recovery...")
                        self.attempt_recovery()
                    
                    time.sleep(interval)
                    
                except Exception as e:
                    logger.error(f"Monitor loop error: {e}")
                    time.sleep(60)  # Wait 1 minute on error
        
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Detener monitoreo"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
    
    def attempt_recovery(self):
        """Intentar recuperar el sistema MCP"""
        logger.info("🛠️ Attempting MCP system recovery...")
        
        try:
            # 1. Reset estado
            self.mcp_integration.initialized = False
            self.health_status["environment_verified"] = False
            
            # 2. Re-verificar environment
            env_check = self.verify_environment()
            
            if env_check["node_available"] and env_check["mcp_directory"]:
                # 3. Intentar re-inicialización
                if self.mcp_integration.initialize():
                    logger.info("✅ MCP recovery successful")
                    self.health_status["consecutive_failures"] = 0
                    return True
                else:
                    logger.warning("❌ MCP recovery failed - initialization failed")
            else:
                logger.warning("❌ MCP recovery failed - environment not ready")
                
        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
        
        return False
    
    def get_health_report(self) -> Dict:
        """Obtener reporte completo de salud"""
        uptime = time.time() - self.health_status["uptime_start"]
        
        return {
            "healthy": self.health_status["healthy"],
            "uptime_seconds": int(uptime),
            "uptime_formatted": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m",
            "total_checks": self.health_status["total_checks"],
            "consecutive_failures": self.health_status["consecutive_failures"],
            "last_check": self.health_status["last_check"],
            "environment_verified": self.health_status["environment_verified"],
            "node_path": self.health_status["node_path"],
            "monitoring_active": self.monitoring
        }

# Instancia global para usar en el bot
health_monitor = None

def initialize_health_monitor(mcp_integration):
    """Inicializar monitor de salud global"""
    global health_monitor
    health_monitor = MCPHealthMonitor(mcp_integration)
    
    # Callback para logs de cambio de estado
    def health_change_logger(event):
        if event["new_healthy"] and not event["old_healthy"]:
            logger.info("🎉 MCP system recovered and is now healthy")
        elif not event["new_healthy"] and event["old_healthy"]:
            logger.warning("⚠️ MCP system became unhealthy")
    
    health_monitor.add_health_callback(health_change_logger)
    return health_monitor