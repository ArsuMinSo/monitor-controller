while True:
    icon = input("Your SVG icon code: ")
    icon = icon.strip()
    # Extract d="..." value
    if icon.count('d="') > 1:
        wrapped = icon
    else:
        start = icon.find('d="')
        if start == -1:
            print("No d attribute found.")
            continue
        start += 3
        end = icon.find('"', start)
        if end == -1:
            print("Malformed d attribute.")
            continue
        d_value = icon[start:end]
        wrapped = f'''<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="{d_value}" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>'''
    
    # Wrap in another wrapper
    icon_name = input("Enter icon name: ").strip()
    if not icon_name:
        print("No icon name provided.")
    
    with open(f"./web/icons/{icon_name}.svg", "w", encoding="utf-8") as f:
        f.write(wrapped)
        f.close()
    print("Icon saved as", f"{icon_name}.svg\n\n")
