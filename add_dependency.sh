#!/bin/bash

# 添加新依赖的便捷脚本
# 用法: ./add_dependency.sh package_name

if [ $# -eq 0 ]; then
    echo "用法: ./add_dependency.sh <package_name> [version]"
    echo "示例: ./add_dependency.sh requests"
    echo "示例: ./add_dependency.sh django-rest-framework==3.14.0"
    exit 1
fi

PACKAGE=$1
VERSION=$2

echo "正在添加依赖: $PACKAGE"

# 如果指定了版本，添加到 requirements.in
if [ -n "$VERSION" ]; then
    echo "$PACKAGE==$VERSION" >> requirements.in
else
    echo "$PACKAGE" >> requirements.in
fi

echo "已添加到 requirements.in"

# 重新编译 requirements.txt
echo "正在重新编译 requirements.txt..."
pip-compile requirements.in

echo "✅ 依赖添加完成！"
echo "📦 新依赖: $PACKAGE"
echo "🔒 版本已锁定到 requirements.txt"
echo ""
echo "💡 提示: 运行 'pip install -r requirements.txt' 安装新依赖"
