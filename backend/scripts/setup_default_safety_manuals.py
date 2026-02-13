import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.ra_system.default_safety_processor import default_safety_processor


def main():
    """Process default safety manuals"""
    print("=" * 60)
    print("PROCESSING DEFAULT SAFETY MANUALS")
    print("=" * 60)
    
    # Get default manuals
    manuals = default_safety_processor.get_default_manuals()
    
    if not manuals:
        print("\n❌ ERROR: No safety manuals found!")
        print(f"Please add PDF, DOCX, or TXT files to:")
        print(f"{default_safety_processor.default_manuals_dir}")
        return
    
    print(f"\n✅ Found {len(manuals)} safety manual(s):")
    for manual in manuals:
        print(f"   - {manual.name}")
    
    print("\n🔄 Processing manuals...")
    result = default_safety_processor.process_default_manuals()
    
    if result['success']:
        print("\n✅ SUCCESS!")
        print(f"   - Manuals processed: {result['manuals_processed']}")
        print(f"   - Total chunks: {result['chunks_count']}")
        print(f"   - Total words: {result['word_count']}")
        print(f"\n📁 Files created:")
        print(f"   - {result['index_path']}")
        print(f"   - {result['chunks_path']}")
        print(f"   - {result['metadata_path']}")
    else:
        print(f"\n❌ ERROR: {result.get('error')}")


if __name__ == "__main__":
    main()