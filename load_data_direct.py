import pandas as pd
from database.db_connection import DatabaseConnection
from data_extraction.extract_competitions import CompetitionExtractor
from data_extraction.extract_complexes import ComplexExtractor
from data_extraction.extract_rankings import RankingsExtractor

class DirectDataLoader:
    def __init__(self):
        self.db = DatabaseConnection()
        
    def insert_dataframe(self, df, table_name, conn):
        """Insert DataFrame using direct SQL INSERT statements"""
        cursor = conn.cursor()
        
        # Get column names
        columns = ', '.join(df.columns)
        placeholders = ', '.join(['?' for _ in df.columns])
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        
        # Insert rows
        for index, row in df.iterrows():
            cursor.execute(insert_sql, tuple(row))
            if (index + 1) % 500 == 0:
                print(f"  Inserted {index + 1}/{len(df)} rows...")
        
        conn.commit()
        print(f"✓ Inserted {len(df)} rows into {table_name}")
    
    
    def insert_competitions_hierarchical(self, competitions_df, conn):
        """Insert competitions in correct hierarchical order"""
        cursor = conn.cursor()
        
        # Get all valid competition IDs in the dataset
        valid_ids = set(competitions_df['competition_id'].unique())
        
        # Separate into those with and without parents
        no_parent = competitions_df[competitions_df['parent_id'].isna()].copy()
        has_parent = competitions_df[competitions_df['parent_id'].notna()].copy()
        
        # Filter children: only keep those whose parent exists in the dataset
        valid_children = has_parent[has_parent['parent_id'].isin(valid_ids)].copy()
        invalid_children = has_parent[~has_parent['parent_id'].isin(valid_ids)].copy()
        
        print(f"  Found {len(no_parent)} top-level competitions")
        print(f"  Found {len(valid_children)} child competitions (parent in dataset)")
        print(f"  Found {len(invalid_children)} competitions with external parent references")
        
        # Step 1: Insert all top-level competitions
        print("\n  Inserting top-level competitions...")
        self.insert_dataframe(no_parent, 'Competitions', conn)
        
        # Step 2: Insert children iteratively in hierarchical order
        if len(valid_children) > 0:
            print(f"\n  Inserting {len(valid_children)} child competitions...")
            remaining = valid_children.copy()
            inserted_ids = set(no_parent['competition_id'].values)
            iteration = 1
            
            while len(remaining) > 0:
                can_insert = remaining[remaining['parent_id'].isin(inserted_ids)].copy()
                
                if len(can_insert) == 0:
                    print(f"\n  ⚠ Remaining {len(remaining)} competitions have circular references")
                    # Insert them with NULL parent_id
                    remaining['parent_id'] = None
                    self.insert_dataframe(remaining, 'Competitions', conn)
                    break
                
                columns = ', '.join(can_insert.columns)
                placeholders = ', '.join(['?' for _ in can_insert.columns])
                insert_sql = f"INSERT INTO Competitions ({columns}) VALUES ({placeholders})"
                
                for index, row in can_insert.iterrows():
                    cursor.execute(insert_sql, tuple(row))
                
                conn.commit()
                inserted_ids.update(can_insert['competition_id'].values)
                remaining = remaining[~remaining['competition_id'].isin(can_insert['competition_id'])].copy()
                iteration += 1
        
        # Step 3: Handle competitions with external parent references
        if len(invalid_children) > 0:
            print(f"\n  Note: {len(invalid_children)} competitions reference archived/external parents")
            print(f"  Inserting with parent_id set to NULL...")
            invalid_children['parent_id'] = None
            self.insert_dataframe(invalid_children, 'Competitions', conn)









    
    def load_all_data(self):
        """
        Extract data from API and load into MSSQL database
        """
        conn = self.db.get_pyodbc_connection()
        
        try:
            # 1. Load Competitions Data
            print("\n" + "="*60)
            print("=== Loading Competitions Data ===")
            print("="*60)
            comp_extractor = CompetitionExtractor()
            categories_df, competitions_df = comp_extractor.extract_and_transform()
            
            # Insert categories
            self.insert_dataframe(categories_df, 'Categories', conn)
            
            # Insert competitions hierarchically
            self.insert_competitions_hierarchical(competitions_df, conn)
            
            # 2. Load Complexes Data
            print("\n" + "="*60)
            print("=== Loading Complexes Data ===")
            print("="*60)
            complex_extractor = ComplexExtractor()
            complexes_df, venues_df = complex_extractor.extract_and_transform()
            
            self.insert_dataframe(complexes_df, 'Complexes', conn)
            self.insert_dataframe(venues_df, 'Venues', conn)
            
            # 3. Load Rankings Data
            print("\n" + "="*60)
            print("=== Loading Rankings Data ===")
            print("="*60)
            rankings_extractor = RankingsExtractor()
            competitors_df, rankings_df = rankings_extractor.extract_and_transform()
            
            self.insert_dataframe(competitors_df, 'Competitors', conn)
            self.insert_dataframe(rankings_df, 'Competitor_Rankings', conn)
            
            print("\n" + "="*60)
            print("✓✓✓ All data loaded successfully! ✓✓✓")
            print("="*60)
            
            # Print summary
            cursor = conn.cursor()
            print("\n=== Database Summary ===")
            cursor.execute("SELECT COUNT(*) FROM Categories")
            print(f"Categories: {cursor.fetchone()[0]}")
            cursor.execute("SELECT COUNT(*) FROM Competitions")
            print(f"Competitions: {cursor.fetchone()[0]}")
            cursor.execute("SELECT COUNT(*) FROM Complexes")
            print(f"Complexes: {cursor.fetchone()[0]}")
            cursor.execute("SELECT COUNT(*) FROM Venues")
            print(f"Venues: {cursor.fetchone()[0]}")
            cursor.execute("SELECT COUNT(*) FROM Competitors")
            print(f"Competitors: {cursor.fetchone()[0]}")
            cursor.execute("SELECT COUNT(*) FROM Competitor_Rankings")
            print(f"Rankings: {cursor.fetchone()[0]}")
            
        except Exception as e:
            print(f"\n✗ Error loading data: {e}")
            import traceback
            traceback.print_exc()
        finally:
            conn.close()

if __name__ == "__main__":
    loader = DirectDataLoader()
    loader.load_all_data()