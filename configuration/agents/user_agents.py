import requests
import random
import json
import os
from datetime import datetime, timedelta

def fetch_user_agents():
    """Fetch latest user agents from useragentstring.com"""
    try:
        response = requests.get('https://www.useragentstring.com/pages/useragentstring.php?name=Chrome')
        if response.status_code == 200:
            # Parse and extract user agents
            agents = response.text.split('\n')
            # Filter for recent Chrome versions
            chrome_agents = [a for a in agents if 'Chrome' in a and not 'Mobile' in a]
            return chrome_agents
    except:
        return None

def fetch_mobile_agents():
    """Fetch latest mobile user agents"""
    try:
        response = requests.get('https://www.useragentstring.com/pages/useragentstring.php?name=Mobile%20Browser')
        if response.status_code == 200:
            agents = response.text.split('\n')
            # Filter for iOS devices
            ios_agents = [a for a in agents if 'iPhone' in a or 'iPad' in a]
            return ios_agents
    except:
        return None

def get_user_agents(mobile=False):
    """Get user agents from cache or fetch new ones"""
    cache_file = 'mobile_agents.json' if mobile else 'desktop_agents.json'
    
    # Check if cache exists and is less than 7 days old
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            data = json.load(f)
            last_updated = datetime.fromisoformat(data['updated'])
            if datetime.now() - last_updated < timedelta(days=7):
                return data['agents']
    
    # Fetch new agents
    agents = fetch_mobile_agents() if mobile else fetch_user_agents()
    
    # Fall back to default agents if fetch fails
    if not agents:
        if mobile:
            agents = [
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
            ]
        else:
            agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
            ]
    
    # Save to cache
    with open(cache_file, 'w') as f:
        json.dump({
            'updated': datetime.now().isoformat(),
            'agents': agents
        }, f)
    
    return agents

def get_random_agent(mobile=False):
    """Get a random user agent"""
    agents = get_user_agents(mobile)
    return random.choice(agents)
