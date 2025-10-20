#!/usr/bin/env python3
"""
直接修复content_list_data.json文件
"""

import json

def fix_json_file():
    # 读取原始文件
    with open('content_list_data.json', 'r', encoding='utf-8') as f:
        content = f.read().strip()
    
    print(f"原始内容类型: {type(content)}")
    print(f"原始内容前100字符: {content[:100]}")
    
    # 如果内容以引号开始，说明是JSON字符串，需要解析
    if content.startswith('"') and content.endswith('"'):
        print("检测到JSON字符串格式，正在解析...")
        try:
            # 解析JSON字符串
            parsed_data = json.loads(content)
            print(f"解析成功，数据类型: {type(parsed_data)}")
            print(f"解析后长度: {len(parsed_data)}")
            
            # 验证第一个元素
            if isinstance(parsed_data, list) and len(parsed_data) > 0:
                first_item = parsed_data[0]
                print(f"第一个元素类型: {type(first_item)}")
                if isinstance(first_item, dict):
                    print(f"第一个元素键: {list(first_item.keys())}")
                else:
                    print(f"第一个元素内容: {first_item}")
            
            # 写入修复后的数据
            with open('content_list_data.json', 'w', encoding='utf-8') as f:
                json.dump(parsed_data, f, ensure_ascii=False, indent=2)
            
            print("✅ 文件修复成功！")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return False
    else:
        print("文件已经是正确的JSON格式")
        return True

if __name__ == "__main__":
    success = fix_json_file()
    if success:
        print("\n🎉 修复完成！")
    else:
        print("\n❌ 修复失败！")
