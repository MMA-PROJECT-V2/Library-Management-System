import xml.etree.ElementTree as ET

try:
    tree = ET.parse('coverage.xml')
    root = tree.getroot()
    
    print(f"{'File':<60} {'Line Rate':<10}")
    print("-" * 70)
    
    for c in root.findall('.//class'):
        filename = c.get('filename')
        if 'notifications' in filename:
            line_rate = float(c.get('line-rate'))
            print(f"{filename:<60} {line_rate:.2%}")
            
except Exception as e:
    print(f"Error: {e}")
