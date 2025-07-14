#!/usr/bin/env python3
"""
Reddit User Persona Analyzer - Fixed Version with Better Setup

This script scrapes a Reddit user's profile and generates a detailed user persona
based on their posts and comments, with citations for each characteristic.
"""

import praw
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import requests
from collections import Counter
import time
import os
from urllib.parse import urlparse
import argparse
import sys


# Configuration - UPDATE THESE WITH YOUR ACTUAL API KEYS
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', "EcVL9PIcZAV6XcdczKeEtg")
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET',"HYgoOu-GiT863wcCaWV4dgDJz3QHlA" )
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'PersonaAnalyzer/1.0')
GROQ_API_KEY = os.getenv('GROQ_API_KEY',"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" )

# Updated API endpoint
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

@dataclass
class Citation:
    """Represents a citation for a persona characteristic"""
    post_id: str
    post_title: str
    content: str
    url: str
    created_utc: float
    subreddit: str
    content_type: str  # 'post' or 'comment'

@dataclass
class PersonaCharacteristic:
    """Represents a characteristic of the user persona with citations"""
    category: str
    trait: str
    confidence: float  # 0.0 to 1.0
    description: str
    citations: List[Citation]

@dataclass
class UserPersona:
    """Complete user persona with all characteristics"""
    username: str
    analysis_date: str
    # Basic Demographics
    age: str
    occupation: str
    status: str
    location: str
    tier: str
    archetype: str
    
    # Personality Traits (slider format)
    personality_traits: Dict[str, float]  # e.g., {"introvert_extrovert": 0.7, "intuition_sensing": 0.3}
    
    # Motivations (bar chart format)
    motivations: Dict[str, float]  # e.g., {"convenience": 0.8, "wellness": 0.6}
    
    # Behavior & Habits
    behavior_habits: List[str]
    
    # Frustrations
    frustrations: List[str]
    
    # Goals & Needs
    goals_needs: List[str]
    
    # Quote (representative statement)
    quote: str
    
    # Activity patterns and other metadata
    activity_patterns: Dict[str, Any]
    characteristics: List[PersonaCharacteristic]
    interests: List[str]
    brand_preferences: List[str]

class GroqClient:
    """Improved client for Groq API with better error handling"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = GROQ_API_URL
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def chat_completion(self, messages: List[Dict], model: str = "llama3-8b-8192", temperature: float = 0.3):
        """Send a chat completion request to Groq API with improved error handling"""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 4000,
            "stream": False
        }
        
        try:
            print(f"Making request to: {self.api_url}")
            print(f"Using model: {model}")
            
            response = requests.post(
                self.api_url, 
                headers=self.headers, 
                json=payload,
                timeout=60
            )
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Response headers: {response.headers}")
                print(f"Response content: {response.text}")
                
                # Try alternative models if the primary one fails
                if model == "llama3-8b-8192":
                    print("Trying alternative model...")
                    payload["model"] = "mixtral-8x7b-32768"
                    response = requests.post(
                        self.api_url, 
                        headers=self.headers, 
                        json=payload,
                        timeout=60
                    )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            raise Exception(f"Groq API request failed: {str(e)}")

class RedditPersonaAnalyzer:
    """Main class for analyzing Reddit user personas"""
    
    def __init__(self):
        """Initialize the analyzer with validation"""
        self.reddit = None
        self.groq_client = None
        self.validate_credentials()
        self.setup_reddit_client()
        self.setup_groq_client()
    
    def validate_credentials(self):
        """Validate that all required credentials are provided"""
        missing_creds = []
        
        if not REDDIT_CLIENT_ID or REDDIT_CLIENT_ID == 'YOUR_REDDIT_CLIENT_ID':
            missing_creds.append('REDDIT_CLIENT_ID')
        
        if not REDDIT_CLIENT_SECRET or REDDIT_CLIENT_SECRET == 'YOUR_REDDIT_CLIENT_SECRET':
            missing_creds.append('REDDIT_CLIENT_SECRET')
        
        if not GROQ_API_KEY or GROQ_API_KEY == 'YOUR_GROQ_API_KEY':
            missing_creds.append('GROQ_API_KEY')
        
        if missing_creds:
            print("❌ Missing required credentials:")
            for cred in missing_creds:
                print(f"   - {cred}")
            print("\n📋 Setup Instructions:")
            print("1. Get Reddit API credentials from https://www.reddit.com/prefs/apps")
            print("2. Get Groq API key from https://console.groq.com/")
            print("3. Set environment variables or update the script directly")
            print("\nFor detailed setup instructions, see the setup guide.")
            sys.exit(1)
    
    def setup_reddit_client(self):
        """Setup Reddit API client with validation"""
        try:
            self.reddit = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT
            )
            # Test the connection by making a simple request
            test_sub = self.reddit.subreddit('test')
            test_sub.id  # This will fail if credentials are invalid
            print("✅ Reddit client initialized successfully")
        except Exception as e:
            print(f"❌ Reddit client setup failed: {e}")
            print("Please check your Reddit API credentials")
            sys.exit(1)
    
    def setup_groq_client(self):
        """Setup Groq API client with validation"""
        try:
            self.groq_client = GroqClient(GROQ_API_KEY)
            # Test the connection with a simple request
            test_messages = [{"role": "user", "content": "Hello"}]
            response = self.groq_client.chat_completion(test_messages)
            print("✅ Groq client initialized successfully")
        except Exception as e:
            print(f"❌ Groq client setup failed: {e}")
            print("Please check your Groq API key")
            sys.exit(1)
    
    def extract_username_from_url(self, url: str) -> str:
        """Extract username from Reddit profile URL"""
        # Handle various Reddit URL formats
        patterns = [
            r'reddit\.com/user/([^/]+)',
            r'reddit\.com/u/([^/]+)',
            r'www\.reddit\.com/user/([^/]+)',
            r'www\.reddit\.com/u/([^/]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If no pattern matches, assume it's just a username
        if '/' not in url and 'reddit.com' not in url:
            return url
        
        raise ValueError(f"Could not extract username from URL: {url}")
    
    def scrape_user_content(self, username: str, limit: int = 100) -> Dict[str, List[Dict]]:
        """
        Scrape user's posts and comments with better error handling
        
        Args:
            username: Reddit username
            limit: Maximum number of posts/comments to scrape
            
        Returns:
            Dictionary containing posts and comments
        """
        try:
            user = self.reddit.redditor(username)
            
            # Test if user exists
            try:
                user.id  # This will raise an exception if user doesn't exist
                print(f"✅ Found user: {username}")
            except Exception:
                raise Exception(f"User '{username}' not found or inaccessible")
            
            # Scrape posts
            posts = []
            try:
                print(f"🔍 Scraping posts...")
                for i, post in enumerate(user.submissions.new(limit=limit)):
                    if i >= limit:
                        break
                    posts.append({
                        'id': post.id,
                        'title': post.title,
                        'selftext': post.selftext,
                        'subreddit': str(post.subreddit),
                        'created_utc': post.created_utc,
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'url': f"https://reddit.com{post.permalink}",
                        'content_type': 'post'
                    })
                    if i % 10 == 0:
                        print(f"   Scraped {i+1} posts...")
                print(f"✅ Scraped {len(posts)} posts")
            except Exception as e:
                print(f"⚠️ Warning: Error scraping posts: {e}")
            
            # Scrape comments
            comments = []
            try:
                print(f"🔍 Scraping comments...")
                for i, comment in enumerate(user.comments.new(limit=limit)):
                    if i >= limit:
                        break
                    comments.append({
                        'id': comment.id,
                        'body': comment.body,
                        'subreddit': str(comment.subreddit),
                        'created_utc': comment.created_utc,
                        'score': comment.score,
                        'post_title': comment.submission.title if hasattr(comment, 'submission') else 'N/A',
                        'url': f"https://reddit.com{comment.permalink}",
                        'content_type': 'comment'
                    })
                    if i % 10 == 0:
                        print(f"   Scraped {i+1} comments...")
                print(f"✅ Scraped {len(comments)} comments")
            except Exception as e:
                print(f"⚠️ Warning: Error scraping comments: {e}")
            
            if not posts and not comments:
                raise Exception("No content found for this user")
            
            return {
                'posts': posts,
                'comments': comments,
                'username': username,
                'total_posts': len(posts),
                'total_comments': len(comments)
            }
            
        except Exception as e:
            raise Exception(f"Error scraping user content: {str(e)}")
    
    def analyze_activity_patterns(self, content: Dict) -> Dict[str, Any]:
        """Analyze user's activity patterns"""
        posts = content['posts']
        comments = content['comments']
        
        # Time analysis
        all_timestamps = [p['created_utc'] for p in posts] + [c['created_utc'] for c in comments]
        
        # Subreddit analysis
        subreddits = [p['subreddit'] for p in posts] + [c['subreddit'] for c in comments]
        top_subreddits = Counter(subreddits).most_common(10)
        
        # Activity frequency
        recent_activity = len([t for t in all_timestamps if t > time.time() - 30*24*3600])  # Last 30 days
        
        return {
            'total_activity': len(all_timestamps),
            'recent_activity_30d': recent_activity,
            'top_subreddits': top_subreddits,
            'posts_vs_comments_ratio': len(posts) / max(len(comments), 1),
            'avg_post_score': sum(p['score'] for p in posts) / max(len(posts), 1),
            'avg_comment_score': sum(c['score'] for c in comments) / max(len(comments), 1)
        }
    
    def generate_persona_with_llm(self, content: Dict, activity_patterns: Dict) -> UserPersona:
        """Generate user persona using Groq LLM analysis"""
        # Prepare content for LLM
        posts_text = "\n".join([f"Title: {p['title']}\nContent: {p['selftext'][:500]}" for p in content['posts'][:20]])
        comments_text = "\n".join([f"Comment: {c['body'][:300]}" for c in content['comments'][:30]])
        
        subreddits_list = ", ".join([f"{sub[0]} ({sub[1]} posts)" for sub in activity_patterns['top_subreddits'][:10]])
        
        # Truncate content if too long
        max_content_length = 8000
        if len(posts_text) > max_content_length:
            posts_text = posts_text[:max_content_length] + "..."
        if len(comments_text) > max_content_length:
            comments_text = comments_text[:max_content_length] + "..."
        
        prompt = f"""
        Analyze the following Reddit user's activity and create a detailed user persona.
        
        Username: {content['username']}
        Total Posts: {content['total_posts']}
        Total Comments: {content['total_comments']}
        Top Subreddits: {subreddits_list}
        
        Recent Posts:
        {posts_text}
        
        Recent Comments:
        {comments_text}
        
        Please provide a detailed analysis in the following JSON format:
        {{
            "age": "estimated age or age range (e.g., '31', '25-30')",
            "occupation": "likely occupation based on content",
            "status": "relationship/life status (e.g., 'Single', 'Married', 'Student')",
            "location": "likely location or region",
            "tier": "user type/segment (e.g., 'Early Adopter', 'Power User', 'Casual User')",
            "archetype": "user archetype (e.g., 'The Creator', 'The Explorer', 'The Helper')",
            
            "personality_traits": {{
                "introvert_extrovert": 0.7,
                "intuition_sensing": 0.3,
                "feeling_thinking": 0.6,
                "perceiving_judging": 0.4
            }},
            
            "motivations": {{
                "convenience": 0.8,
                "wellness": 0.6,
                "speed": 0.4,
                "preferences": 0.7,
                "comfort": 0.5,
                "social_connection": 0.6,
                "achievement": 0.7,
                "learning": 0.8
            }},
            
            "behavior_habits": [
                "List of observed behaviors and habits from their posts/comments",
                "Include specific patterns you notice"
            ],
            
            "frustrations": [
                "List of frustrations and pain points mentioned",
                "Include specific complaints or challenges"
            ],
            
            "goals_needs": [
                "List of goals and needs expressed",
                "Include aspirations and desired outcomes"
            ],
            
            "quote": "A representative quote that captures their essence",
            
            "interests": ["list of interests"],
            "brand_preferences": ["list of mentioned brands or preferences"]
        }}
        
        Return ONLY the JSON object, no additional text.
        """
        
        try:
            messages = [
                {"role": "system", "content": "You are an expert user researcher and data analyst specializing in social media persona analysis. You must return only valid JSON."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.groq_client.chat_completion(messages, temperature=0.3)
            response_text = response['choices'][0]['message']['content'].strip()
            
            # Clean up the response to ensure it's valid JSON
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            # Parse JSON response
            persona_data = json.loads(response_text)
            
            # Create persona object
            persona = UserPersona(
                username=content['username'],
                analysis_date=datetime.now().isoformat(),
                age=persona_data.get('age', 'Unknown'),
                occupation=persona_data.get('occupation', 'Unknown'),
                status=persona_data.get('status', 'Unknown'),
                location=persona_data.get('location', 'Unknown'),
                tier=persona_data.get('tier', 'Unknown'),
                archetype=persona_data.get('archetype', 'Unknown'),
                personality_traits=persona_data.get('personality_traits', {}),
                motivations=persona_data.get('motivations', {}),
                behavior_habits=persona_data.get('behavior_habits', []),
                frustrations=persona_data.get('frustrations', []),
                goals_needs=persona_data.get('goals_needs', []),
                quote=persona_data.get('quote', ''),
                activity_patterns=activity_patterns,
                characteristics=[],
                interests=persona_data.get('interests', []),
                brand_preferences=persona_data.get('brand_preferences', [])
            )
            
            return persona
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"Response text: {response_text}")
            return self.create_fallback_persona(content, activity_patterns)
        except Exception as e:
            print(f"❌ Error generating persona with LLM: {str(e)}")
            return self.create_fallback_persona(content, activity_patterns)
    
    def create_fallback_persona(self, content: Dict, activity_patterns: Dict) -> UserPersona:
        """Create a basic persona when LLM analysis fails"""
        print("⚠️ Creating fallback persona based on basic analysis...")
        
        # Basic analysis without LLM
        top_subreddits = [sub[0] for sub in activity_patterns['top_subreddits'][:5]]
        
        # Simple interest detection
        interests = []
        for sub in top_subreddits:
            if sub not in ['AskReddit', 'funny', 'pics', 'videos', 'news']:
                interests.append(sub)
        
        # Basic behavior analysis
        behavior_habits = [
            f"Active in {len(top_subreddits)} main subreddits",
            f"Posts {activity_patterns['posts_vs_comments_ratio']:.1f}x more than comments" if activity_patterns['posts_vs_comments_ratio'] > 1 else "Comments more than posts"
        ]
        
        return UserPersona(
            username=content['username'],
            analysis_date=datetime.now().isoformat(),
            age="Unknown",
            occupation="Unknown",
            status="Unknown",
            location="Unknown",
            tier="Regular User",
            archetype="The Participant",
            personality_traits={
                "introvert_extrovert": 0.5,
                "intuition_sensing": 0.5,
                "feeling_thinking": 0.5,
                "perceiving_judging": 0.5
            },
            motivations={
                "social_connection": 0.6,
                "information": 0.7,
                "entertainment": 0.8
            },
            behavior_habits=behavior_habits,
            frustrations=["Unable to analyze due to API limitations"],
            goals_needs=["Further analysis needed"],
            quote="Profile requires deeper analysis",
            activity_patterns=activity_patterns,
            characteristics=[],
            interests=interests,
            brand_preferences=[]
        )
    
    def find_supporting_evidence(self, content: Dict, persona: UserPersona) -> List[PersonaCharacteristic]:
        """Find supporting evidence for persona characteristics"""
        characteristics = []
        
        # Analyze interests
        for interest in persona.interests:
            citations = self._find_citations_for_trait(content, interest, 'interest')
            if citations:
                characteristics.append(PersonaCharacteristic(
                    category='interests',
                    trait=interest,
                    confidence=min(len(citations) * 0.3, 1.0),
                    description=f"User shows interest in {interest}",
                    citations=citations
                ))
        
        # Analyze behavior & habits
        for habit in persona.behavior_habits:
            citations = self._find_citations_for_trait(content, habit, 'behavior')
            if citations:
                characteristics.append(PersonaCharacteristic(
                    category='behavior_habits',
                    trait=habit,
                    confidence=min(len(citations) * 0.3, 1.0),
                    description=f"User exhibits this behavior: {habit}",
                    citations=citations
                ))
        
        return characteristics
    
    def _find_citations_for_trait(self, content: Dict, trait: str, category: str) -> List[Citation]:
        """Find citations that support a specific trait"""
        citations = []
        trait_lower = trait.lower()
        
        # Search in posts
        for post in content['posts']:
            title_lower = post['title'].lower()
            content_lower = post['selftext'].lower()
            
            if trait_lower in title_lower or trait_lower in content_lower:
                citations.append(Citation(
                    post_id=post['id'],
                    post_title=post['title'],
                    content=post['selftext'][:300] if post['selftext'] else post['title'],
                    url=post['url'],
                    created_utc=post['created_utc'],
                    subreddit=post['subreddit'],
                    content_type='post'
                ))
        
        # Search in comments
        for comment in content['comments']:
            body_lower = comment['body'].lower()
            
            if trait_lower in body_lower:
                citations.append(Citation(
                    post_id=comment['id'],
                    post_title=comment['post_title'],
                    content=comment['body'][:300],
                    url=comment['url'],
                    created_utc=comment['created_utc'],
                    subreddit=comment['subreddit'],
                    content_type='comment'
                ))
        
        return citations[:5]  # Limit to 5 citations per trait
    
    def generate_persona_report(self, persona: UserPersona) -> str:
        """Generate a comprehensive persona report"""
        
        def create_bar_chart(value, max_width=20):
            """Create a simple ASCII bar chart"""
            filled = int(value * max_width)
            return "█" * filled + "░" * (max_width - filled)
        
        def create_slider(value, max_width=20):
            """Create a simple ASCII slider"""
            pos = int(value * max_width)
            slider = "─" * max_width
            return slider[:pos] + "●" + slider[pos+1:]
        
        report = f"""
# User Persona Report: {persona.username}

**Analysis Date:** {persona.analysis_date}

## Basic Information

**AGE:** {persona.age}
**OCCUPATION:** {persona.occupation}
**STATUS:** {persona.status}
**LOCATION:** {persona.location}
**TIER:** {persona.tier}
**ARCHETYPE:** {persona.archetype}

## Personality Traits

**INTROVERT** {create_slider(persona.personality_traits.get('introvert_extrovert', 0.5))} **EXTROVERT**
**INTUITION** {create_slider(1 - persona.personality_traits.get('intuition_sensing', 0.5))} **SENSING**
**FEELING** {create_slider(1 - persona.personality_traits.get('feeling_thinking', 0.5))} **THINKING**
**PERCEIVING** {create_slider(1 - persona.personality_traits.get('perceiving_judging', 0.5))} **JUDGING**

## Motivations

"""
        
        # Add motivations with bar charts
        for motivation, value in persona.motivations.items():
            bar = create_bar_chart(value)
            report += f"**{motivation.upper()}** {bar} ({value:.1f})\n"
        
        report += f"""

## Behavior & Habits

{chr(10).join(f"• {habit}" for habit in persona.behavior_habits)}

## Frustrations

{chr(10).join(f"• {frustration}" for frustration in persona.frustrations)}

## Goals & Needs

{chr(10).join(f"• {goal}" for goal in persona.goals_needs)}

## Representative Quote

> "{persona.quote}"

## Interests

{', '.join(persona.interests)}

## Brand Preferences

{', '.join(persona.brand_preferences)}

## Activity Patterns

- **Total Activity:** {persona.activity_patterns.get('total_activity', 0)} posts/comments
- **Recent Activity (30d):** {persona.activity_patterns.get('recent_activity_30d', 0)} posts/comments
- **Posts vs Comments Ratio:** {persona.activity_patterns.get('posts_vs_comments_ratio', 0):.2f}
- **Average Post Score:** {persona.activity_patterns.get('avg_post_score', 0):.1f}
- **Average Comment Score:** {persona.activity_patterns.get('avg_comment_score', 0):.1f}

## Top Subreddits

{chr(10).join(f"- {sub[0]} ({sub[1]} posts)" for sub in persona.activity_patterns.get('top_subreddits', [])[:10])}

## Supporting Evidence & Citations

"""
        
        # Group characteristics by category
        categories = {}
        for char in persona.characteristics:
            if char.category not in categories:
                categories[char.category] = []
            categories[char.category].append(char)
        
        # Add characteristics with citations
        for category, chars in categories.items():
            report += f"### {category.replace('_', ' ').title()}\n\n"
            
            for char in chars:
                report += f"**{char.trait}** (Confidence: {char.confidence:.1f})\n"
                report += f"{char.description}\n\n"
                
                if char.citations:
                    report += "**Supporting Evidence:**\n"
                    for citation in char.citations:
                        date_str = datetime.fromtimestamp(citation.created_utc).strftime('%Y-%m-%d')
                        report += f"- [{citation.content_type.title()}] r/{citation.subreddit} ({date_str}): {citation.content[:100]}...\n"
                        report += f"  Link: {citation.url}\n"
                    report += "\n"
        
        report += f"""

---

*This persona analysis was generated automatically based on publicly available Reddit activity. 
The analysis is for research and understanding purposes only.*

*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
    
    def save_persona_data(self, persona: UserPersona, filename: str = None):
        """Save persona data to JSON file"""
        if filename is None:
            filename = f"persona_{persona.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert to dictionary for JSON serialization
        persona_dict = asdict(persona)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(persona_dict, f, indent=2, ensure_ascii=False, default=str)
            print(f"✅ Persona data saved to: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error saving persona data: {e}")
            return None
    
    def analyze_user(self, username_or_url: str, limit: int = 100) -> UserPersona:
        """
        Main method to analyze a Reddit user and generate persona
        
        Args:
            username_or_url: Reddit username or profile URL
            limit: Maximum number of posts/comments to analyze
            
        Returns:
            UserPersona object with complete analysis
        """
        try:
            # Extract username from URL if needed
            if 'reddit.com' in username_or_url:
                username = self.extract_username_from_url(username_or_url)
            else:
                username = username_or_url
            
            print(f"🚀 Starting analysis for user: {username}")
            
            # Step 1: Scrape user content
            print("\n📊 Step 1: Scraping user content...")
            content = self.scrape_user_content(username, limit)
            
            # Step 2: Analyze activity patterns
            print("\n📈 Step 2: Analyzing activity patterns...")
            activity_patterns = self.analyze_activity_patterns(content)
            
            # Step 3: Generate persona with LLM
            print("\n🧠 Step 3: Generating persona with AI analysis...")
            persona = self.generate_persona_with_llm(content, activity_patterns)
            
            # Step 4: Find supporting evidence
            print("\n🔍 Step 4: Finding supporting evidence...")
            characteristics = self.find_supporting_evidence(content, persona)
            persona.characteristics = characteristics
            
            print("\n✅ Analysis complete!")
            return persona
            
        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
            raise

def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(
        description="Analyze Reddit user profiles and generate detailed personas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python persona_analyzer.py spez
  python persona_analyzer.py https://www.reddit.com/user/spez
  python persona_analyzer.py spez --limit 200 --output spez_persona.json
  
Setup:
  1. Get Reddit API credentials: https://www.reddit.com/prefs/apps
  2. Get Groq API key: https://console.groq.com/
  3. Set environment variables or update script constants
        """
    )
    
    parser.add_argument(
        'username',
        help='Reddit username or profile URL to analyze'
    )
    
    parser.add_argument(
        '--limit',
        type=int,
        default=100,
        help='Maximum number of posts/comments to analyze (default: 100)'
    )
    
    parser.add_argument(
        '--output',
        help='Output filename for JSON data (optional)'
    )
    
    parser.add_argument(
        '--report-only',
        action='store_true',
        help='Only generate and display the report (no JSON output)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress progress messages'
    )
    
    args = parser.parse_args()
    
    # Suppress print statements if quiet mode
    if args.quiet:
        import builtins
        def quiet_print(*args, **kwargs):
            pass
        builtins.print = quiet_print
    
    try:
        # Initialize analyzer
        analyzer = RedditPersonaAnalyzer()
        
        # Perform analysis
        persona = analyzer.analyze_user(args.username, args.limit)
        
        # Generate and display report
        print("\n" + "="*80)
        print("PERSONA ANALYSIS REPORT")
        print("="*80)
        
        report = analyzer.generate_persona_report(persona)
        print(report)
        
        # Save data if requested
        if not args.report_only:
            filename = analyzer.save_persona_data(persona, args.output)
            if filename:
                print(f"\n💾 Full persona data saved to: {filename}")
        
        print("\n🎉 Analysis completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        sys.exit(1)

# Additional utility functions

def validate_environment():
    """Validate that the environment is properly set up"""
    issues = []
    
    # Check Python version
    if sys.version_info < (3, 7):
        issues.append("Python 3.7+ required")
    
    # Check required packages
    required_packages = ['praw', 'requests']
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            issues.append(f"Missing package: {package}")
    
    # Check API credentials
    if not REDDIT_CLIENT_ID or REDDIT_CLIENT_ID == 'YOUR_REDDIT_CLIENT_ID':
        issues.append("Reddit API credentials not configured")
    
    if not GROQ_API_KEY or GROQ_API_KEY == 'YOUR_GROQ_API_KEY':
        issues.append("Groq API key not configured")
    
    if issues:
        print("⚠️ Environment validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    
    return True

def setup_guide():
    """Display setup guide"""
    print("""
🚀 Reddit Persona Analyzer Setup Guide

1. REDDIT API SETUP:
   - Go to https://www.reddit.com/prefs/apps
   - Click "Create App" or "Create Another App"
   - Fill in the form:
     * Name: PersonaAnalyzer
     * App type: Script
     * Description: User persona analysis tool
     * About URL: (leave blank)
     * Redirect URI: http://localhost:8080
   - Click "Create app"
   - Note down the Client ID (under the app name) and Client Secret

2. GROQ API SETUP:
   - Go to https://console.groq.com/
   - Sign up/login with your account
   - Navigate to API Keys section
   - Generate a new API key
   - Copy the API key

3. CONFIGURE CREDENTIALS:
   
   Option A - Environment Variables (Recommended):
   export REDDIT_CLIENT_ID="your_client_id_here"
   export REDDIT_CLIENT_SECRET="your_client_secret_here"
   export GROQ_API_KEY="your_groq_api_key_here"
   
   Option B - Edit Script Directly:
   Update the constants at the top of the script:
   REDDIT_CLIENT_ID = "your_client_id_here"
   REDDIT_CLIENT_SECRET = "your_client_secret_here"
   GROQ_API_KEY = "your_groq_api_key_here"

4. INSTALL DEPENDENCIES:
   pip install praw requests

5. TEST THE SETUP:
   python persona_analyzer.py --help

📋 USAGE EXAMPLES:

Basic analysis:
  python persona_analyzer.py spez

With custom limit:
  python persona_analyzer.py spez --limit 200

Save to specific file:
  python persona_analyzer.py spez --output my_analysis.json

Analyze from URL:
  python persona_analyzer.py https://www.reddit.com/user/spez

Quiet mode:
  python persona_analyzer.py spez --quiet

📊 OUTPUT:
- Detailed persona report displayed in terminal
- JSON file with complete analysis data
- Citations and supporting evidence for each characteristic

⚠️ IMPORTANT NOTES:
- Respect Reddit's API rate limits
- Only analyze public profiles
- Use responsibly and ethically
- The tool analyzes public data only

🔧 TROUBLESHOOTING:
- If Reddit API fails: Check credentials and rate limits
- If Groq API fails: Check API key and quota
- If user not found: Verify username/URL is correct
- If analysis fails: Try with lower limit or different user

For more help, check the script's error messages and validation output.
""")

def interactive_setup():
    """Interactive setup wizard"""
    print("🧙 Interactive Setup Wizard\n")
    
    # Check if credentials are already set
    if (REDDIT_CLIENT_ID and REDDIT_CLIENT_ID != 'YOUR_REDDIT_CLIENT_ID' and
        REDDIT_CLIENT_SECRET and REDDIT_CLIENT_SECRET != 'YOUR_REDDIT_CLIENT_SECRET' and
        GROQ_API_KEY and GROQ_API_KEY != 'YOUR_GROQ_API_KEY'):
        print("✅ Credentials already configured!")
        return
    
    print("Let's set up your API credentials:\n")
    
    # Reddit API setup
    print("1. Reddit API Setup:")
    print("   Visit: https://www.reddit.com/prefs/apps")
    print("   Create a new 'script' application")
    
    client_id = input("\nEnter your Reddit Client ID: ").strip()
    client_secret = input("Enter your Reddit Client Secret: ").strip()
    
    # Groq API setup
    print("\n2. Groq API Setup:")
    print("   Visit: https://console.groq.com/")
    print("   Generate a new API key")
    
    groq_key = input("\nEnter your Groq API Key: ").strip()
    
    # Generate environment variable commands
    print("\n🔧 Add these to your environment (.bashrc, .zshrc, etc.):")
    print(f'export REDDIT_CLIENT_ID="{client_id}"')
    print(f'export REDDIT_CLIENT_SECRET="{client_secret}"')
    print(f'export GROQ_API_KEY="{groq_key}"')
    
    print("\nOr restart this script after setting the environment variables.")

if __name__ == "__main__":
    # Check if this is a setup request
    if len(sys.argv) > 1 and sys.argv[1] in ['--setup', 'setup']:
        setup_guide()
        sys.exit(0)
    
    if len(sys.argv) > 1 and sys.argv[1] in ['--interactive-setup', 'interactive']:
        interactive_setup()
        sys.exit(0)
    
    # Validate environment before running
    if not validate_environment():
        print("\n💡 Run with --setup for detailed setup instructions")
        print("💡 Run with --interactive-setup for guided setup")
        sys.exit(1)
    
    # Run main program
    main()