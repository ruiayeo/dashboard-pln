#!/usr/bin/env python3
"""
Test script untuk validate data sebelum jalankan dashboard
Run: python test_data.py
"""

import sys
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.data_loader import load_and_clean_data, get_data_summary
from modules.metrics import calculate_ranking, calculate_time_metrics


def test_data_loading():
    """Test data loading dan cleaning"""
    print("\n" + "="*80)
    print("🔍 TEST 1: Data Loading & Cleaning")
    print("="*80)
    
    try:
        df = load_and_clean_data()
        print("✅ Data loaded successfully!\n")
        
        # Display summary
        summary = get_data_summary(df)
        print("📊 Data Summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        print(f"\n📋 Columns: {list(df.columns)}")
        print(f"\n🔢 Data Shape: {df.shape}")
        
        return df
    
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return None


def test_data_quality(df):
    """Test data quality"""
    print("\n" + "="*80)
    print("🔍 TEST 2: Data Quality Check")
    print("="*80)
    
    issues = []
    
    # Check missing values
    print("\n📍 Missing Values:")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(missing[missing > 0])
    else:
        print("   ✅ No missing values")
    
    # Check petugas
    print("\n👥 Petugas Check:")
    unique_petugas = df['kd_petugas'].nunique()
    print(f"   Unique petugas: {unique_petugas}")
    print(f"   Sample petugas: {df['kd_petugas'].unique()[:5]}")
    
    if unique_petugas < 2:
        issues.append("⚠️  Kurang dari 2 petugas (minimum untuk analisis)")
    
    # Check waktu
    print("\n⏰ Waktu Check:")
    print(f"   Range jam: {df['jam_pembacaan_menit'].min()} - {df['jam_pembacaan_menit'].max()}")
    print(f"   (Jam {df['jam_pembacaan_menit'].min() // 60}:{df['jam_pembacaan_menit'].min() % 60:02d} - {df['jam_pembacaan_menit'].max() // 60}:{df['jam_pembacaan_menit'].max() % 60:02d})")
    
    print(f"   Date range: {df['tanggal_pembacaan'].min()} - {df['tanggal_pembacaan'].max()}")
    
    # Check shift distribution
    print("\n🌅 Shift Distribution:")
    for shift in ['Pagi (06-11)', 'Siang (11-16)', 'Sore (16-21)', 'Malam (21-06)']:
        count = len(df[df['shift'] == shift])
        pct = count / len(df) * 100
        print(f"   {shift}: {count} ({pct:.1f}%)")
    
    # Check koordinat
    print("\n📍 Geografis Check:")
    print(f"   X range: {df['koordinat_x'].min():.4f} - {df['koordinat_x'].max():.4f}")
    print(f"   Y range: {df['koordinat_y'].min():.4f} - {df['koordinat_y'].max():.4f}")
    
    # Check meter reading values
    print("\n📊 Meter Reading Check:")
    print(f"   Stand Baca: {df['stand_baca'].min()} - {df['stand_baca'].max()}")
    print(f"   PEMKWH: {df['pemkwh'].min():.0f} - {df['pemkwh'].max():.0f}")
    
    return issues


def test_ranking_calculation(df):
    """Test ranking calculation"""
    print("\n" + "="*80)
    print("🔍 TEST 3: Ranking Calculation")
    print("="*80)
    
    try:
        # Use default weights
        weights = {
            'total_pembacaan': 0.35,
            'konsistensi_waktu': 0.30,
            'efisiensi_area': 0.20,
            'kecepatan_pembacaan': 0.15
        }
        
        ranking_df = calculate_ranking(df, weights)
        
        print(f"\n✅ Ranking calculated for {len(ranking_df)} petugas\n")
        print("Top 5 Ranking:")
        print(ranking_df[['rank', 'kd_petugas', 'total_pembacaan', 'ranking_score']].head().to_string(index=False))
        
        return ranking_df
    
    except Exception as e:
        print(f"❌ Error calculating ranking: {e}")
        return None


def test_time_metrics(df):
    """Test time metrics calculation"""
    print("\n" + "="*80)
    print("🔍 TEST 4: Time Metrics")
    print("="*80)
    
    try:
        metrics = calculate_time_metrics(df)
        
        print("\n✅ Time metrics calculated\n")
        print(metrics.to_string(index=False))
        
    except Exception as e:
        print(f"❌ Error calculating time metrics: {e}")


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "PLN DASHBOARD - DATA VALIDATION TEST" + " "*23 + "║")
    print("╚" + "="*78 + "╝")
    
    # Test 1: Load data
    df = test_data_loading()
    if df is None:
        print("\n❌ Cannot proceed - data loading failed")
        return
    
    # Test 2: Data quality
    issues = test_data_quality(df)
    
    # Test 3: Ranking
    ranking_df = test_ranking_calculation(df)
    
    # Test 4: Metrics
    test_time_metrics(df)
    
    # Summary
    print("\n" + "="*80)
    print("📋 TEST SUMMARY")
    print("="*80)
    
    if ranking_df is None:
        print("❌ FAILED - See errors above")
    else:
        print("✅ ALL TESTS PASSED!")
        print("\n✅ Data ready to use in dashboard")
        print("\n🚀 Next step: streamlit run dashboard.py")
    
    if issues:
        print("\n⚠️  WARNINGS:")
        for issue in issues:
            print(f"   {issue}")
    
    print("\n" + "="*80 + "\n")


if __name__ == '__main__':
    main()
