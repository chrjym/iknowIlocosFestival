import pandas as pd
import re
from typing import List, Dict, Any

# Load Excel into a DataFrame
df = pd.read_excel('Aidatabase.xlsx')

# Normalize column names (strip whitespace and lowercase)
df.columns = [c.strip().lower() for c in df.columns]

# Map the actual column 'about that festival' to 'description'
col_mapping = {
    'municipalities': 'location',
    'festival': 'festival',
    'category': 'category', 
    'month': 'month',
    'about that festival': 'description'
}

# Only rename columns that exist
for old_name, new_name in col_mapping.items():
    if old_name in df.columns:
        df = df.rename(columns={old_name: new_name})

# Convert to list of dicts (knowledge base)
facts: List[Dict[str, Any]] = df.to_dict(orient='records')

def parse_query(query: str) -> Dict[str, str]:
    """Parse user query - NEW APPROACH: Search ALL fields with query words"""
    query_lower = query.lower().strip()
    words = re.findall(r'\b\w+\b', query_lower)
    
    result = {'location': '', 'month': '', 'festival': '', 'category': '', 'raw_words': words}
    
    months = {'january', 'february', 'march', 'april', 'may', 'june', 
              'july', 'august', 'september', 'october', 'november', 'december'}
    
    # Sequential assignment (FIXED: removed len>4 bug)
    for word in words:
        if word in months:
            result['month'] = word.title()
        elif word not in {'festival', 'of', 'in', 'the', 'about', 'what', 'is', 'and'}:
            if not result['location']:
                result['location'] = word.title()
            elif not result['festival']:
                result['festival'] = word.title()
            elif not result['category']:
                result['category'] = word.title()
    
    return result

def check_query_has_all_fields(parsed: Dict[str, str]) -> bool:
    """Check if USER QUERY provided ALL 4 fields"""
    return (parsed['location'] and 
            parsed['festival'] and 
            parsed['category'] and 
            parsed['month'])

def find_festival_matches(query: str) -> List[Dict[str, Any]]:
    """NEW APPROACH: Search EVERY field with query words"""
    parsed = parse_query(query)
    matches = []
    query_words = [w.lower() for w in parsed['raw_words']]
    
    for fact in facts:
        score = 0
        match_reasons = []
        
        # Search EVERY field with ALL query words
        all_text = ' '.join([
            str(fact.get('location', '')).lower(),
            str(fact.get('festival', '')).lower(),
            str(fact.get('category', '')).lower(),
            str(fact.get('month', '')).lower(),
            str(fact.get('description', '')).lower()
        ])
        
        # Match any query word in any field
        for qword in query_words:
            if qword in all_text:
                score += 2
                match_reasons.append(f"{qword}")
        
        # Bonus for exact field matches
        if parsed['location'] and parsed['location'].lower() in str(fact.get('location', '')).lower():
            score += 3
            match_reasons.append("location")
        if parsed['festival'] and parsed['festival'].lower() in str(fact.get('festival', '')).lower():
            score += 4
            match_reasons.append("festival")
        if parsed['month'] and parsed['month'].lower() in str(fact.get('month', '')).lower():
            score += 3
            match_reasons.append("month")
        if parsed['category'] and parsed['category'].lower() in str(fact.get('category', '')).lower():
            score += 2
            match_reasons.append("category")
        
        if score > 0:
            fact['match_score'] = score
            fact['match_reasons'] = match_reasons
            matches.append(fact)
    
    return sorted(matches, key=lambda x: x['match_score'], reverse=True)

def process_query(query: str):
    """Process a single query and show results"""
    parsed = parse_query(query)
    print(f"\n🔍 Searching: '{query}'")
    print("=" * 60)
    
    matches = find_festival_matches(query)
    
    if not matches:
        print("❌ No festivals found matching your query.")
        print("\n💡 Try: 'saniata', 'pamulinawen', 'bacarra', 'religious'")
        return
    
    user_has_all_fields = check_query_has_all_fields(parsed)
    
    # Show top matches
    for i, match in enumerate(matches[:3], 1):
        print(f"\n🎉 #{i} BEST MATCH (Score: {match['match_score']})")
        print(f"   📍 Location: {match.get('location', 'N/A').strip()}")
        print(f"   🎭 Festival: {match.get('festival', 'N/A').strip().rstrip(',')}")
        
        if 'category' in match and match['category'] and str(match['category']).strip():
            print(f"   🏷️  Category: {match['category'].strip()}")
        if 'month' in match and match['month'] and str(match['month']).strip():
            print(f"   📅 Month: {match['month'].strip()}")
        
        # Description rules
        if user_has_all_fields:
            description = match.get('description', '').strip()
            if description and str(description).lower() != 'nan':
                print(f"   📝 {description}")
        elif len(parsed['raw_words']) == 1:  # Single word search
            print(f"   ℹ️  Found by: {match.get('festival', 'N/A').strip().rstrip(',')} Festival!")
        else:
            print(f"   ℹ️  🔒 Full description needs all 4 fields!")
            print(f"   💡 Try: '{match.get('location', '?')} {match.get('festival', '?').rstrip(',')} {match.get('category', '?')} {match.get('month', '?')}'")
        
        if 'match_reasons' in match:
            print(f"   ✅ Matches: {', '.join(match['match_reasons'][:3])}")
    
    print(f"\n📊 Found {len(matches)} total matches")

def main():
    print("🎊 Ilocos Norte Festival AI - NEW SEARCH ENGINE!")
    print("🔍 Searches ALL fields: location, festival, category, month, description")
    print("💡 Works with: 'saniata', 'pamulinawen', 'religious', 'bacarra'")
    print("=" * 60)
    
    while True:
        try:
            query = input("\n💬 Your question: ").strip()
            
            if query.lower() in {'quit', 'exit', 'bye', 'stop'}:
                print("\n👋 Thanks for using Festival AI!")
                break
            
            if not query:
                print("Please enter a question about festivals.")
                continue
            
            process_query(query)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"⚠️  Error: {e}")

if __name__ == '__main__':
    main()
