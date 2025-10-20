import requests
import os
import json

class PDFParserClient:
    """
    PDF解析客户端：
    输入：pdf文件路径
    输出：json对象
    {
        "filename": "document",
        "md_content": "# 文档标题\n\n这是解析后的markdown内容...",
        "middle_json": "{...}",
        "content_list": "[...]",
        "figure_dict": {"file_name","base64"},
        "backend": "pipeline",
        "version": "2.5.4"
    }
    """
    def __init__(self, server_url="http://10.3.35.21:8003/file_parse_json", backend='pipeline'):
        self.server_url = server_url
        self.backend = backend

    def upload_pdf(self, pdf_file_path):
        if not os.path.exists(pdf_file_path):
            raise FileNotFoundError(f"找不到要上传的文件: {pdf_file_path}")

        form_data = {
            'backend': self.backend
        }

        with open(pdf_file_path, 'rb') as f:
            files_to_upload = {
                'file': (os.path.basename(pdf_file_path), f, 'application/pdf')
            }
            try:
                response = requests.post(self.server_url, files=files_to_upload, data=form_data)
            except requests.exceptions.ConnectionError:
                raise ConnectionError(f"连接被拒绝。请确保服务端正在 {self.server_url} 运行。")

        if response.status_code == 200:
            try:
                result_json = response.json()
                return result_json
            except Exception as e:
                raise ValueError(f"解析JSON时出错: {e}")
        else:
            raise RuntimeError(f"请求失败, 状态码: {response.status_code}, 错误信息: {response.text}")

    def upload_pdf_from_content(self, file_content, filename):
        """
        从文件内容上传PDF（用于处理上传的文件流）
        
        Args:
            file_content: PDF文件内容（字节流）
            filename: 文件名
        
        Returns:
            dict: 解析结果
        """
        form_data = {
            'backend': self.backend
        }

        files_to_upload = {
            'file': (filename, file_content, 'application/pdf')
        }
        
        try:
            response = requests.post(self.server_url, files=files_to_upload, data=form_data)
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"连接被拒绝。请确保服务端正在 {self.server_url} 运行。")

        if response.status_code == 200:
            try:
                result_json = response.json()
                return result_json
            except Exception as e:
                raise ValueError(f"解析JSON时出错: {e}")
        else:
            raise RuntimeError(f"请求失败, 状态码: {response.status_code}, 错误信息: {response.text}")

# 用法示例:
# parser = PDFParserClient()
# result = parser.upload_pdf("/path/to/xxx.pdf")
# print(result)
