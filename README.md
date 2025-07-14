
# Reddit User Persona Analyzer

A Python tool that analyzes Reddit user profiles to generate detailed user personas based on their posts, comments, and activity patterns. The tool uses Reddit's API to scrape user content and leverages Groq's LLM API to generate comprehensive persona reports with supporting evidence and citations.

## Features

- 🔍 **Comprehensive Profile Analysis**: Scrapes posts, comments, and activity patterns
- 🧠 **AI-Powered Persona Generation**: Uses Groq LLM for intelligent analysis
- 📊 **Visual Data Representation**: ASCII charts for personality traits and motivations
- 📝 **Detailed Reports**: Complete persona profiles with citations and evidence
- 🔗 **Citation Support**: Links back to original posts/comments for verification
- 📈 **Activity Pattern Analysis**: Subreddit preferences, posting frequency, and engagement metrics

## Prerequisites

- Python 3.7+
- Reddit API credentials
- Groq API key
- Internet connection

## Installation

1. **Clone or download the script**
   ```bash
   git clone <repository-url>
   cd reddit-persona-analyzer
   ```

2. **Install required packages**
   ```bash
   pip install praw requests python-dotenv
   ```

3. **Create environment file**
   ```bash
   cp .env.example .env
   ```

4. **Set up API credentials** (see Configuration section below)

## Configuration

### Reddit API Setup

1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Fill in the form:
   - **Name**: Your app name
   - **App type**: Select "script"
   - **Description**: Optional
   - **About URL**: Optional
   - **Redirect URI**: `http://localhost:8080`
4. Note your **Client ID** (under the app name) and **Client Secret**

### Groq API Setup

1. Visit [Groq Console](https://console.groq.com/)
2. Sign up or log in
3. Generate an API key
4. Copy the API key

### Environment Configuration

1. **Create a `.env` file** in the project root directory:
   ```bash
   touch .env
   ```

2. **Add your API credentials** to the `.env` file:
   ```env
   # Reddit API Credentials
   REDDIT_CLIENT_ID=your_reddit_client_id_here
   REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
   REDDIT_USER_AGENT=PersonaAnalyzer/1.0

   # Groq API Credentials
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. **Keep `.env` secure**:
   - Never commit `.env` to version control
   - Add `.env` to your `.gitignore` file
   - Use different `.env` files for different environments

### Example .env File

Create a `.env.example` file for reference:
```env
# Reddit API Credentials
REDDIT_CLIENT_ID=your_reddit_client_id_here
REDDIT_CLIENT_SECRET=your_reddit_client_secret_here
REDDIT_USER_AGENT=PersonaAnalyzer/1.0

# Groq API Credentials
GROQ_API_KEY=your_groq_api_key_here
```

### Security Best Practices

- **Never share your `.env` file** or commit it to version control
- **Use strong, unique API keys** for each environment
- **Rotate API keys regularly** for security
- **Set appropriate file permissions** on your `.env` file:
  ```bash
  chmod 600 .env
  ```

## Usage

### Quick Start

1. **Basic Analysis**
   ```bash
   python reddit_persona_analyzer.py <username>
   ```

2. **The script will:**
   - Scrape the user's recent posts and comments
   - Analyze activity patterns across subreddits
   - Generate AI-powered persona insights
   - Create a detailed report with citations
   - Save the report to a text file

### Command Line Interface

```bash
python reddit_persona_analyzer.py <profile_url_or_username> [-o output_file]
```

**Arguments:**
- `profile_url_or_username`: Reddit username or full profile URL
- `-o, --output`: Optional custom output file path

### Detailed Examples

```bash
# Analyze a user by username (simplest method)
python reddit_persona_analyzer.py spez

# Analyze using full Reddit URL
python reddit_persona_analyzer.py https://www.reddit.com/user/spez
python reddit_persona_analyzer.py https://reddit.com/u/spez

# Specify custom output file
python reddit_persona_analyzer.py spez -o spez_analysis.txt

# Analyze multiple users (run separately)
python reddit_persona_analyzer.py user1 -o user1_report.txt
python reddit_persona_analyzer.py user2 -o user2_report.txt
```

### Step-by-Step Process

When you run the script, it follows this process:

1. **Username Extraction**: Parses the input to extract the Reddit username
2. **Content Scraping**: Fetches up to 200 recent posts and comments
3. **Activity Analysis**: Analyzes subreddit preferences, posting patterns, and engagement
4. **AI Processing**: Uses Groq LLM to generate persona insights
5. **Evidence Gathering**: Finds supporting citations for each characteristic
6. **Report Generation**: Creates a comprehensive markdown-formatted report
7. **File Output**: Saves the report to `{username}_persona_report.txt` (or custom filename)

### What You'll See During Execution

```
Analyzing user: spez
Scraping user content...
Analyzing activity patterns...
Generating persona with Groq LLM...
Finding supporting evidence...
Generating report...
Report saved to: spez_persona_report.txt

==================================================
ANALYSIS COMPLETE!
==================================================
Report saved to: spez_persona_report.txt
Username analyzed: spez

==================================================
REPORT PREVIEW:
==================================================
# User Persona Report: spez

**Analysis Date:** 2024-01-15T14:30:00

## Basic Information

**AGE:** 35-40
**OCCUPATION:** Technology Executive
**STATUS:** Married
**LOCATION:** San Francisco, CA
**TIER:** Power User
**ARCHETYPE:** The Leader
...
```

### Programmatic Usage

For integration into other projects:

```python
from reddit_persona_analyzer import RedditPersonaAnalyzer

# Initialize analyzer
analyzer = RedditPersonaAnalyzer()

try:
    # Analyze user and get report
    report = analyzer.analyze_user("spez", "spez_analysis.txt")
    print("Analysis complete!")
    print(report[:500] + "...")
    
except Exception as e:
    print(f"Error: {e}")
```

### Advanced Usage

**Custom Content Limits:**
```python
# Modify the script to analyze more content
content = analyzer.scrape_user_content("username", limit=500)
```

**Access Raw Data:**
```python
# Get the structured persona object
persona = analyzer.generate_persona_with_llm(content, activity_patterns)
print(f"User archetype: {persona.archetype}")
print(f"Interests: {persona.interests}")
```

### Input Formats Supported

The tool accepts various input formats:
- `username` → Plain username
- `https://www.reddit.com/user/username` → Full profile URL
- `https://reddit.com/u/username` → Short profile URL
- `www.reddit.com/user/username` → URL without protocol

## Sample Output

The tool generates comprehensive persona reports including:

### Basic Demographics
- Age estimation
- Likely occupation
- Relationship status
- Location
- User tier/archetype

### Personality Traits
Visual sliders showing:
- Introvert ←→ Extrovert
- Intuition ←→ Sensing  
- Feeling ←→ Thinking
- Perceiving ←→ Judging

### Motivations
Bar charts displaying motivation levels for:
- Convenience
- Wellness
- Social connection
- Achievement
- Learning
- And more...

### Behavioral Analysis
- Habits and patterns
- Frustrations and pain points
- Goals and needs
- Representative quotes
- Interests and brand preferences

### Supporting Evidence
- Citations with links to original posts/comments
- Confidence scores for each trait
- Activity patterns and statistics

## Error Handling

The script includes robust error handling for:
- Invalid usernames or URLs
- Private/restricted profiles
- API rate limiting
- Network connectivity issues
- Malformed API responses

## Limitations

- **Rate Limits**: Reddit API has rate limits (60 requests per minute)
- **Private Profiles**: Cannot analyze private or suspended accounts
- **Content Limits**: Analyzes up to 200 recent posts/comments by default
- **API Dependencies**: Requires active Reddit and Groq API keys

## Troubleshooting

### Common Issues

1. **"User not found"**
   - Check if the username exists
   - Verify the user hasn't been suspended
   - Ensure the profile is public

2. **API Authentication Errors**
   - Verify your Reddit API credentials
   - Check your Groq API key is valid
   - Ensure you have sufficient API quota

3. **Network/Connection Issues**
   - Check your internet connection
   - Verify API endpoints are accessible
   - Consider firewall/proxy settings

4. **Empty Analysis**
   - User might have very recent account with no content
   - Content might be in private subreddits
   - Try increasing the content limit

### Getting Help

If you encounter issues:
1. Check the error message for specific details
2. Verify your API credentials are correct
3. Test with a well-known public user (e.g., "spez")
4. Check Reddit and Groq service status

## Data Privacy

- **No Data Storage**: The tool doesn't store user data permanently
- **Public Content Only**: Only analyzes publicly available Reddit content
- **Respectful Usage**: Please use responsibly and respect user privacy
- **Rate Limiting**: Built-in delays to respect API limits

## Contributing

Contributions are welcome! Areas for improvement:
- Additional personality frameworks
- Enhanced visualization options
- More sophisticated NLP analysis
- Export formats (JSON, CSV, etc.)
- Web interface

## License

This project is provided as-is for educational and research purposes. Please ensure you comply with Reddit's API Terms of Service and respect user privacy.

## Disclaimer

This tool is for educational and research purposes only. The generated personas are AI-generated interpretations based on public Reddit activity and should not be considered definitive psychological profiles. Always respect user privacy and use this tool responsibly.

## Dependencies

- `praw`: Reddit API wrapper
- `requests`: HTTP library for API calls
- `python-dotenv`: Environment variable management
- `json`: JSON data handling
- `re`: Regular expressions
- `datetime`: Date/time handling
- `dataclasses`: Data structure definitions
- `collections`: Counter for frequency analysis
- `argparse`: Command-line argument parsing
