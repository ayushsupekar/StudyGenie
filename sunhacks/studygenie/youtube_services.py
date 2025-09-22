import os
import requests
import logging
import re
from collections import Counter
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def extract_keywords(text, top_n=5):
    """Extract document-specific keywords for highly relevant YouTube recommendations"""
    if not text:
        return []
    
    # Clean and normalize text
    text = text.lower()
    # Remove special characters and keep only alphanumeric and spaces
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    
    # Enhanced stop words to filter out generic terms
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
        'his', 'her', 'its', 'our', 'their', 'from', 'up', 'about', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'among', 'all', 'any', 'both', 'each',
        'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
        'so', 'than', 'too', 'very', 'just', 'now', 'here', 'there', 'when', 'where', 'why', 'how',
        'also', 'example', 'used', 'using', 'use', 'one', 'two', 'three', 'first', 'second', 'third',
        'page', 'document', 'text', 'content', 'information', 'data', 'file', 'pdf', 'image', 'covers',
        'includes', 'provides', 'explains', 'discusses', 'material', 'points', 'key'
    }
    
    # Extract meaningful technical phrases
    phrases = []
    sentences = text.split('.')
    
    for sentence in sentences[:15]:  # Check more sentences
        sentence = sentence.strip()
        if len(sentence) > 20:  # Meaningful sentences
            # Look for technical terms, proper nouns, and key concepts
            words = sentence.split()
            for i in range(len(words) - 1):
                if (len(words[i]) > 3 and len(words[i+1]) > 3 and
                    words[i] not in stop_words and words[i+1] not in stop_words):
                    phrase = f"{words[i]} {words[i+1]}"
                    phrases.append(phrase)
    
    # Extract single important words
    words = [word for word in text.split() if len(word) > 3 and word not in stop_words]
    
    # Prioritize technical and educational terms with expanded list
    priority_terms = []
    educational_indicators = [
        'programming', 'algorithm', 'function', 'method', 'class', 'variable', 'loop', 'condition', 
        'statement', 'syntax', 'code', 'software', 'computer', 'science', 'mathematics', 'physics', 
        'chemistry', 'biology', 'history', 'literature', 'language', 'theory', 'concept', 'principle', 
        'analysis', 'database', 'system', 'design', 'structure', 'process', 'implementation',
        'architecture', 'model', 'framework', 'development', 'engineering', 'technical', 'digital',
        'network', 'security', 'management', 'application', 'interface', 'protocol', 'standard'
    ]
    
    for word in words:
        if any(indicator in word for indicator in educational_indicators):
            priority_terms.append(word)
    
    # Count frequencies with better weighting
    word_counts = Counter(words)
    phrase_counts = Counter(phrases)
    
    # Combine and prioritize results with better logic
    all_keywords = []
    
    # Add priority terms first (technical/educational)
    all_keywords.extend(priority_terms[:3])
    
    # Add top technical phrases
    top_phrases = [phrase for phrase, count in phrase_counts.most_common(3) 
                  if count > 1 and any(term in phrase for term in educational_indicators)]
    all_keywords.extend(top_phrases[:2])
    
    # Add top frequent words that aren't already included
    top_words = [word for word, count in word_counts.most_common(top_n*2) 
                if word not in all_keywords and count > 1]
    all_keywords.extend(top_words[:3])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for keyword in all_keywords:
        clean_keyword = keyword.lower().strip()
        if clean_keyword not in seen and len(clean_keyword) > 2:
            seen.add(clean_keyword)
            unique_keywords.append(keyword)
    
    return unique_keywords[:top_n]

def fetch_youtube_videos(query, max_results=5):
    """Fetch YouTube videos using YouTube Data API v3"""
    try:
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            print("YouTube API key not found")
            return create_fallback_videos(query, max_results)
        
        print(f"Searching YouTube for: {query}")
        
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': f"{query} lecture tutorial",
            'type': 'video',
            'maxResults': max_results,
            'key': api_key,
            'order': 'relevance',
            'safeSearch': 'strict'
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            videos = []
            
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                # Get the best available thumbnail
                thumbnails = item['snippet']['thumbnails']
                thumbnail_url = (
                    thumbnails.get('high', {}).get('url') or
                    thumbnails.get('medium', {}).get('url') or
                    thumbnails.get('default', {}).get('url') or
                    f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                )
                
                video = {
                    'title': item['snippet']['title'],
                    'video_id': video_id,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'embed_url': f"https://www.youtube.com/embed/{video_id}",
                    'thumbnail': thumbnail_url,
                    'channel': item['snippet']['channelTitle'],
                    'description': item['snippet']['description'][:150] + '...' if len(item['snippet']['description']) > 150 else item['snippet']['description']
                }
                videos.append(video)
            
            print(f"Found {len(videos)} YouTube videos")
            return videos
        else:
            print(f"YouTube API error: {response.status_code}")
            return create_fallback_videos(query, max_results)
            
    except Exception as e:
        print(f"YouTube error: {e}")
        return create_fallback_videos(query, max_results)

def create_fallback_videos(query, max_results=3):
    """Create fallback video search links when API fails"""
    clean_query = query.replace('.pdf', '').strip()
    search_query = clean_query.replace(' ', '+')
    
    videos = [
        {
            'title': f'{clean_query} - Complete Tutorial',
            'video_id': 'search_result_1',
            'url': f'https://www.youtube.com/results?search_query={search_query}+tutorial',
            'thumbnail': 'https://via.placeholder.com/320x180/ff0000/ffffff?text=Search+YouTube',
            'channel': 'Search Results',
            'description': f'Search YouTube for {clean_query} tutorials and explanations'
        },
        {
            'title': f'{clean_query} - Explained Simply',
            'video_id': 'search_result_2',
            'url': f'https://www.youtube.com/results?search_query={search_query}+explained+simple',
            'thumbnail': 'https://via.placeholder.com/320x180/ff0000/ffffff?text=Search+YouTube',
            'channel': 'Search Results',
            'description': f'Find simple explanations of {clean_query} concepts'
        },
        {
            'title': f'{clean_query} - Course & Lectures',
            'video_id': 'search_result_3',
            'url': f'https://www.youtube.com/results?search_query={search_query}+course+lecture',
            'thumbnail': 'https://via.placeholder.com/320x180/ff0000/ffffff?text=Search+YouTube',
            'channel': 'Search Results',
            'description': f'Browse courses and lectures about {clean_query}'
        }
    ]
    
    return videos

def generate_enhanced_fallback_videos(query):
    """Generate comprehensive fallback recommendations with proper thumbnails"""
    clean_query = query.replace('.pdf', '').replace('_', ' ')
    search_query = clean_query.replace(' ', '+')
    
    fallback_videos = [
        {
            'title': f'{clean_query} - Complete Tutorial',
            'video_id': 'enhanced_search_1',
            'url': f'https://www.youtube.com/results?search_query={search_query}+complete+tutorial',
            'embed_url': '',
            'thumbnail': 'https://via.placeholder.com/320x180/1a1a2e/ffffff?text=YouTube+Tutorial',
            'channel': 'Educational Content',
            'description': f'Comprehensive tutorial covering {clean_query} concepts and applications.'
        },
        {
            'title': f'{clean_query} - Explained Simply',
            'video_id': 'enhanced_search_2', 
            'url': f'https://www.youtube.com/results?search_query={search_query}+explained+simple',
            'embed_url': '',
            'thumbnail': 'https://via.placeholder.com/320x180/16213e/ffffff?text=YouTube+Explanation',
            'channel': 'Learning Hub',
            'description': f'Clear explanation of {clean_query} with practical examples.'
        },
        {
            'title': f'{clean_query} - Course & Examples',
            'video_id': 'enhanced_search_3',
            'url': f'https://www.youtube.com/results?search_query={search_query}+course+examples',
            'embed_url': '',
            'thumbnail': 'https://via.placeholder.com/320x180/0f3460/ffffff?text=YouTube+Course', 
            'channel': 'Academic Channel',
            'description': f'Complete course on {clean_query} with real-world examples and practice.'
        }
    ]
    return fallback_videos

def extract_keywords_from_summary(summary_text):
    """Extract meaningful keywords from summary"""
    if not summary_text:
        return []
    
    # Remove bullet points and clean text
    text = summary_text.replace('•', '').replace('\n', ' ').lower()
    
    # Stop words to filter out
    stop_words = {
        'this', 'that', 'these', 'those', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'document', 'covers', 'includes', 'provides', 'explains', 'discusses', 'material',
        'content', 'information', 'key', 'points', 'main', 'important', 'essential', 'basic', 'fundamental'
    }
    
    # Extract words longer than 3 characters
    words = [word.strip('.,!?;:()[]{}"') for word in text.split() if len(word) > 3 and word not in stop_words]
    
    # Count word frequency
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get top 5 most frequent words
    top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    keywords = [keyword for keyword, count in top_keywords if count > 1 or len(top_keywords) < 3]
    
    return keywords[:5]

def extract_keywords(text, top_n=5):
    """Extract keywords from document text using NLP approach"""
    import re
    from collections import Counter
    
    if not text:
        return []
    
    # Clean text and extract words
    words = re.findall(r'\w+', text.lower())
    
    # Enhanced stopwords
    stopwords = {
        'the', 'is', 'and', 'of', 'in', 'a', 'to', 'for', 'with', 'on', 'at', 'by', 'from', 'as', 'an', 'are', 'was', 'were',
        'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'can', 'this', 'that', 'these', 'those', 'but', 'or', 'if', 'when', 'where', 'why', 'how', 'what', 'which', 'who',
        'document', 'covers', 'includes', 'provides', 'explains', 'discusses', 'material', 'content', 'information'
    }
    
    # Filter words
    filtered = [w for w in words if w not in stopwords and len(w) > 3]
    
    # Get most common words
    common = Counter(filtered).most_common(top_n)
    return [word for word, _ in common]

def get_video_recommendations_from_summary(summary_text, fallback_title=""):
    """Get YouTube videos using extracted keywords from summary"""
    try:
        # Extract keywords from summary
        keywords = extract_keywords(summary_text, top_n=5)
        
        if keywords:
            # Use top 3 keywords for search
            search_query = ' '.join(keywords[:3])
            print(f"Extracted keywords: {keywords}")
        else:
            # Fallback to document title
            search_query = fallback_title.replace('.pdf', '').replace('_', ' ')
            keywords = [search_query]
            print(f"Using fallback title: {search_query}")
        
        print(f"YouTube search query: {search_query}")
        
        # Get videos using the search query
        videos = fetch_youtube_videos(search_query, max_results=5)
        
        return videos, keywords
        
    except Exception as e:
        print(f"Error getting video recommendations: {e}")
        return [], []

def extract_educational_keywords(text):
    """Extract educational and learning-focused keywords from text"""
    if not text:
        return []
    
    import re
    
    # Educational patterns to look for
    educational_patterns = [
        r'\b(algorithm|programming|function|method|class|variable)\b',
        r'\b(concept|principle|theory|definition|explanation)\b',
        r'\b(tutorial|guide|introduction|basics|fundamentals)\b',
        r'\b(example|application|implementation|practice)\b',
        r'\b(analysis|design|development|structure)\b'
    ]
    
    educational_keywords = []
    text_lower = text.lower()
    
    for pattern in educational_patterns:
        matches = re.findall(pattern, text_lower)
        educational_keywords.extend(matches)
    
    # Remove duplicates and return top keywords
    unique_keywords = list(set(educational_keywords))
    return unique_keywords[:5]

def generate_comprehensive_search_strategies(keywords, doc_type):
    """Generate multiple comprehensive search strategies for deep topic coverage"""
    strategies = []
    
    if not keywords:
        return strategies
    
    # Strategy 1: Core concept tutorial
    if len(keywords) >= 2:
        strategies.append(f"{keywords[0]} {keywords[1]} complete tutorial")
    
    # Strategy 2: Fundamentals and basics
    if keywords:
        strategies.append(f"{keywords[0]} fundamentals basics explained")
    
    # Strategy 3: Advanced concepts
    if len(keywords) >= 3:
        strategies.append(f"{keywords[0]} {keywords[2]} advanced concepts")
    
    # Strategy 4: Practical applications
    if len(keywords) >= 2:
        strategies.append(f"{keywords[0]} {keywords[1]} practical examples")
    
    # Strategy 5: Course/lecture format
    if keywords:
        doc_context = get_document_context(doc_type)
        strategies.append(f"{keywords[0]} {doc_context} course lecture")
    
    # Strategy 6: Problem solving
    if len(keywords) >= 2:
        strategies.append(f"{keywords[0]} {keywords[1]} problems solutions")
    
    return strategies

def get_document_context(doc_type):
    """Get educational context based on document type"""
    context_map = {
        'Programming/Computer Science Material': 'programming coding',
        'Mathematics Material': 'mathematics math',
        'Physics Material': 'physics science',
        'Engineering Material': 'engineering technical',
        'Academic Study Material': 'academic study',
        'Educational Document': 'education learning'
    }
    return context_map.get(doc_type, 'tutorial')

def advanced_video_deduplication(videos):
    """Advanced deduplication with better similarity detection"""
    unique_videos = []
    seen_ids = set()
    processed_titles = []
    
    for video in videos:
        video_id = video.get('video_id', '')
        title = video.get('title', '').lower()
        
        # Skip exact ID duplicates
        if video_id in seen_ids:
            continue
        
        # Advanced title similarity check
        is_duplicate = False
        for existing_title in processed_titles:
            similarity = calculate_advanced_similarity(title, existing_title)
            if similarity > 0.75:  # 75% similarity threshold
                is_duplicate = True
                break
        
        if not is_duplicate:
            seen_ids.add(video_id)
            processed_titles.append(title)
            unique_videos.append(video)
    
    return unique_videos

def calculate_advanced_similarity(title1, title2):
    """Calculate advanced similarity between titles"""
    # Tokenize and clean
    words1 = set(word for word in title1.split() if len(word) > 2)
    words2 = set(word for word in title2.split() if len(word) > 2)
    
    if not words1 or not words2:
        return 0
    
    # Jaccard similarity
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    jaccard = len(intersection) / len(union) if union else 0
    
    # Length similarity bonus
    len_similarity = 1 - abs(len(words1) - len(words2)) / max(len(words1), len(words2))
    
    return (jaccard * 0.8) + (len_similarity * 0.2)

def calculate_title_similarity(title1, title2):
    """Calculate similarity between two video titles"""
    words1 = set(title1.split())
    words2 = set(title2.split())
    
    if not words1 or not words2:
        return 0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)

def rank_videos_by_deep_relevance(videos, keywords, summary_text):
    """Advanced ranking using deep content analysis"""
    if not videos:
        return videos
    
    scored_videos = []
    summary_words = set(summary_text.lower().split())
    
    for video in videos:
        score = 0
        title = video.get('title', '').lower()
        description = video.get('description', '').lower()
        channel = video.get('channel', '').lower()
        
        # Keyword matching (high weight)
        for keyword in keywords:
            if keyword.lower() in title:
                score += 5
            if keyword.lower() in description:
                score += 2
            if keyword.lower() in channel:
                score += 1
        
        # Summary content overlap
        title_words = set(title.split())
        desc_words = set(description.split())
        
        title_overlap = len(summary_words.intersection(title_words))
        desc_overlap = len(summary_words.intersection(desc_words))
        
        score += title_overlap * 2
        score += desc_overlap
        
        # Educational quality indicators
        quality_terms = {
            'tutorial': 4, 'explained': 4, 'course': 3, 'lecture': 3,
            'guide': 3, 'learn': 2, 'basics': 2, 'introduction': 2,
            'complete': 2, 'comprehensive': 3, 'step by step': 4
        }
        
        for term, weight in quality_terms.items():
            if term in title:
                score += weight
            if term in description:
                score += weight // 2
        
        # Channel credibility bonus
        credible_indicators = ['university', 'academy', 'education', 'institute', 'official']
        for indicator in credible_indicators:
            if indicator in channel:
                score += 3
        
        scored_videos.append((video, score))
    
    # Sort by score (descending)
    scored_videos.sort(key=lambda x: x[1], reverse=True)
    
    return [video for video, score in scored_videos]