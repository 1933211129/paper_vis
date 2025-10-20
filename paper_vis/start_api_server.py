#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动学术论文智能分析API服务器
"""

import subprocess
import sys
import os


def start_server():
    """启动API服务器"""
    
    print("🚀 启动学术论文智能分析API服务器")
    print("=" * 60)
    
    # 检查依赖
    try:
        import fastapi
        import uvicorn
        import requests
        print("✅ 依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请安装依赖: pip install fastapi uvicorn requests")
        return
    
    # 检查MainScheduler模块
    try:
        from MainScheduler import MainScheduler
        print("✅ MainScheduler模块检查通过")
    except ImportError as e:
        print(f"❌ MainScheduler模块导入失败: {e}")
        return
    
    print("\n📡 服务器配置:")
    print("   - 地址: http://10.3.35.21:8004")
    print("   - API文档: http://10.3.35.21:8004/docs")
    print("   - 健康检查: http://10.3.35.21:8004/health")
    print("   - 主要接口: POST /paper_vis")
    print("   - 同步接口: POST /paper_vis_sync")
    
    print("\n🔧 接口说明:")
    print("   POST /paper_vis")
    print("   输入: {\"pdf_path\": \"/path/to/paper.pdf\"}")
    print("   输出: {\"success\": true, \"data\": {...}, \"total_time\": 42.93}")
    print("   POST /paper_vis_sync")
    print("   输入: {\"pdf_path\": \"/path/to/paper.pdf\"}")
    print("   输出: 直接返回MainScheduler完整结果")
    
    print("\n⚡ 启动服务器...")
    print("=" * 60)
    
    try:
        # 启动服务器
        subprocess.run([
            sys.executable, "api_server.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务器启动失败: {e}")
    except Exception as e:
        print(f"❌ 未知错误: {e}")


if __name__ == "__main__":
    start_server()
