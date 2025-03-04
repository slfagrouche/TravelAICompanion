from typing import List
from firecrawl import FirecrawlApp
import logging
from datetime import datetime
from pydantic import BaseModel, Field
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SafetyAlertSchema(BaseModel):
    dangerous_news_and_safety_alert: str = Field(
        description="A clear description of the safety alert, emergency, or dangerous situation"
    )
    date: str = Field(
        description="The date when this alert was published"
    )
    link: str = Field(
        description="Source link of this news"
    )

class SafetyMonitor:
    """Class to monitor and analyze safety alerts for locations using Firecrawl LLM Extract"""

    def __init__(self, api_key: str):
        """Initialize the SafetyMonitor"""
        if not api_key:
            raise ValueError("Firecrawl API key is required")
        self.app = FirecrawlApp(api_key=api_key)

    def fetch_safety_alerts(self, destination: str, min_alerts: int = 3) -> List[dict]:
        """
        Fetch and extract safety alerts for a given destination using Firecrawl LLM Extract
        
        Args:
            destination: Location to check for alerts
            min_alerts: Minimum number of alerts to fetch (default: 3)
        """
        alerts = []
        search_terms = [
            f"{destination} emergency alert news",
            f"{destination} safety warning",
            f"{destination} travel warning",
            f"{destination} crisis news",
            f"{destination} security alert"
        ]
        
        try:
            for search_term in search_terms:
                if len(alerts) >= min_alerts:
                    break
                    
                try:
                    # Add system prompt to guide extraction
                    system_prompt = """
                    Extract only recent and relevant safety alerts. Ensure:
                    1. Links are complete, direct URLs to news articles
                    2. Dates are in a clear format
                    3. Alerts are genuinely safety-related
                    4. No duplicate alerts
                    """
                    
                    scrape_result = self.app.scrape_url(
                        f"https://news.google.com/search?q={search_term}",
                        {
                            'formats': ['extract'],
                            'extract': {
                                'schema': SafetyAlertSchema.model_json_schema(),
                                'systemPrompt': system_prompt
                            }
                        }
                    )
                    
                    if scrape_result and "extract" in scrape_result:
                        new_alert = scrape_result["extract"]
                        
                        # Check for duplicates
                        if not any(
                            existing["dangerous_news_and_safety_alert"] == new_alert["dangerous_news_and_safety_alert"]
                            for existing in alerts
                        ):
                            alerts.append(new_alert)
                    
                    # Brief pause between requests
                    time.sleep(1)
                    
                except Exception as e:
                    logger.warning(f"Error processing search term '{search_term}': {str(e)}")
                    continue
                            
        except Exception as e:
            logger.error(f"Error fetching alerts for {destination}: {str(e)}")
            raise
            
        return alerts

def main(): 
    """Main function to run the safety monitoring system"""
    try:
        api_key = "***"  # Replace with your API key
        monitor = SafetyMonitor(api_key)
        
        while True:
            destination = input("\nEnter destination address (or 'quit' to exit): ").strip()
            
            if destination.lower() == 'quit':
                break
                
            if not destination:
                print("Please enter a valid destination.")
                continue
                
            print(f"\nChecking safety alerts for {destination}...")
            try:
                alerts = monitor.fetch_safety_alerts(destination)
                
                if alerts:
                    print(f"\nFound {len(alerts)} safety alert(s):")
                    for idx, alert in enumerate(alerts, 1):
                        print(f"\nAlert {idx}:")
                        print(f"Date: {alert.get('date', 'N/A')}")
                        print(f"Alert: {alert.get('dangerous_news_and_safety_alert', 'N/A')}")
                        print(f"Source: {alert.get('link', 'N/A')}")
                        print("-" * 80)
                else:
                    print(f"No immediate safety alerts found for {destination}.")
                    print("Note: Please always check official travel advisories for the most up-to-date information.")
                    
            except Exception as e:
                print(f"Error checking alerts: {str(e)}")
                print("Please try again or check official travel advisory websites.")
                
    except KeyboardInterrupt:
        print("\nExiting safely...")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        print("An error occurred. Please check the logs for details.")

if __name__ == "__main__":
    main()