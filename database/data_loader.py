import pandas as pd
from db_connection import DatabaseConnection
import sys
import os

# Add parent directory to path to access data_extraction module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data_extraction.extract_competitions import CompetitionExtractor
from data_extraction.extract_complexes import ComplexExtractor
from data_extraction.extract_rankings import RankingsExtractor

class DataLoader:
    def __init__(self):
        self.db = DatabaseConnection()
        
    def load_all_data(self):
        """
        Extract data from API and load into MSSQL database
        """
        engine = self.db.get_sqlalchemy_engine()
        
        try:
            # 1. Load Competitions Data
            print("\n" + "="*60)
            print("=== Loading Competitions Data ===")
            print("="*60)
            comp_extractor = CompetitionExtractor()
            categories_df, competitions_df = comp_extractor.extract_and_transform()
            
            categories_df.to_sql('Categories', engine, if_exists='append', index=False)
            competitions_df.to_sql('Competitions', engine, if_exists='append', index=False)
            print("✓ Competitions loaded successfully")
            
            # 2. Load Complexes Data
            print("\n" + "="*60)
            print("=== Loading Complexes Data ===")
            print("="*60)
            complex_extractor = ComplexExtractor()
            complexes_df, venues_df = complex_extractor.extract_and_transform()
            
            complexes_df.to_sql('Complexes', engine, if_exists='append', index=False)
            venues_df.to_sql('Venues', engine, if_exists='append', index=False)
            print("✓ Complexes loaded successfully")
            
            # 3. Load Rankings Data
            print("\n" + "="*60)
            print("=== Loading Rankings Data ===")
            print("="*60)
            rankings_extractor = RankingsExtractor()
            competitors_df, rankings_df = rankings_extractor.extract_and_transform()
            
            competitors_df.to_sql('Competitors', engine, if_exists='append', index=False)
            rankings_df.to_sql('Competitor_Rankings', engine, if_exists='append', index=False)
            print("✓ Rankings loaded successfully")
            
            print("\n" + "="*60)
            print("✓✓✓ All data loaded successfully! ✓✓✓")
            print("="*60)
            
        except Exception as e:
            print(f"\n✗ Error loading data: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == "__main__":
    loader = DataLoader()
    loader.load_all_data()