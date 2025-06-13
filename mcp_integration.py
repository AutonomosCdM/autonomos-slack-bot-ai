#!/usr/bin/env python3
"""
Integración MCP para Dona Bot
Proporciona acceso a capacidades MCP desde Python
"""

import os
import sys
import json
import logging
import subprocess
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class MCPIntegration:
    """Integración con Dona MCP Toolbox desde Python"""
    
    def __init__(self):
        self.mcp_path = os.path.join(os.path.dirname(__file__), "dona-mcp-toolbox")
        self.node_executable = self._find_node_executable()
        self.initialized = False
    
    def _find_node_executable(self) -> str:
        """Find Node.js executable in different environments"""
        # Common Node.js paths
        node_paths = [
            "node",                    # Standard PATH
            "/usr/bin/node",           # Ubuntu/Debian
            "/usr/local/bin/node",     # MacOS/Homebrew
            "/opt/render/project/bin/node",  # Render.com
            "/app/bin/node",           # Heroku-style
        ]
        
        for node_path in node_paths:
            try:
                result = subprocess.run([node_path, "--version"], 
                                     capture_output=True, check=True, text=True)
                logger.info(f"✅ Found Node.js at: {node_path} (version: {result.stdout.strip()})")
                return node_path
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        logger.warning("⚠️ Using default 'node' executable (may fail in production)")
        return "node"
        
    def _run_mcp_command(self, script: str, timeout: int = 30) -> Dict:
        """Ejecutar comando MCP vía Node.js"""
        try:
            # Cambiar al directorio MCP
            original_cwd = os.getcwd()
            os.chdir(self.mcp_path)
            
            # Ejecutar script Node.js
            result = subprocess.run(
                [self.node_executable, "-e", script],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.mcp_path
            )
            
            # Restaurar directorio
            os.chdir(original_cwd)
            
            if result.returncode != 0:
                logger.error(f"MCP command failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
            
            # Parsear salida JSON
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"success": True, "output": result.stdout.strip()}
                
        except subprocess.TimeoutExpired:
            logger.error("MCP command timed out")
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            logger.error(f"Error executing MCP command: {e}")
            return {"success": False, "error": str(e)}
    
    def initialize(self) -> bool:
        """Inicializar la integración MCP"""
        try:
            logger.info("🚀 Inicializando integración MCP...")
            
            # Verificar que existe el directorio MCP
            if not os.path.exists(self.mcp_path):
                logger.error(f"❌ MCP directory not found: {self.mcp_path}")
                return False
            
            logger.info(f"✅ MCP directory found: {self.mcp_path}")
            
            # Verificar Node.js
            try:
                result = subprocess.run([self.node_executable, "--version"], 
                                     capture_output=True, check=True, text=True)
                logger.info(f"✅ Node.js version: {result.stdout.strip()}")
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                logger.error(f"❌ Node.js not found or not working: {e}")
                return False
            
            # Test básico de MCP
            script = """
            const DonaMCP = require('./src/DonaMCP');
            (async () => {
                try {
                    const dona = new DonaMCP();
                    await dona.initialize();
                    const status = dona.getSystemStatus();
                    await dona.dispose();
                    console.log(JSON.stringify({success: true, status}));
                } catch (error) {
                    console.log(JSON.stringify({success: false, error: error.message}));
                }
            })();
            """
            
            logger.info("🧪 Testing MCP initialization...")
            result = self._run_mcp_command(script)
            logger.info(f"🔍 MCP test result: {result}")
            
            if result.get("success"):
                self.initialized = True
                logger.info("✅ MCP integration initialized successfully")
                return True
            else:
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"❌ MCP initialization failed: {error_msg}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing MCP: {e}")
            return False
    
    def search_papers(self, query: str, max_results: int = 5, category: str = None) -> Dict:
        """Buscar papers en ArXiv"""
        if not self.initialized:
            return {"success": False, "error": "MCP not initialized"}
        
        try:
            logger.info(f"🔍 Searching papers: {query}")
            
            category_param = f", '{category}'" if category else ""
            
            script = f"""
            const DonaMCP = require('./src/DonaMCP');
            (async () => {{
                try {{
                    const dona = new DonaMCP();
                    await dona.initialize();
                    const papers = await dona.searchResearchPapers('{query}', {max_results}{category_param});
                    await dona.dispose();
                    console.log(JSON.stringify({{success: true, papers}}));
                }} catch (error) {{
                    console.log(JSON.stringify({{success: false, error: error.message}}));
                }}
            }})();
            """
            
            result = self._run_mcp_command(script, timeout=60)
            
            if result.get("success"):
                papers = result.get("papers", [])
                logger.info(f"✅ Found {len(papers)} papers")
                return {"success": True, "papers": papers, "count": len(papers)}
            else:
                logger.error(f"Paper search failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"Error searching papers: {e}")
            return {"success": False, "error": str(e)}
    
    def get_paper_details(self, arxiv_id: str) -> Dict:
        """Obtener detalles de un paper específico"""
        if not self.initialized:
            return {"success": False, "error": "MCP not initialized"}
        
        try:
            logger.info(f"📄 Getting paper details: {arxiv_id}")
            
            script = f"""
            const DonaMCP = require('./src/DonaMCP');
            (async () => {{
                try {{
                    const dona = new DonaMCP();
                    await dona.initialize();
                    const details = await dona.executeCapability('arxiv', 'getPaperDetails', '{arxiv_id}');
                    await dona.dispose();
                    console.log(JSON.stringify({{success: true, details}}));
                }} catch (error) {{
                    console.log(JSON.stringify({{success: false, error: error.message}}));
                }}
            }})();
            """
            
            result = self._run_mcp_command(script, timeout=45)
            
            if result.get("success"):
                logger.info(f"✅ Retrieved paper details for {arxiv_id}")
                return result
            else:
                logger.error(f"Paper details failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"Error getting paper details: {e}")
            return {"success": False, "error": str(e)}
    
    def get_arxiv_categories(self) -> Dict:
        """Obtener categorías disponibles de ArXiv"""
        if not self.initialized:
            return {"success": False, "error": "MCP not initialized"}
        
        try:
            script = """
            const DonaMCP = require('./src/DonaMCP');
            (async () => {
                try {
                    const dona = new DonaMCP();
                    await dona.initialize();
                    const categories = dona.getArxivMCP().getCategories();
                    await dona.dispose();
                    console.log(JSON.stringify({success: true, categories}));
                } catch (error) {
                    console.log(JSON.stringify({success: false, error: error.message}));
                }
            })();
            """
            
            result = self._run_mcp_command(script)
            
            if result.get("success"):
                logger.info("✅ Retrieved ArXiv categories")
                return result
            else:
                logger.error(f"Categories retrieval failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return {"success": False, "error": str(e)}
    
    def get_recent_papers(self, category: str, max_results: int = 5) -> Dict:
        """Obtener papers recientes en una categoría"""
        if not self.initialized:
            return {"success": False, "error": "MCP not initialized"}
        
        try:
            logger.info(f"📅 Getting recent papers in {category}")
            
            script = f"""
            const DonaMCP = require('./src/DonaMCP');
            (async () => {{
                try {{
                    const dona = new DonaMCP();
                    await dona.initialize();
                    const papers = await dona.executeCapability('arxiv', 'getRecentPapers', '{category}', {max_results});
                    await dona.dispose();
                    console.log(JSON.stringify({{success: true, papers}}));
                }} catch (error) {{
                    console.log(JSON.stringify({{success: false, error: error.message}}));
                }}
            }})();
            """
            
            result = self._run_mcp_command(script, timeout=60)
            
            if result.get("success"):
                papers = result.get("papers", [])
                logger.info(f"✅ Found {len(papers)} recent papers")
                return {"success": True, "papers": papers, "count": len(papers)}
            else:
                logger.error(f"Recent papers failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"Error getting recent papers: {e}")
            return {"success": False, "error": str(e)}
    
    def get_system_status(self) -> Dict:
        """Obtener estado del sistema MCP"""
        if not self.initialized:
            return {"success": False, "error": "MCP not initialized"}
        
        try:
            script = """
            const DonaMCP = require('./src/DonaMCP');
            (async () => {
                try {
                    const dona = new DonaMCP();
                    await dona.initialize();
                    const status = dona.getSystemStatus();
                    const health = await dona.healthCheck();
                    await dona.dispose();
                    console.log(JSON.stringify({success: true, status, health}));
                } catch (error) {
                    console.log(JSON.stringify({success: false, error: error.message}));
                }
            })();
            """
            
            result = self._run_mcp_command(script)
            
            if result.get("success"):
                logger.info("✅ Retrieved MCP system status")
                return result
            else:
                logger.error(f"Status retrieval failed: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"success": False, "error": str(e)}
    
    def format_papers_for_slack(self, papers: List[Dict]) -> str:
        """Formatear papers para mostrar en Slack"""
        if not papers:
            return "No se encontraron papers."
        
        formatted = f"📚 **Encontré {len(papers)} papers:**\n\n"
        
        for i, paper in enumerate(papers[:5], 1):
            title = paper.get('title', 'Sin título')[:100]
            authors = paper.get('authors', [])
            author_str = ', '.join(authors[:2])
            if len(authors) > 2:
                author_str += f" +{len(authors)-2} más"
            
            categories = paper.get('categories', [])
            cat_str = ', '.join(categories[:2])
            
            url = paper.get('arxivUrl', paper.get('pdfUrl', ''))
            
            formatted += f"**{i}. {title}**\n"
            formatted += f"👥 *Autores:* {author_str}\n"
            if cat_str:
                formatted += f"🏷️ *Categorías:* {cat_str}\n"
            if url:
                formatted += f"🔗 {url}\n"
            formatted += "\n"
        
        return formatted
    
    def format_paper_details_for_slack(self, details: Dict) -> str:
        """Formatear detalles de paper para Slack"""
        if not details:
            return "No se encontraron detalles del paper."
        
        title = details.get('title', 'Sin título')
        authors = details.get('authors', [])
        summary = details.get('summary', 'Sin resumen disponible')
        categories = details.get('categories', [])
        published = details.get('published', 'Fecha desconocida')
        
        formatted = f"📄 **{title}**\n\n"
        formatted += f"👥 **Autores:** {', '.join(authors[:3])}\n"
        if len(authors) > 3:
            formatted += f"   *+{len(authors)-3} autores más*\n"
        
        formatted += f"📅 **Publicado:** {published[:10]}\n"
        formatted += f"🏷️ **Categorías:** {', '.join(categories[:3])}\n\n"
        
        # Resumen truncado
        if len(summary) > 500:
            summary = summary[:500] + "..."
        formatted += f"📝 **Resumen:**\n{summary}\n\n"
        
        # URLs
        if details.get('arxivUrl'):
            formatted += f"🔗 **ArXiv:** {details['arxivUrl']}\n"
        if details.get('pdfUrl'):
            formatted += f"📑 **PDF:** {details['pdfUrl']}\n"
        
        return formatted

# Instancia global
mcp_integration = MCPIntegration()