#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试客户端
测试文件上传接口 /paper_vis
"""

import requests
import json
import time
import os


def test_paper_vis_upload():
    """测试 /paper_vis 文件上传接口"""
    
    # API服务器地址
    base_url = "http://10.3.35.21:8004"
    
    # 测试PDF文件路径
    test_pdf_path = "/Users/xiaokong/Desktop/2510.15614v1.pdf"
    
    print("🧪 测试 /paper_vis 文件上传接口")
    print("=" * 60)
    
    # 检查文件是否存在
    if not os.path.exists(test_pdf_path):
        print(f"❌ 测试文件不存在: {test_pdf_path}")
        return
    
    print(f"📄 上传文件: {test_pdf_path}")
    print("⏳ 开始分析...")
    
    start_time = time.time()
    
    try:
        # 准备文件上传
        with open(test_pdf_path, 'rb') as f:
            files = {
                'file': (os.path.basename(test_pdf_path), f, 'application/pdf')
            }
            
            response = requests.post(
                f"{base_url}/paper_vis",
                files=files,
                timeout=300  # 5分钟超时
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 论文分析成功")
            print(f"⏱️ 总耗时: {duration:.2f}秒")
            print(f"📊 处理结果:")
            print(f"   - 成功状态: {result.get('success', False)}")
            print(f"   - 处理时间: {result.get('total_time', 0):.2f}秒")
            
            if result.get('success'):
                print(f"   - 论文标题: {result.get('metadata', {}).get('title', 'N/A')}")
                authors = result.get('metadata', {}).get('authors', [])
                print(f"   - 作者数量: {len(authors) if authors else 0}")
                lanes = result.get('lanes', {})
                print(f"   - 泳道数量: {len(lanes) if lanes else 0}")
                figure_map = result.get('figure_map', {})
                total_figures = sum(len(figures) for figures in figure_map.values()) if figure_map else 0
                print(f"   - 图表总数: {total_figures}")
                
                # 保存结果到文件
                output_file = "paper_vis_upload_result.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"💾 结果已保存到: {output_file}")
            else:
                print(f"❌ 分析失败: {result.get('error', '未知错误')}")
        else:
            print(f"❌ 论文分析失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时（5分钟）")
    except Exception as e:
        print(f"❌ 论文分析异常: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")


def test_server_health():
    """测试服务器健康状态"""
    base_url = "http://10.3.35.21:8004"
    
    try:
        # 直接测试 /paper_vis 接口的OPTIONS请求
        response = requests.options(f"{base_url}/paper_vis", timeout=10)
        if response.status_code in [200, 405]:  # 405表示方法不允许，但接口存在
            print("✅ 服务器运行正常")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False


if __name__ == "__main__":
    print("🚀 开始API测试")
    print("=" * 60)
    
    # 首先测试服务器健康状态
    if test_server_health():
        print("\n" + "=" * 60)
        # 测试文件上传接口
        test_paper_vis_upload()
    else:
        print("❌ 服务器不可用，请先启动API服务器")
        print("   运行命令: python api_server.py")