import pandas as pd
from .api_client import SportRadarClient  # Changed: added dot for relative import

class CompetitionExtractor:
    def __init__(self):
        self.client = SportRadarClient()
        
    def extract_and_transform(self):
        """
        Extract competitions data and transform into DataFrames
        Returns: (categories_df, competitions_df)
        """
        print("Fetching competitions data...")
        data = self.client.get_competitions()
        
        categories_list = []
        competitions_list = []
        
        # Parse competitions
        if 'competitions' in data:
            for comp in data['competitions']:
                # Extract category
                if 'category' in comp:
                    category = comp['category']
                    categories_list.append({
                        'category_id': category.get('id'),
                        'category_name': category.get('name')
                    })
                
                # Extract competition
                competitions_list.append({
                    'competition_id': comp.get('id'),
                    'competition_name': comp.get('name'),
                    'parent_id': comp.get('parent_id'),
                    'type': comp.get('type'),
                    'gender': comp.get('gender'),
                    'category_id': comp.get('category', {}).get('id')
                })
        
        # Create DataFrames
        categories_df = pd.DataFrame(categories_list).drop_duplicates(subset=['category_id'])
        competitions_df = pd.DataFrame(competitions_list)
        
        print(f"Extracted {len(categories_df)} categories")
        print(f"Extracted {len(competitions_df)} competitions")
        
        return categories_df, competitions_df