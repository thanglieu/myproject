import os
import re
from collections import defaultdict

def extract_css(html_content):
    # Find <style> content
    style_match = re.search(r'<style>(.*?)</style>', html_content, re.DOTALL | re.IGNORECASE)
    if not style_match:
        return ''
    return style_match.group(1).strip()

def parse_css_rules(css):
    rules = {}
    # Split by } but keep the selector
    parts = css.split('}')
    for part in parts:
        part = part.strip()
        if '{' in part:
            selector, properties = part.split('{', 1)
            selector = selector.strip()
            properties = properties.strip()
            if selector and properties:
                # Split properties by ;
                prop_list = [p.strip() for p in properties.split(';') if p.strip()]
                # Sort properties for normalization
                prop_list.sort()
                rules[selector] = '; '.join(prop_list)
    return rules

def main():
    base_path = 'blog/templates'
    files = [
        'confirm.html',
        'error.html',
        'filter.html',
        'home.html',
        'login.html',
        'register.html',
        'search.html',
        'articles/article.html',
        'articles/create.html',
        'users/user.html',
        'users/users_list.html'
    ]
    
    all_rules = defaultdict(list)  # rule -> list of files
    file_rules = {}  # file -> set of rules
    
    for file in files:
        path = os.path.join(base_path, file)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            css = extract_css(content)
            rules = parse_css_rules(css)
            file_rules[file] = set(rules.keys())
            for selector, props in rules.items():
                rule = f"{selector} {{ {props} }}"
                all_rules[rule].append(file)
    
    # Common rules: appear in at least 2 files
    common = {rule: files for rule, files in all_rules.items() if len(files) >= 2}
    
    # Unique per file: rules that appear only in that file
    unique_per_file = {}
    for file, rules in file_rules.items():
        unique = []
        for rule in all_rules:
            if len(all_rules[rule]) == 1 and file in all_rules[rule]:
                unique.append(rule)
        unique_per_file[file] = unique
    
    print("Common CSS rules (appear in at least 2 files):")
    for rule, files in common.items():
        print(f"Rule: {rule}")
        print(f"Files: {', '.join(files)}")
        print()
    
    print("Unique CSS rules per file:")
    for file, rules in unique_per_file.items():
        print(f"File: {file}")
        for rule in rules:
            print(f"  {rule}")
        print()

if __name__ == '__main__':
    main()