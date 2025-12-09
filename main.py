# filename: main.py
from data_loader import load_and_clean_data
from eda import perform_eda
from visualizer import generate_visualizations
from interactive_dashboard import generate_interactive_dashboard

def main():
    print("Starting 'Financing the Future' Pipeline...")
    df = load_and_clean_data()
    
    if not df.empty:
        perform_eda(df)
        generate_visualizations(df)
        generate_interactive_dashboard(df)
        print("\nPipeline Complete. Check the /figures directory.")
    else:
        print("Error: Dataset empty or not found.")

if __name__ == "__main__":
    main()