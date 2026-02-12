import pandas as pd
from .api_client import SportRadarClient  # Changed: added dot for relative import

class ComplexExtractor:
    def __init__(self):
        self.client = SportRadarClient()
        
    def extract_and_transform(self):
        """
        Extract complexes and venues data
        Returns: (complexes_df, venues_df)
        """
        print("Fetching complexes data...")
        data = self.client.get_complexes()
        
        complexes_list = []
        venues_list = []
        
        if 'complexes' in data:
            for complex_item in data['complexes']:
                # Extract complex
                complexes_list.append({
                    'complex_id': complex_item.get('id'),
                    'complex_name': complex_item.get('name')
                })
                
                # Extract venues
                if 'venues' in complex_item:
                    for venue in complex_item['venues']:
                        venues_list.append({
                            'venue_id': venue.get('id'),
                            'venue_name': venue.get('name'),
                            'city_name': venue.get('city_name'),
                            'country_name': venue.get('country_name'),
                            'country_code': venue.get('country_code'),
                            'timezone': venue.get('timezone'),
                            'complex_id': complex_item.get('id')
                        })
        
        complexes_df = pd.DataFrame(complexes_list)
        venues_df = pd.DataFrame(venues_list)
        
        print(f"Extracted {len(complexes_df)} complexes")
        print(f"Extracted {len(venues_df)} venues")
        
        return complexes_df, venues_df