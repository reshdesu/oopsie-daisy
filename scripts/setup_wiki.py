#!/usr/bin/env python3
"""
Script to help set up GitHub Wiki pages from documentation files.
This creates the wiki structure and provides guidance for manual setup.
"""

import os
from pathlib import Path

def main():
    print("🐱 Oopsie Daisy Wiki Setup Helper")
    print("=" * 50)
    
    docs_dir = Path(__file__).parent.parent / "docs"
    
    if not docs_dir.exists():
        print("❌ Docs directory not found!")
        return
    
    print("\n📚 Documentation files found:")
    
    wiki_pages = {
        "Home.md": "Main wiki homepage",
        "Installation.md": "Installation guide for all platforms", 
        "Windows-SmartScreen.md": "Windows security warnings explanation",
        "User-Guide.md": "How to use the application",
        "Common-Issues.md": "FAQ and troubleshooting",
        "Architecture.md": "Technical architecture overview",
        "Development.md": "Development setup and contributing",
        "Testing.md": "Testing methodology and coverage",
        "CI-CD-Process.md": "Build and release process",
        "GPU-Acceleration.md": "GPU support details",
        "Hardware-Monitoring.md": "System monitoring features",
        "Community-Testing.md": "Community testing program"
    }
    
    existing_files = []
    missing_files = []
    
    for filename, description in wiki_pages.items():
        file_path = docs_dir / filename
        if file_path.exists():
            existing_files.append((filename, description))
            print(f"  ✅ {filename} - {description}")
        else:
            missing_files.append((filename, description))
            print(f"  ⚠️  {filename} - {description} (MISSING)")
    
    print(f"\n📊 Status: {len(existing_files)}/{len(wiki_pages)} pages ready")
    
    if missing_files:
        print(f"\n⚠️  Missing files to create:")
        for filename, description in missing_files:
            print(f"  - {filename}: {description}")
    
    print("\n🚀 Next Steps:")
    print("1. Go to https://github.com/reshdesu/oopsie-daisy/wiki")
    print("2. Click 'Create the first page' or edit existing pages")
    print("3. Copy content from docs/ files to corresponding wiki pages:")
    
    for filename, description in existing_files:
        wiki_name = filename.replace('.md', '').replace('-', ' ').title()
        print(f"   📝 {filename} → Wiki page: '{wiki_name}'")
    
    print("\n📋 Wiki Page Mapping:")
    print("docs/Home.md → Wiki Home page")
    print("docs/Installation.md → Installation page")  
    print("docs/Windows-SmartScreen.md → Windows SmartScreen page")
    print("README.md → Keep as main repository README (streamlined)")
    
    print("\n💡 Tips:")
    print("- Use [[Page Name]] syntax for internal wiki links")
    print("- GitHub Wiki automatically creates navigation")
    print("- Images can be uploaded directly to wiki pages")
    print("- Wiki has built-in search functionality")
    
    print("\n🎯 Benefits of GitHub Wiki:")
    print("✅ Cleaner, more organized documentation")
    print("✅ Better navigation and search")
    print("✅ Collaborative editing")
    print("✅ Automatic table of contents")
    print("✅ Streamlined main README")

if __name__ == "__main__":
    main()