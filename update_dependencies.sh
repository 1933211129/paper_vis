#!/bin/bash

# 更新所有依赖的便捷脚本

echo "🔄 正在更新依赖..."

# 重新编译 requirements.txt
echo "📦 重新编译 requirements.txt..."
pip-compile requirements.in

echo "✅ 依赖更新完成！"
echo ""
echo "💡 提示: 运行以下命令安装更新的依赖:"
echo "   pip install -r requirements.txt"
echo ""
echo "🔍 查看依赖变更:"
echo "   git diff requirements.txt"
