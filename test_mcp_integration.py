#!/usr/bin/env python3
"""
Test script para verificar la integración MCP
"""

import sys
import logging
from mcp_integration import mcp_integration

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mcp_integration():
    """Test completo de la integración MCP"""
    print("🧪 Testing MCP Integration")
    print("=" * 50)
    
    # Test 1: Inicialización
    print("\n📦 Test 1: Inicialización MCP")
    if mcp_integration.initialize():
        print("✅ MCP inicializado correctamente")
    else:
        print("❌ Error inicializando MCP")
        return False
    
    # Test 2: Búsqueda de papers
    print("\n🔍 Test 2: Búsqueda de papers")
    result = mcp_integration.search_papers("machine learning", max_results=3)
    
    if result.get("success"):
        papers = result.get("papers", [])
        print(f"✅ Encontrados {len(papers)} papers")
        if papers:
            print(f"   Primer paper: {papers[0].get('title', 'Sin título')[:60]}...")
    else:
        print(f"❌ Error buscando papers: {result.get('error')}")
        return False
    
    # Test 3: Categorías
    print("\n📂 Test 3: Categorías ArXiv")
    result = mcp_integration.get_arxiv_categories()
    
    if result.get("success"):
        categories = result.get("categories", {})
        print(f"✅ Encontradas {len(categories)} categorías")
        print(f"   Ejemplo: cs.AI = {categories.get('cs.AI', 'N/A')}")
    else:
        print(f"❌ Error obteniendo categorías: {result.get('error')}")
        return False
    
    # Test 4: Detalles de paper
    print("\n📄 Test 4: Detalles de paper")
    if papers:
        paper_id = papers[0].get('id', '').split('/')[-1]  # Extraer ID limpio
        if paper_id:
            result = mcp_integration.get_paper_details(paper_id)
            
            if result.get("success"):
                details = result.get("details", {})
                print(f"✅ Detalles obtenidos para paper {paper_id}")
                print(f"   Título: {details.get('title', 'N/A')[:60]}...")
            else:
                print(f"❌ Error obteniendo detalles: {result.get('error')}")
        else:
            print("⚠️ No se pudo extraer ID del paper")
    else:
        print("⚠️ No hay papers para obtener detalles")
    
    # Test 5: Estado del sistema
    print("\n📊 Test 5: Estado del sistema")
    result = mcp_integration.get_system_status()
    
    if result.get("success"):
        status = result.get("status", {})
        health = result.get("health", {})
        print(f"✅ Sistema {'saludable' if health.get('healthy') else 'con problemas'}")
        print(f"   Módulos activos: {status.get('mcpCount', 0)}")
        print(f"   Cache: {status.get('arxivCache', {}).get('size', 0)} elementos")
    else:
        print(f"❌ Error obteniendo estado: {result.get('error')}")
    
    # Test 6: Formateo para Slack
    print("\n💬 Test 6: Formateo para Slack")
    if papers:
        formatted = mcp_integration.format_papers_for_slack(papers[:2])
        print("✅ Formateo completado")
        print("   Preview:", formatted[:100] + "..." if len(formatted) > 100 else formatted)
        
        if len(papers) > 0:
            details_formatted = mcp_integration.format_paper_details_for_slack(papers[0])
            print("✅ Formateo de detalles completado")
            print("   Preview:", details_formatted[:100] + "..." if len(details_formatted) > 100 else details_formatted)
    else:
        print("⚠️ No hay papers para formatear")
    
    print("\n🎉 ¡Todos los tests completados exitosamente!")
    return True

if __name__ == "__main__":
    try:
        success = test_mcp_integration()
        if success:
            print("\n✅ Integración MCP lista para usar en el bot")
            sys.exit(0)
        else:
            print("\n❌ Hay problemas con la integración MCP")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error en tests: {e}")
        print(f"\n💥 Error ejecutando tests: {e}")
        sys.exit(1)