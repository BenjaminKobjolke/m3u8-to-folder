#!/usr/bin/env python3
"""Debug script to test m3u8 library behavior."""

import json
from pathlib import Path
import m3u8

def debug_m3u8_parser():
    """Debug the m3u8 library with our test file."""
    
    print("=== M3U8 Library Debug Script ===")
    print()
    
    # Parse the test file
    test_file = "test.m3u8"
    if not Path(test_file).exists():
        print(f"ERROR: {test_file} not found!")
        return
    
    print(f"Parsing file: {test_file}")
    print()
    
    try:
        # Method 1: Load from file
        print("=== Method 1: m3u8.load() ===")
        playlist = m3u8.load(test_file)
        
        print(f"Playlist type: {type(playlist)}")
        print(f"Number of segments: {len(playlist.segments)}")
        print(f"Target duration: {playlist.target_duration}")
        print(f"Is endlist: {playlist.is_endlist}")
        print()
        
        if playlist.segments:
            print("=== Examining Segments ===")
            
            # Show first few segments in detail
            for i, segment in enumerate(playlist.segments[:3]):
                print(f"Segment {i+1}:")
                print(f"  Type: {type(segment)}")
                print(f"  URI: {repr(segment.uri)}")
                print(f"  Duration: {segment.duration}")
                print(f"  Title: {repr(segment.title)}")
                
                # Show key attributes (avoiding problematic ones)
                print("  Key attributes:")
                key_attrs = ['uri', 'duration', 'title', 'discontinuity', 'key', 'byterange']
                for attr in key_attrs:
                    if hasattr(segment, attr):
                        try:
                            value = getattr(segment, attr)
                            print(f"    {attr}: {repr(value)}")
                        except Exception as e:
                            print(f"    {attr}: <Error: {e}>")
                print()
            
            # Extract file paths
            print("=== Extracting File Paths ===")
            extracted_files = []
            
            for i, segment in enumerate(playlist.segments):
                if segment.uri:
                    extracted_files.append(segment.uri)
                    if i < 5:  # Show first 5
                        filename = Path(segment.uri).name
                        print(f"  {i+1}. Path: {segment.uri}")
                        print(f"      Filename: {filename}")
                        print(f"      Title: {segment.title}")
            
            print(f"\nTotal extracted files: {len(extracted_files)}")
        
        # Method 2: Load from string content
        print("\n=== Method 2: m3u8.loads() ===")
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        playlist2 = m3u8.loads(content)
        print(f"Loaded from string - segments: {len(playlist2.segments)}")
        
        if playlist2.segments:
            print("First segment from string method:")
            segment = playlist2.segments[0]
            print(f"  URI: {repr(segment.uri)}")
            print(f"  Title: {repr(segment.title)}")
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_m3u8_parser()
