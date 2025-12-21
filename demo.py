"""
DataPolish - Comprehensive Demo Script
Demonstrates all features of the DataPolish library
"""

from datapolish import DataCleaner

print("=" * 80)
print("DataPolish - AI-Powered Data Cleaning Demo")
print("=" * 80)

# Load data
print("\n1. Loading data...")
cleaner = DataCleaner("medical_patient_data.csv")
print(f"   ✓ Loaded {cleaner.df.shape[0]} rows, {cleaner.df.shape[1]} columns")

# AI Description
print("\n" + "=" * 80)
print("2. AI-Powered Data Description")
print("=" * 80)
print(cleaner.describe_data(detail_level=0))

# Recommendations
print("\n" + "=" * 80)
print("3. Intelligent Recommendations")
print("=" * 80)
print(cleaner.get_recommendations())

# Profile
print("\n" + "=" * 80)
print("4. Data Profiling")
print("=" * 80)
profile = cleaner.profile()
print(f"Quality Score: {profile['quality_score']}/100")
print(f"Missing Values: {len(profile['missing_values'])} columns affected")
print(f"Duplicates: {profile['duplicates']} records")
print(f"Outliers: {profile['outliers']} detected")

# Drop columns
print("\n" + "=" * 80)
print("5. Drop Columns (NEW Feature!)")
print("=" * 80)
dropped = cleaner.drop_columns('Patient_ID', 'Admission_Date')
print(f"   ✓ Dropped {len(dropped)} columns: {dropped}")

# Correlation analysis
print("\n" + "=" * 80)
print("6. Correlation Analysis (NEW Feature!)")
print("=" * 80)
result = cleaner.analyze_correlation('Systolic_BP', 'Diastolic_BP')
print(f"   Correlation: {result['correlation_value']:.4f}")
print(f"   Strength: {result['strength']}")
print(f"   Direction: {result['direction']}")

# View as image
print("\n" + "=" * 80)
print("7. View as Image (NEW Feature!)")
print("=" * 80)
cleaner.view_as_image(rows=10, save_path='preview.png', title='First 10 Records')
print("   ✓ Saved preview.png")
cleaner.view_as_image(rows=-10, save_path='tail.png', title='Last 10 Records')
print("   ✓ Saved tail.png")

# Visualizations
print("\n" + "=" * 80)
print("8. Professional Visualizations")
print("=" * 80)
cleaner.visualize('overview', save_path='dashboard.png')
print("   ✓ Saved dashboard.png")
cleaner.visualize('missing', save_path='missing_values.png')
print("   ✓ Saved missing_values.png")

# Clean data
print("\n" + "=" * 80)
print("9. Cleaning Data")
print("=" * 80)
config = {
    'missing': {'strategy': 'median'},
    'outliers': {'method': 'iqr', 'action': 'cap'},
    'duplicates': {'drop': True}
}
cleaner.clean(config)
print("   ✓ Cleaning completed")

# Explanation
print("\n" + "=" * 80)
print("10. Cleaning Explanation")
print("=" * 80)
print(cleaner.explain_cleaning('summary'))

# Save
print("\n" + "=" * 80)
print("11. Saving Cleaned Data")
print("=" * 80)
saved_path = cleaner.save()
print(f"   ✓ Saved to: {saved_path}")

print("\n" + "=" * 80)
print("✅ Demo Complete!")
print("=" * 80)
print("\nDataPolish successfully cleaned your data!")
print("Check the output files:")
print("  - preview.png")
print("  - tail.png") 
print("  - dashboard.png")
print("  - missing_values.png")
print(f"  - {saved_path}")
