#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI 服务器 - 学术论文智能分析接口
基于 MainScheduler 的完整论文处理系统

唯一接口：
POST /paper_vis
- 输入：上传PDF文件
- 输出：MainScheduler的完整JSON结果
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
import uvicorn

# 导入主调度器
from MainScheduler import MainScheduler


# 创建FastAPI应用
app = FastAPI(
    title="学术论文智能分析API",
    description="基于AI的学术论文智能分析系统",
    version="1.0.0"
)


@app.post("/paper_vis")
async def paper_vis(file: UploadFile = File(...)):
    """
    分析PDF论文 - 唯一接口
    
    输入：
    - file: 上传的PDF文件
    
    输出：
    - MainScheduler的完整JSON结果
    """
    try:
        print(f"🚀 开始处理PDF文件: {file.filename}")
        
        # 检查文件类型
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail="只支持PDF文件格式"
            )
        
        # 读取上传的文件内容
        file_content = await file.read()
        
        # 创建主调度器实例
        scheduler = MainScheduler()
        
        # 执行完整的论文分析流程（直接使用文件内容，不保存到服务器）
        result = scheduler.process_uploaded_pdf(file_content, file.filename)
        
        return result
            
    except Exception as e:
        print(f"❌ 服务器内部错误: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )


if __name__ == "__main__":
    print("🚀 启动学术论文智能分析API服务器...")
    print("📡 服务地址: http://10.3.35.21:8004")
    print("📊 唯一接口: POST /paper_vis")
    print("=" * 60)
    
    # 启动服务器
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )
