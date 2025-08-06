#!/usr/bin/env python3
"""
Script to verify configuration consistency after migration
"""

import os
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_env_file():
    """Check .env file exists and has correct values"""
    env_file = Path(__file__).parent.parent / ".env"
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    content = env_file.read_text()
    checks = [
        ("QDRANT_URL", "da84a490-2db4-41eb-a610-9e96795692ce"),
        ("QDRANT_COLLECTION", "TestCollection6"),
        ("EMBEDDING_MODEL", "bge-m3"),
        ("API_PORT", "8001")
    ]
    
    print("🔍 Checking .env file...")
    all_good = True
    
    for key, expected_substring in checks:
        if f"{key}=" in content and expected_substring in content:
            print(f"✅ {key}: OK")
        else:
            print(f"❌ {key}: Missing or incorrect")
            all_good = False
    
    return all_good

def check_config_files():
    """Check YAML config files"""
    config_dir = Path(__file__).parent.parent / "config"
    files_to_check = ["config.dev.yaml", "config.prod.yaml", "config.yaml.example"]
    
    print("\n🔍 Checking config files...")
    all_good = True
    
    for file_name in files_to_check:
        config_file = config_dir / file_name
        if config_file.exists():
            content = config_file.read_text()
            if "TestCollection6" in content:
                print(f"✅ {file_name}: Collection name updated")
            else:
                print(f"❌ {file_name}: Collection name not updated")
                all_good = False
        else:
            print(f"❌ {file_name}: File not found")
            all_good = False
    
    return all_good

def check_docker_config():
    """Check Docker configuration"""
    docker_file = Path(__file__).parent.parent / "docker" / "docker-compose.yml"
    
    print("\n🔍 Checking docker-compose.yml...")
    
    if docker_file.exists():
        content = docker_file.read_text()
        if "TestCollection6" in content:
            print("✅ docker-compose.yml: Collection name updated")
            return True
        else:
            print("❌ docker-compose.yml: Collection name not updated")
            return False
    else:
        print("❌ docker-compose.yml: File not found")
        return False

def main():
    """Main verification function"""
    print("🔧 Configuration Migration Verification")
    print("=" * 50)
    
    env_ok = check_env_file()
    config_ok = check_config_files()
    docker_ok = check_docker_config()
    
    print("\n" + "=" * 50)
    
    if env_ok and config_ok and docker_ok:
        print("🎉 All configurations migrated successfully!")
        print("\n✅ Next steps:")
        print("   1. Run: python tools/check_config.py")
        print("   2. Test: python -m app.main")
        print("   3. API docs: http://localhost:8001/docs")
        return True
    else:
        print("❌ Some configurations need attention!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
