# filename: main.py
from data_loader import load_and_clean_data
from eda import perform_eda
from visualizer import generate_visualizations
from interactive_dashboard import generate_interactive_dashboard

def main():
    print("Starting 'Financing the Future' Analysis Pipeline...")
    
    # 1. Load Data
    df = load_and_clean_data()
    
    if not df.empty:
        # 2. Run EDA (Economic & Transition Focus)
        perform_eda(df)
        
        # 3. Generate Static Visuals (Funding, Kuznets, Mix)
        generate_visualizations(df)
        
        # 4. Generate Interactive Dashboard
        generate_interactive_dashboard(df)
        
        print("\nPipeline Complete. Check 'figures/' for your report assets.")
    else:
        print("Pipeline aborted due to missing data.")

if __name__ == "__main__":
    main()