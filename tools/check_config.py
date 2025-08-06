#!/usr/bin/env python3
"""
Configuration checker tool
Tests all configuration and service connections
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import ConfigManager, get_config
from app.services.search_service import SearchService

async def check_config(config_path: str = None):
    """Check configuration and service health"""
    print("🔍 Configuration Checker")
    print("=" * 50)
    
    # Load configuration
    try:
        if config_path:
            config_manager = ConfigManager(config_path)
            config = config_manager.load_config()
            print(f"✅ Configuration loaded from: {config_path}")
        else:
            config = get_config()
            print("✅ Configuration loaded from default sources")
        
        print(f"   Environment: {config.environment}")
        print(f"   Vector DB: {config.vector_db.provider} at {config.vector_db.url}")
        print(f"   Embedding: {config.embedding.provider} - {config.embedding.model}")
        print(f"   API: {config.api.host}:{config.api.port}")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    print()
    
    # Test service connections
    try:
        print("🔗 Testing service connections...")
        
        search_service = SearchService(config)
        await search_service.initialize()
        
        health = await search_service.health_check()
        
        for service, status in health.items():
            status_icon = "✅" if status else "❌"
            print(f"   {status_icon} {service}: {'healthy' if status else 'unhealthy'}")
        
        if all(health.values()):
            print("\n✅ All services are healthy!")
            return True
        else:
            print("\n⚠️ Some services are unhealthy")
            return False
            
    except Exception as e:
        print(f"❌ Service connection error: {e}")
        return False
    
    finally:
        if 'search_service' in locals():
            await search_service.close()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Check configuration and service health")
    parser.add_argument(
        "--config", 
        help="Path to configuration file",
        type=str
    )
    
    args = parser.parse_args()
    
    # Run the check
    try:
        success = asyncio.run(check_config(args.config))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🔄 Check cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
