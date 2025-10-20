#!/usr/bin/env python3
"""
简单修复content_list_data.json文件
"""

import json

def fix_content_list():
    # 读取文件
    with open('content_list_data.json', 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    print(f"原始内容类型: {type(content)}")
    print(f"原始内容前50字符: {content[:50]}")
    
    # 如果内容是字符串，需要解析它
    if isinstance(content, str) and content.startswith('"'):
        # 这是一个JSON字符串，需要解析
        try:
            parsed = json.loads(content)
            print(f"解析后类型: {type(parsed)}")
            print(f"解析后长度: {len(parsed)}")
            
            # 直接写入解析后的数据
            with open('content_list_data.json', 'w', encoding='utf-8') as f:
                json.dump(parsed, f, ensure_ascii=False, indent=2)
            
            print("✅ 文件已修复！")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析错误: {e}")
            return False
    else:
        print("文件已经是正确的格式")
        return True

if __name__ == "__main__":
    fix_content_list()
