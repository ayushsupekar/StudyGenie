#!/usr/bin/env python
"""
Test keyword extraction from summary
"""

import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studygenie.settings')
django.setup()

from youtube_services import extract_keywords_from_summary, get_video_recommendations_from_summary

def test_keyword_extraction():
    """Test keyword extraction from different summaries"""
    
    # Test with programming summary
    programming_summary = """
    This programming/computer science material focuses on control statements, covering key concepts including loops, conditions, and decision-making structures.
    
    Key Points:
    • Defines control flow concepts and their importance in programming
    • Covers technical topics including if-else statements, while loops, for loops
    • Explains methodologies for implementing conditional logic
    • Provides practical applications in software development
    """
    
    print("Testing Programming Summary:")
    keywords = extract_keywords_from_summary(programming_summary)
    print(f"Keywords extracted: {keywords}")
    
    videos, video_keywords = get_video_recommendations_from_summary(programming_summary, "Programming Tutorial")
    print(f"Videos found: {len(videos)}")
    for video in videos:
        print(f"- {video['title']}")
    
    print("\n" + "="*50 + "\n")
    
    # Test with database summary
    database_summary = """
    This database management material covers DBMS fundamentals, focusing on relational databases, SQL queries, and database design principles.
    
    Key Points:
    • Database architecture and ANSI-SPARC model
    • SQL commands and query optimization
    • Normalization and database design
    • Transaction management and ACID properties
    """
    
    print("Testing Database Summary:")
    keywords = extract_keywords_from_summary(database_summary)
    print(f"Keywords extracted: {keywords}")
    
    videos, video_keywords = get_video_recommendations_from_summary(database_summary, "Database Tutorial")
    print(f"Videos found: {len(videos)}")
    for video in videos:
        print(f"- {video['title']}")

if __name__ == "__main__":
    test_keyword_extraction()