"""
Business Analytics Chart Generator for Ipoteka.az Real Estate Data
Generates executive-ready visualizations for strategic decision-making
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import re
import os

# Set style for professional business charts
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 12

# Colors - professional business palette
COLORS = {
    'primary': '#2C3E50',
    'secondary': '#3498DB',
    'accent': '#E74C3C',
    'success': '#27AE60',
    'warning': '#F39C12',
    'info': '#9B59B6',
    'gradient': ['#3498DB', '#2980B9', '#1ABC9C', '#16A085', '#27AE60', '#2ECC71']
}

# Create output directory
OUTPUT_DIR = 'charts'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_and_prepare_data():
    """Load and prepare data for analysis"""
    df = pd.read_csv('29_12_2025.csv')

    # Extract numeric price
    def extract_price(p):
        if pd.isna(p):
            return None
        nums = re.findall(r'[\d\s]+', str(p).replace(' ', ''))
        if nums:
            try:
                return float(nums[0].replace(' ', ''))
            except:
                return None
        return None

    # Extract numeric area
    def extract_area(a):
        if pd.isna(a):
            return None
        nums = re.findall(r'[\d.]+', str(a))
        if nums:
            try:
                return float(nums[0])
            except:
                return None
        return None

    # Extract property type
    def extract_property_type(title):
        if pd.isna(title):
            return 'Other'
        title = str(title)
        if 'Torpaq' in title:
            return 'Land'
        elif 'Villa' in title or 'Evlər' in title:
            return 'House/Villa'
        elif 'Yeni tikili' in title:
            return 'New Building'
        elif 'Köhnə tikili' in title:
            return 'Old Building'
        elif 'Ofis' in title:
            return 'Office'
        elif 'Obyekt' in title:
            return 'Commercial'
        else:
            return 'Other'

    # Extract location
    def extract_location(title):
        if pd.isna(title):
            return 'Other'
        title = str(title)
        locations = {
            'Masazır': 'Masazir',
            'Xırdalan': 'Khirdalan',
            'Saray': 'Saray',
            'Buzovna': 'Buzovna',
            'Sumqayıt': 'Sumgayit',
            'Binəqədi': 'Binagadi',
            'Yasamal': 'Yasamal',
            'Nəsimi': 'Nasimi',
            'Səbail': 'Sabail',
            'Xətai': 'Khatai',
            'Nizami': 'Nizami',
            'Suraxanı': 'Surakhani',
            'Sabunçu': 'Sabunchu',
            'Qaradağ': 'Qaradag',
            'Pirallahı': 'Pirallahi'
        }
        for az_name, en_name in locations.items():
            if az_name in title:
                return en_name
        return 'Other Areas'

    df['price_numeric'] = df['price'].apply(extract_price)
    df['area_numeric'] = df['area'].apply(extract_area)
    df['property_type'] = df['title'].apply(extract_property_type)
    df['location'] = df['title'].apply(extract_location)
    df['price_per_sqm'] = df['price_numeric'] / df['area_numeric']

    return df


def chart_1_market_composition(df):
    """Chart 1: Property Type Market Composition"""
    fig, ax = plt.subplots(figsize=(12, 7))

    type_counts = df['property_type'].value_counts()
    colors = COLORS['gradient'][:len(type_counts)]

    bars = ax.barh(type_counts.index, type_counts.values, color=colors, edgecolor='white', linewidth=1.5)

    # Add value labels
    for bar, val in zip(bars, type_counts.values):
        pct = val / len(df) * 100
        ax.text(val + 20, bar.get_y() + bar.get_height()/2,
                f'{val:,} ({pct:.1f}%)', va='center', fontweight='bold', fontsize=11)

    ax.set_xlabel('Number of Listings', fontweight='bold')
    ax.set_title('Market Composition by Property Type\nTotal Active Listings: {:,}'.format(len(df)),
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(0, max(type_counts.values) * 1.25)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/01_market_composition.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: 01_market_composition.png")


def chart_2_price_distribution(df):
    """Chart 2: Price Range Distribution"""
    fig, ax = plt.subplots(figsize=(12, 7))

    df_valid = df[df['price_numeric'].notna() & (df['price_numeric'] > 0) & (df['price_numeric'] < 2000000)]

    bins = [0, 50000, 100000, 150000, 200000, 300000, 500000, 1000000, 2000000]
    labels = ['<50K', '50-100K', '100-150K', '150-200K', '200-300K', '300-500K', '500K-1M', '1-2M']

    df_valid['price_range'] = pd.cut(df_valid['price_numeric'], bins=bins, labels=labels)
    price_dist = df_valid['price_range'].value_counts().reindex(labels)

    colors = plt.cm.Blues(np.linspace(0.3, 0.9, len(labels)))
    bars = ax.bar(labels, price_dist.values, color=colors, edgecolor='white', linewidth=1.5)

    # Add value labels
    for bar, val in zip(bars, price_dist.values):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2, val + 20,
                    f'{val:,}', ha='center', fontweight='bold', fontsize=10)

    ax.set_xlabel('Price Range (AZN)', fontweight='bold')
    ax.set_ylabel('Number of Properties', fontweight='bold')
    ax.set_title('Property Distribution by Price Range\nIdentifying Market Sweet Spots',
                 fontsize=16, fontweight='bold', pad=20)

    # Add median line
    median_price = df_valid['price_numeric'].median()
    ax.axvline(x=2.5, color=COLORS['accent'], linestyle='--', linewidth=2, label=f'Median: {median_price:,.0f} AZN')
    ax.legend(loc='upper right', fontsize=11)

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/02_price_distribution.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: 02_price_distribution.png")


def chart_3_location_analysis(df):
    """Chart 3: Top Locations by Listing Volume"""
    fig, ax = plt.subplots(figsize=(12, 7))

    location_counts = df['location'].value_counts().head(10)
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(location_counts)))

    bars = ax.barh(location_counts.index[::-1], location_counts.values[::-1],
                   color=colors[::-1], edgecolor='white', linewidth=1.5)

    # Add value labels
    for bar, val in zip(bars, location_counts.values[::-1]):
        pct = val / len(df) * 100
        ax.text(val + 10, bar.get_y() + bar.get_height()/2,
                f'{val:,} ({pct:.1f}%)', va='center', fontweight='bold', fontsize=10)

    ax.set_xlabel('Number of Listings', fontweight='bold')
    ax.set_title('Top 10 Locations by Market Activity\nWhere is the Real Estate Action?',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(0, max(location_counts.values) * 1.3)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/03_location_analysis.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: 03_location_analysis.png")


def chart_4_price_by_property_type(df):
    """Chart 4: Average Price by Property Type"""
    fig, ax = plt.subplots(figsize=(12, 7))

    df_valid = df[df['price_numeric'].notna() & (df['price_numeric'] > 0) & (df['price_numeric'] < 2000000)]

    avg_prices = df_valid.groupby('property_type')['price_numeric'].agg(['mean', 'median', 'count'])
    avg_prices = avg_prices[avg_prices['count'] >= 10].sort_values('median', ascending=True)

    x = np.arange(len(avg_prices))
    width = 0.35

    bars1 = ax.barh(x - width/2, avg_prices['mean']/1000, width,
                    label='Average Price', color=COLORS['primary'], edgecolor='white')
    bars2 = ax.barh(x + width/2, avg_prices['median']/1000, width,
                    label='Median Price', color=COLORS['secondary'], edgecolor='white')

    ax.set_yticks(x)
    ax.set_yticklabels(avg_prices.index)
    ax.set_xlabel('Price (Thousand AZN)', fontweight='bold')
    ax.set_title('Price Comparison by Property Type\nAverage vs Median Analysis',
                 fontsize=16, fontweight='bold', pad=20)
    ax.legend(loc='lower right', fontsize=11)

    # Add count annotations
    for i, (idx, row) in enumerate(avg_prices.iterrows()):
        ax.text(max(row['mean'], row['median'])/1000 + 5, i,
                f'n={int(row["count"]):,}', va='center', fontsize=9, style='italic')

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/04_price_by_type.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: 04_price_by_type.png")


def chart_5_room_demand(df):
    """Chart 5: Market Demand by Room Count"""
    fig, ax = plt.subplots(figsize=(12, 7))

    df_valid = df[df['room_count'].notna() & (df['room_count'] >= 1) & (df['room_count'] <= 6)]
    room_counts = df_valid['room_count'].value_counts().sort_index()

    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(room_counts)))
    bars = ax.bar([f'{int(x)} Room{"s" if x > 1 else ""}' for x in room_counts.index],
                  room_counts.values, color=colors, edgecolor='white', linewidth=2)

    # Add value labels
    for bar, val in zip(bars, room_counts.values):
        pct = val / df_valid['room_count'].notna().sum() * 100
        ax.text(bar.get_x() + bar.get_width()/2, val + 20,
                f'{val:,}\n({pct:.1f}%)', ha='center', fontweight='bold', fontsize=10)

    ax.set_xlabel('Property Size', fontweight='bold')
    ax.set_ylabel('Number of Listings', fontweight='bold')
    ax.set_title('Market Supply by Property Size\nUnderstanding Inventory Distribution',
                 fontsize=16, fontweight='bold', pad=20)

    # Highlight most common
    max_idx = room_counts.values.argmax()
    bars[max_idx].set_edgecolor(COLORS['accent'])
    bars[max_idx].set_linewidth(3)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/05_room_demand.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: 05_room_demand.png")


def chart_6_document_readiness(df):
    """Chart 6: Legal Document Status"""
    fig, ax = plt.subplots(figsize=(12, 7))

    doc_types = df['document_type'].value_counts()

    # Categorize by risk level
    doc_labels = {
        'Çıxarış (Kupça)': 'Full Title Deed\n(Lowest Risk)',
        'Müqavilə': 'Contract Only\n(Medium Risk)',
        'Bələdiyyə sənədi': 'Municipal Doc\n(Medium Risk)',
        'Yoxdur': 'No Document\n(High Risk)',
        'Sərəncam': 'Decree\n(Medium Risk)',
        'Digər sənəd': 'Other\n(Verify Required)',
        'Qeydiyyat vəsiqəsi': 'Registration\n(Low Risk)',
        'Şəhadətnamə': 'Certificate\n(Low Risk)'
    }

    colors_map = {
        'Çıxarış (Kupça)': '#27AE60',
        'Müqavilə': '#F39C12',
        'Bələdiyyə sənədi': '#F39C12',
        'Yoxdur': '#E74C3C',
        'Sərəncam': '#F39C12',
        'Digər sənəd': '#95A5A6',
        'Qeydiyyat vəsiqəsi': '#2ECC71',
        'Şəhadətnamə': '#2ECC71'
    }

    labels = [doc_labels.get(x, x) for x in doc_types.index]
    colors = [colors_map.get(x, '#95A5A6') for x in doc_types.index]

    bars = ax.barh(labels[::-1], doc_types.values[::-1], color=colors[::-1], edgecolor='white', linewidth=1.5)

    for bar, val in zip(bars, doc_types.values[::-1]):
        pct = val / len(df) * 100
        ax.text(val + 20, bar.get_y() + bar.get_height()/2,
                f'{val:,} ({pct:.1f}%)', va='center', fontweight='bold', fontsize=10)

    ax.set_xlabel('Number of Properties', fontweight='bold')
    ax.set_title('Property Documentation Status\nLegal Readiness Assessment',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(0, max(doc_types.values) * 1.25)

    # Add legend for risk levels
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#27AE60', label='Low Risk'),
        Patch(facecolor='#F39C12', label='Medium Risk'),
        Patch(facecolor='#E74C3C', label='High Risk')
    ]
    ax.legend(handles=legend_elements, loc='lower right', title='Risk Level')

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/06_document_status.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: 06_document_status.png")


def chart_7_property_condition(df):
    """Chart 7: Property Condition Distribution"""
    fig, ax = plt.subplots(figsize=(12, 7))

    repair_map = {
        'Əla': 'Excellent',
        'Yaxşı': 'Good',
        'Orta': 'Average',
        'Təmirsiz': 'No Repairs',
        'Zəif': 'Poor',
        'Natamam': 'Unfinished',
        'Ağ divar': 'Shell Only'
    }

    condition_counts = df['repair_type'].value_counts()
    labels = [repair_map.get(x, x) for x in condition_counts.index]

    colors = ['#27AE60', '#2ECC71', '#F1C40F', '#E67E22', '#E74C3C', '#95A5A6', '#BDC3C7']

    bars = ax.bar(labels, condition_counts.values, color=colors[:len(labels)],
                  edgecolor='white', linewidth=2)

    for bar, val in zip(bars, condition_counts.values):
        pct = val / condition_counts.sum() * 100
        ax.text(bar.get_x() + bar.get_width()/2, val + 20,
                f'{val:,}\n({pct:.1f}%)', ha='center', fontweight='bold', fontsize=10)

    ax.set_xlabel('Property Condition', fontweight='bold')
    ax.set_ylabel('Number of Properties', fontweight='bold')
    ax.set_title('Property Condition Analysis\nMarket Quality Overview',
                 fontsize=16, fontweight='bold', pad=20)

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/07_property_condition.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: 07_property_condition.png")


def chart_8_top_agents(df):
    """Chart 8: Top Performing Agents"""
    fig, ax = plt.subplots(figsize=(12, 7))

    # Clean agent names
    df['agent_clean'] = df['user_name'].str.replace(r'\s*\(\s*Əmlak Agenti\s*\)', '', regex=True)
    df['agent_clean'] = df['agent_clean'].str.replace(r'\s*\(\s*Mülkiyyətçi\s*\)', ' [Owner]', regex=True)
    df['agent_clean'] = df['agent_clean'].str.strip()

    top_agents = df['agent_clean'].value_counts().head(12)

    colors = plt.cm.plasma(np.linspace(0.2, 0.8, len(top_agents)))
    bars = ax.barh(top_agents.index[::-1], top_agents.values[::-1],
                   color=colors[::-1], edgecolor='white', linewidth=1.5)

    for bar, val in zip(bars, top_agents.values[::-1]):
        market_share = val / len(df) * 100
        ax.text(val + 2, bar.get_y() + bar.get_height()/2,
                f'{val} ({market_share:.1f}%)', va='center', fontweight='bold', fontsize=10)

    ax.set_xlabel('Number of Active Listings', fontweight='bold')
    ax.set_title('Top 12 Real Estate Agents by Portfolio Size\nMarket Leadership Analysis',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(0, max(top_agents.values) * 1.25)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/08_top_agents.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: 08_top_agents.png")


def chart_9_price_per_sqm_by_location(df):
    """Chart 9: Price per Square Meter by Location"""
    fig, ax = plt.subplots(figsize=(12, 7))

    df_valid = df[(df['price_per_sqm'].notna()) &
                  (df['price_per_sqm'] > 100) &
                  (df['price_per_sqm'] < 10000)]

    location_prices = df_valid.groupby('location')['price_per_sqm'].agg(['median', 'count'])
    location_prices = location_prices[location_prices['count'] >= 20].sort_values('median', ascending=True)

    colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(location_prices)))
    bars = ax.barh(location_prices.index, location_prices['median'],
                   color=colors, edgecolor='white', linewidth=1.5)

    for bar, (idx, row) in zip(bars, location_prices.iterrows()):
        ax.text(row['median'] + 30, bar.get_y() + bar.get_height()/2,
                f'{row["median"]:,.0f} AZN/m²', va='center', fontweight='bold', fontsize=10)

    ax.set_xlabel('Median Price per m² (AZN)', fontweight='bold')
    ax.set_title('Real Estate Value by Location\nPrice per Square Meter Comparison',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(0, location_prices['median'].max() * 1.25)

    # Add average line
    overall_median = df_valid['price_per_sqm'].median()
    ax.axvline(x=overall_median, color=COLORS['accent'], linestyle='--', linewidth=2,
               label=f'Market Average: {overall_median:,.0f} AZN/m²')
    ax.legend(loc='lower right', fontsize=11)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/09_price_per_sqm.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: 09_price_per_sqm.png")


def chart_10_market_segments(df):
    """Chart 10: Market Segmentation Matrix"""
    fig, ax = plt.subplots(figsize=(14, 8))

    df_valid = df[(df['price_numeric'].notna()) &
                  (df['room_count'].notna()) &
                  (df['price_numeric'] > 0) &
                  (df['price_numeric'] < 1000000) &
                  (df['room_count'] >= 1) &
                  (df['room_count'] <= 5)]

    # Create segments
    df_valid['segment'] = pd.cut(df_valid['price_numeric'],
                                  bins=[0, 80000, 150000, 300000, 1000000],
                                  labels=['Budget', 'Mid-Range', 'Premium', 'Luxury'])

    # Create cross-tabulation
    segment_room = pd.crosstab(df_valid['segment'], df_valid['room_count'])
    segment_room.columns = [f'{int(x)} Room{"s" if x > 1 else ""}' for x in segment_room.columns]

    # Stacked bar chart
    segment_room.plot(kind='bar', stacked=True, ax=ax,
                      colormap='viridis', edgecolor='white', linewidth=1)

    ax.set_xlabel('Price Segment', fontweight='bold')
    ax.set_ylabel('Number of Properties', fontweight='bold')
    ax.set_title('Market Segmentation: Price Tier vs Property Size\nStrategic Portfolio Analysis',
                 fontsize=16, fontweight='bold', pad=20)
    ax.legend(title='Property Size', bbox_to_anchor=(1.02, 1), loc='upper left')

    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/10_market_segments.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: 10_market_segments.png")


def chart_11_listing_activity(df):
    """Chart 11: Listing Activity Over Time"""
    fig, ax = plt.subplots(figsize=(14, 7))

    df['date_parsed'] = pd.to_datetime(df['update_date'], format='%d.%m.%Y', errors='coerce')
    df_valid = df[df['date_parsed'].notna()]

    # Weekly aggregation
    df_valid['week'] = df_valid['date_parsed'].dt.to_period('W').dt.start_time
    weekly_counts = df_valid.groupby('week').size()

    ax.fill_between(weekly_counts.index, weekly_counts.values, alpha=0.3, color=COLORS['primary'])
    ax.plot(weekly_counts.index, weekly_counts.values, color=COLORS['primary'], linewidth=2.5, marker='o', markersize=4)

    ax.set_xlabel('Week', fontweight='bold')
    ax.set_ylabel('Number of Listings Updated', fontweight='bold')
    ax.set_title('Market Activity Trend\nWeekly Listing Updates',
                 fontsize=16, fontweight='bold', pad=20)

    # Add trend annotation
    avg_weekly = weekly_counts.mean()
    ax.axhline(y=avg_weekly, color=COLORS['accent'], linestyle='--', linewidth=2,
               label=f'Weekly Average: {avg_weekly:.0f} listings')
    ax.legend(loc='upper right', fontsize=11)

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/11_listing_activity.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: 11_listing_activity.png")


def chart_12_investment_opportunity(df):
    """Chart 12: Investment Opportunity Score"""
    fig, ax = plt.subplots(figsize=(12, 8))

    df_valid = df[(df['price_per_sqm'].notna()) &
                  (df['price_per_sqm'] > 100) &
                  (df['price_per_sqm'] < 10000) &
                  (df['view_count'].notna())]

    location_analysis = df_valid.groupby('location').agg({
        'price_per_sqm': 'median',
        'view_count': 'mean',
        'announcement_id': 'count'
    }).rename(columns={'announcement_id': 'listings'})

    location_analysis = location_analysis[location_analysis['listings'] >= 30]

    # Normalize for scoring
    location_analysis['price_score'] = 1 - (location_analysis['price_per_sqm'] - location_analysis['price_per_sqm'].min()) / (location_analysis['price_per_sqm'].max() - location_analysis['price_per_sqm'].min())
    location_analysis['demand_score'] = (location_analysis['view_count'] - location_analysis['view_count'].min()) / (location_analysis['view_count'].max() - location_analysis['view_count'].min())
    location_analysis['opportunity_score'] = (location_analysis['price_score'] + location_analysis['demand_score']) / 2

    location_analysis = location_analysis.sort_values('opportunity_score', ascending=True)

    colors = plt.cm.RdYlGn(location_analysis['opportunity_score'])
    bars = ax.barh(location_analysis.index, location_analysis['opportunity_score'],
                   color=colors, edgecolor='white', linewidth=1.5)

    for bar, (idx, row) in zip(bars, location_analysis.iterrows()):
        ax.text(row['opportunity_score'] + 0.02, bar.get_y() + bar.get_height()/2,
                f'{row["opportunity_score"]:.2f}', va='center', fontweight='bold', fontsize=10)

    ax.set_xlabel('Investment Opportunity Score (0-1)', fontweight='bold')
    ax.set_title('Investment Opportunity Index by Location\nBalancing Price Affordability & Market Demand',
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(0, 1.15)

    # Add explanation
    ax.text(0.95, 0.05, 'Higher Score = Better Opportunity\n(Low Price + High Demand)',
            transform=ax.transAxes, fontsize=10, verticalalignment='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/12_investment_opportunity.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: 12_investment_opportunity.png")


def generate_summary_dashboard(df):
    """Generate Executive Summary Dashboard"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Azerbaijan Real Estate Market - Executive Dashboard', fontsize=20, fontweight='bold', y=1.02)

    # 1. Total Market Value
    ax1 = axes[0, 0]
    df_valid = df[df['price_numeric'].notna()]
    total_value = df_valid['price_numeric'].sum()
    ax1.text(0.5, 0.6, f'{total_value/1e9:.2f}B AZN', ha='center', va='center',
             fontsize=36, fontweight='bold', color=COLORS['primary'])
    ax1.text(0.5, 0.3, 'Total Market Value', ha='center', va='center', fontsize=14)
    ax1.text(0.5, 0.15, f'({len(df_valid):,} properties)', ha='center', va='center', fontsize=11, style='italic')
    ax1.axis('off')
    ax1.set_title('Market Size', fontweight='bold', fontsize=14)

    # 2. Median Price
    ax2 = axes[0, 1]
    median_price = df_valid['price_numeric'].median()
    ax2.text(0.5, 0.6, f'{median_price:,.0f}', ha='center', va='center',
             fontsize=36, fontweight='bold', color=COLORS['secondary'])
    ax2.text(0.5, 0.3, 'Median Price (AZN)', ha='center', va='center', fontsize=14)
    ax2.axis('off')
    ax2.set_title('Price Benchmark', fontweight='bold', fontsize=14)

    # 3. Top Location
    ax3 = axes[0, 2]
    top_loc = df['location'].value_counts().index[0]
    top_loc_count = df['location'].value_counts().values[0]
    ax3.text(0.5, 0.6, top_loc, ha='center', va='center',
             fontsize=28, fontweight='bold', color=COLORS['success'])
    ax3.text(0.5, 0.3, 'Most Active Location', ha='center', va='center', fontsize=14)
    ax3.text(0.5, 0.15, f'{top_loc_count:,} listings ({top_loc_count/len(df)*100:.1f}%)',
             ha='center', va='center', fontsize=11, style='italic')
    ax3.axis('off')
    ax3.set_title('Market Hotspot', fontweight='bold', fontsize=14)

    # 4. Property Type Distribution (mini bar)
    ax4 = axes[1, 0]
    type_counts = df['property_type'].value_counts().head(4)
    colors = [COLORS['primary'], COLORS['secondary'], COLORS['success'], COLORS['warning']]
    ax4.barh(type_counts.index[::-1], type_counts.values[::-1], color=colors[::-1])
    ax4.set_title('Property Mix', fontweight='bold', fontsize=14)
    ax4.set_xlabel('Listings')

    # 5. Document Status Summary
    ax5 = axes[1, 1]
    kupca_pct = (df['document_type'] == 'Çıxarış (Kupça)').sum() / len(df) * 100
    ax5.text(0.5, 0.6, f'{kupca_pct:.1f}%', ha='center', va='center',
             fontsize=36, fontweight='bold', color=COLORS['success'])
    ax5.text(0.5, 0.3, 'Have Full Title Deed', ha='center', va='center', fontsize=14)
    ax5.text(0.5, 0.15, '(Lowest Legal Risk)', ha='center', va='center', fontsize=11, style='italic')
    ax5.axis('off')
    ax5.set_title('Legal Readiness', fontweight='bold', fontsize=14)

    # 6. Quality Summary
    ax6 = axes[1, 2]
    good_condition = df['repair_type'].isin(['Əla', 'Yaxşı']).sum() / df['repair_type'].notna().sum() * 100
    ax6.text(0.5, 0.6, f'{good_condition:.1f}%', ha='center', va='center',
             fontsize=36, fontweight='bold', color=COLORS['info'])
    ax6.text(0.5, 0.3, 'Good/Excellent Condition', ha='center', va='center', fontsize=14)
    ax6.text(0.5, 0.15, '(Move-in Ready)', ha='center', va='center', fontsize=11, style='italic')
    ax6.axis('off')
    ax6.set_title('Property Quality', fontweight='bold', fontsize=14)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/00_executive_dashboard.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print("Generated: 00_executive_dashboard.png")


def main():
    print("=" * 60)
    print("Generating Business Analytics Charts")
    print("=" * 60)

    df = load_and_prepare_data()
    print(f"\nLoaded {len(df):,} property records")
    print(f"Generating charts in '{OUTPUT_DIR}/' directory...\n")

    generate_summary_dashboard(df)
    chart_1_market_composition(df)
    chart_2_price_distribution(df)
    chart_3_location_analysis(df)
    chart_4_price_by_property_type(df)
    chart_5_room_demand(df)
    chart_6_document_readiness(df)
    chart_7_property_condition(df)
    chart_8_top_agents(df)
    chart_9_price_per_sqm_by_location(df)
    chart_10_market_segments(df)
    chart_11_listing_activity(df)
    chart_12_investment_opportunity(df)

    print("\n" + "=" * 60)
    print("All charts generated successfully!")
    print(f"Output directory: {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
