#!/usr/bin/env python
"""
Test YouTube API functionality
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from youtube_services import get_youtube_videos, get_video_recommendations_from_summary

def test_youtube_api():
    """Test YouTube API directly"""
    print("Testing YouTube API...")
    
    # Test direct API call
    videos = get_youtube_videos("python programming", max_results=3)
    
    if videos:
        print(f"SUCCESS: Found {len(videos)} videos")
        for i, video in enumerate(videos, 1):
            print(f"{i}. {video['title']}")
            print(f"   Channel: {video['channel']}")
            print(f"   URL: {video['url']}")
    else:
        print("FAILED: No videos found")

def test_summary_integration():
    """Test summary to YouTube integration"""
    print("\nTesting summary integration...")
    
    sample_summary = "This document covers programming concepts including variables, loops, and functions in Python."
    
    videos, keywords = get_video_recommendations_from_summary(sample_summary, "Python Programming")
    
    print(f"Keywords extracted: {keywords}")
    print(f"Videos found: {len(videos)}")
    
    for video in videos:
        print(f"- {video['title']}")

if __name__ == "__main__":
    test_youtube_api()
    test_summary_integration()