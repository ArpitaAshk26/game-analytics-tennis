import pandas as pd
from .api_client import SportRadarClient

class RankingsExtractor:
    def __init__(self):
        self.client = SportRadarClient()
        
    def extract_and_transform(self):
        """
        Extract rankings data
        Returns: (competitors_df, rankings_df)
        """
        print("Fetching rankings data...")
        data = self.client.get_rankings()
        
        competitors_list = []
        rankings_list = []
        
        # The API returns a list of ranking types (ATP, WTA, etc.)
        if 'rankings' in data:
            for ranking_type in data['rankings']:
                # Each ranking type has competitor_rankings
                if 'competitor_rankings' in ranking_type:
                    for ranking in ranking_type['competitor_rankings']:
                        if 'competitor' in ranking:
                            competitor = ranking['competitor']
                            
                            # Extract competitor
                            competitors_list.append({
                                'competitor_id': competitor.get('id'),
                                'name': competitor.get('name'),
                                'country': competitor.get('country'),
                                'country_code': competitor.get('country_code'),
                                'abbreviation': competitor.get('abbreviation', 'N/A')
                            })
                            
                            # Extract ranking
                            rankings_list.append({
                                'rank': ranking.get('rank'),
                                'movement': ranking.get('movement', 0),
                                'points': ranking.get('points'),
                                'competitions_played': ranking.get('competitions_played', 0),
                                'competitor_id': competitor.get('id')
                            })
        
        competitors_df = pd.DataFrame(competitors_list).drop_duplicates(subset=['competitor_id'])
        rankings_df = pd.DataFrame(rankings_list)
        
        print(f"Extracted {len(competitors_df)} competitors")
        print(f"Extracted {len(rankings_df)} rankings")
        
        return competitors_df, rankings_df