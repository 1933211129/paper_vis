"""
PDF文件上传API视图
处理前端上传的PDF文件，调用PDF解析接口，保存到后端指定路径
"""

import os
import uuid
import shutil
import requests
import time
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import json
import logging
import sys

# 配置日志
logger = logging.getLogger(__name__)

# 添加functions目录到Python路径
functions_path = os.path.join(os.path.dirname(__file__), '..', 'functions')
if functions_path not in sys.path:
    sys.path.append(functions_path)

# 导入MainScheduler
try:
    from MainScheduler import MainScheduler
    logger.info(f"MainScheduler导入成功，路径: {functions_path}")
except ImportError as e:
    logger.error(f"无法导入MainScheduler: {e}")
    logger.error(f"Python路径: {sys.path}")
    MainScheduler = None

# PDF文件上传路径
PDF_UPLOAD_PATH = '/data/kongyb/paper_vis/backend/uploads/pdfs'
# PDF解析结果路径
PDF_PARSE_OUTPUT_PATH = '/data/kongyb/paper_vis/backend/uploads/papers'
# PDF解析接口地址
PDF_PARSE_API_URL = "http://10.3.35.21:8003/file_parse"

@csrf_exempt
@require_http_methods(["POST"])
def upload_pdf(request):
    """
    处理PDF文件上传请求
    
    期望的请求格式：
    - Content-Type: multipart/form-data
    - 字段名: file (单个PDF文件)
    
    返回格式：
    {
        "success": true/false,
        "message": "消息",
        "pdf_path": "PDF保存路径",
        "parse_output_path": "解析结果路径",
        "folder_id": "文件夹ID"
    }
    """
    try:
        # 检查是否有文件
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'message': '没有找到上传的PDF文件'
            }, status=400)
        
        pdf_file = request.FILES['file']
        
        # 检查文件类型
        if not pdf_file.name.lower().endswith('.pdf'):
            return JsonResponse({
                'success': False,
                'message': '只支持PDF文件格式'
            }, status=400)
        
        # 生成时间戳文件名
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3]  # 精确到毫秒
        pdf_filename = f"{timestamp}.pdf"
        
        # 确保PDF上传目录存在
        os.makedirs(PDF_UPLOAD_PATH, exist_ok=True)
        os.makedirs(PDF_PARSE_OUTPUT_PATH, exist_ok=True)
        
        # 保存PDF文件
        pdf_path = os.path.join(PDF_UPLOAD_PATH, pdf_filename)
        with open(pdf_path, 'wb') as destination:
            for chunk in pdf_file.chunks():
                destination.write(chunk)
        
        logger.info(f"PDF文件保存成功: {pdf_path}")
        
        # 调用PDF解析接口
        try:
            logger.info("开始调用PDF解析接口...")
            
            # 准备请求数据
            form_data = {
                'backend': 'pipeline',
                'output_dir': PDF_PARSE_OUTPUT_PATH
            }
            
            files_to_upload = {
                'files': (pdf_filename, open(pdf_path, 'rb'), 'application/pdf')
            }
            
            # 发送请求
            start_time = time.time()
            response = requests.post(PDF_PARSE_API_URL, files=files_to_upload, data=form_data)
            end_time = time.time()
            
            # 关闭文件
            files_to_upload['files'][1].close()
            
            if response.status_code == 200:
                result = response.json()
                parse_output_path = result.get('output_path')
                
                if parse_output_path:
                    logger.info(f"PDF解析成功，结果路径: {parse_output_path}")
                    logger.info(f"解析耗时: {end_time - start_time:.2f}秒")
                    
                    # 验证解析结果
                    validation_result = validate_required_files(parse_output_path)
                    
                    if not validation_result['valid']:
                        return JsonResponse({
                            'success': False,
                            'message': f"PDF解析结果验证失败: {validation_result['message']}"
                        }, status=400)
                    
                    # 生成文件夹ID（使用UUID）
                    folder_id = str(uuid.uuid4())
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'PDF上传和解析成功',
                        'pdf_path': pdf_path,
                        'parse_output_path': parse_output_path,
                        'folder_id': folder_id,
                        'parse_time': end_time - start_time,
                        'validation': validation_result,
                        'status': 'parsing_complete',
                        'next_step': 'extraction'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'PDF解析接口未返回输出路径'
                    }, status=500)
            else:
                logger.error(f"PDF解析接口返回错误: {response.status_code} - {response.text}")
                return JsonResponse({
                    'success': False,
                    'message': f'PDF解析失败: {response.status_code} - {response.text}'
                }, status=500)
                
        except requests.exceptions.ConnectionError:
            logger.error("无法连接到PDF解析服务")
            return JsonResponse({
                'success': False,
                'message': '无法连接到PDF解析服务，请检查服务是否运行'
            }, status=500)
        except Exception as parse_error:
            logger.error(f"PDF解析异常: {parse_error}")
            return JsonResponse({
                'success': False,
                'message': f'PDF解析过程中发生错误: {str(parse_error)}'
            }, status=500)
        
    except Exception as e:
        logger.error(f"PDF上传异常: {e}")
        return JsonResponse({
            'success': False,
            'message': f'上传过程中发生错误: {str(e)}'
        }, status=500)


def validate_required_files(folder_path):
    """
    验证文件夹是否包含必需的文件（适配PDF解析后的文件结构）
    
    Args:
        folder_path: 文件夹路径
    
    Returns:
        dict: 验证结果
    """
    try:
        required_files = {
            'md_file': False,
            'content_list': False,
            'middle': False
        }
        
        found_files = []
        images_count = 0
        
        # 遍历文件夹中的所有文件
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, folder_path)
                found_files.append(relative_path)
                
                # 检查必需的文件类型
                if file.endswith('.md'):
                    required_files['md_file'] = True
                elif 'content_list.json' in file:
                    required_files['content_list'] = True
                elif 'middle.json' in file:
                    required_files['middle'] = True
                
                # 统计图片文件
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    images_count += 1
        
        # 检查是否所有必需文件都存在
        missing_files = []
        for file_type, exists in required_files.items():
            if not exists:
                if file_type == 'md_file':
                    missing_files.append('*.md 文件')
                elif file_type == 'content_list':
                    missing_files.append('*content_list.json 文件')
                elif file_type == 'middle':
                    missing_files.append('*middle.json 文件')
        
        if missing_files:
            return {
                'valid': False,
                'message': f"缺少必需文件: {', '.join(missing_files)}",
                'found_files': found_files,
                'required_files': required_files,
                'images_count': images_count
            }
        
        return {
            'valid': True,
            'message': '所有必需文件都存在',
            'found_files': found_files,
            'required_files': required_files,
            'images_count': images_count
        }
        
    except Exception as e:
        logger.error(f"文件验证异常: {e}")
        return {
            'valid': False,
            'message': f'文件验证过程中发生错误: {str(e)}',
            'found_files': [],
            'required_files': required_files,
            'images_count': 0
        }


@require_http_methods(["GET"])
def list_uploaded_folders(request):
    """
    列出已上传的文件夹（适配PDF解析后的文件结构）
    
    返回格式：
    {
        "success": true,
        "folders": [
            {
                "folder_id": "uuid",
                "folder_path": "路径",
                "upload_time": "时间",
                "file_count": 数量,
                "validation": 验证结果
            }
        ]
    }
    """
    try:
        if not os.path.exists(PDF_PARSE_OUTPUT_PATH):
            return JsonResponse({
                'success': True,
                'folders': []
            })
        
        folders = []
        for folder_name in os.listdir(PDF_PARSE_OUTPUT_PATH):
            folder_path = os.path.join(PDF_PARSE_OUTPUT_PATH, folder_name)
            
            if os.path.isdir(folder_path):
                # 获取文件夹信息
                stat = os.stat(folder_path)
                file_count = len([f for f in os.listdir(folder_path) 
                                if os.path.isfile(os.path.join(folder_path, f))])
                
                # 验证文件夹
                validation = validate_required_files(folder_path)
                
                folders.append({
                    'folder_id': folder_name,
                    'folder_path': folder_path,
                    'upload_time': stat.st_ctime,
                    'file_count': file_count,
                    'validation': validation
                })
        
        # 按上传时间排序（最新的在前）
        folders.sort(key=lambda x: x['upload_time'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'folders': folders
        })
        
    except Exception as e:
        logger.error(f"列出文件夹异常: {e}")
        return JsonResponse({
            'success': False,
            'message': f'列出文件夹时发生错误: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_folder(request, folder_id):
    """
    删除指定的文件夹（适配PDF解析后的文件结构）
    
    Args:
        folder_id: 文件夹ID或完整路径
    """
    try:
        # 构建文件夹路径 - 现在使用PDF解析结果路径
        if os.path.exists(folder_id):
            # 如果folder_id是完整路径，直接使用
            folder_path = folder_id
        else:
            # 否则尝试在PDF解析结果目录中查找
            folder_path = os.path.join(PDF_PARSE_OUTPUT_PATH, folder_id)
        
        if not os.path.exists(folder_path):
            return JsonResponse({
                'success': False,
                'message': '文件夹不存在'
            }, status=404)
        
        # 删除文件夹
        shutil.rmtree(folder_path)
        
        logger.info(f"删除文件夹: {folder_path}")
        
        return JsonResponse({
            'success': True,
            'message': '文件夹删除成功'
        })
        
    except Exception as e:
        logger.error(f"删除文件夹异常: {e}")
        return JsonResponse({
            'success': False,
            'message': f'删除文件夹时发生错误: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def start_analysis(request):
    logger.info(f"收到start_analysis请求: {request.method} {request.path}")
    logger.info(f"请求头: {dict(request.headers)}")
    logger.info(f"请求体: {request.body}")
    """
    开始分析指定的文件夹
    
    请求格式：
    {
        "folder_id": "uuid"
    }
    
    返回格式：
    {
        "success": true/false,
        "message": "消息",
        "analysis_result": {
            "total_time": 耗时,
            "generated_files": 生成的文件列表,
            "file_check_results": 文件检查结果
        }
    }
    """
    try:
        # 解析请求数据
        data = json.loads(request.body)
        folder_id = data.get('folder_id')
        
        if not folder_id:
            return JsonResponse({
                'success': False,
                'message': '缺少folder_id参数'
            }, status=400)
        
        # 构建文件夹路径 - 现在使用PDF解析结果路径
        # folder_id 实际上是解析结果的UUID路径
        if os.path.exists(folder_id):
            # 如果folder_id是完整路径，直接使用
            folder_path = folder_id
        else:
            # 否则尝试在PDF解析结果目录中查找
            folder_path = os.path.join(PDF_PARSE_OUTPUT_PATH, folder_id)
        
        # 检查文件夹是否存在
        if not os.path.exists(folder_path):
            return JsonResponse({
                'success': False,
                'message': '指定的文件夹不存在'
            }, status=404)
        
        # 验证文件夹是否包含必需文件
        validation_result = validate_required_files(folder_path)
        if not validation_result['valid']:
            return JsonResponse({
                'success': False,
                'message': f"文件夹验证失败: {validation_result['message']}"
            }, status=400)
        
        # 检查MainScheduler是否可用
        if MainScheduler is None:
            return JsonResponse({
                'success': False,
                'message': 'MainScheduler模块不可用'
            }, status=500)
        
        logger.info(f"开始分析文件夹: {folder_path}")
        logger.info(f"MainScheduler可用性: {MainScheduler is not None}")
        
        # 创建MainScheduler实例并执行分析
        try:
            scheduler = MainScheduler()
            logger.info("MainScheduler实例创建成功")
            analysis_result = scheduler.process_folder(folder_path)
            logger.info(f"分析结果: {analysis_result}")
        except Exception as scheduler_error:
            logger.error(f"MainScheduler执行异常: {scheduler_error}")
            import traceback
            logger.error(f"详细错误信息: {traceback.format_exc()}")
            return JsonResponse({
                'success': False,
                'message': f'MainScheduler执行异常: {str(scheduler_error)}'
            }, status=500)
        
        if analysis_result['success']:
            logger.info(f"分析完成: {folder_path}")
            logger.info(f"耗时: {analysis_result['total_time']:.2f}秒")
            
            return JsonResponse({
                'success': True,
                'message': '分析完成',
                'status': 'extraction_complete',
                'analysis_result': {
                    'total_time': analysis_result['total_time'],
                    'generated_files': analysis_result['file_check_results']['generated_files'],
                    'file_check_results': analysis_result['file_check_results'],
                    'output_folder': analysis_result['output_folder']
                }
            })
        else:
            logger.error(f"分析失败: {analysis_result['error']}")
            return JsonResponse({
                'success': False,
                'message': f"分析失败: {analysis_result['error']}",
                'analysis_result': {
                    'total_time': analysis_result.get('total_time', 0),
                    'error': analysis_result['error']
                }
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': '请求数据格式错误'
        }, status=400)
    except Exception as e:
        logger.error(f"分析异常: {e}")
        return JsonResponse({
            'success': False,
            'message': f'分析过程中发生错误: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def get_visualization_data(request, folder_id):
    """
    获取指定文件夹的可视化数据（适配PDF解析后的文件结构）
    
    返回格式：
    {
        "success": true/false,
        "message": "消息",
        "data": {
            "metadata": {...},
            "abstract": {...},
            "context_related_work": {...},
            "methodology_setup": {...},
            "results_analysis": {...},
            "conclusion": {...},
            "figure_map": {...}
        }
    }
    """
    try:
        # 构建文件夹路径 - 现在使用PDF解析结果路径
        # folder_id 实际上是解析结果的UUID路径
        if os.path.exists(folder_id):
            # 如果folder_id是完整路径，直接使用
            folder_path = folder_id
        else:
            # 否则尝试在PDF解析结果目录中查找
            folder_path = os.path.join(PDF_PARSE_OUTPUT_PATH, folder_id)
        
        # 检查文件夹是否存在
        if not os.path.exists(folder_path):
            return JsonResponse({
                'success': False,
                'message': '指定的文件夹不存在'
            }, status=404)
        
        # 定义需要加载的JSON文件
        json_files = [
            'metadata.json',
            'abstract.json', 
            'context_related_work.json',
            'methodology_setup.json',
            'results_analysis.json',
            'conclusion.json',
            'figure_map.json'
        ]
        
        # 加载JSON数据
        data = {}
        for filename in json_files:
            file_path = os.path.join(folder_path, filename)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # 使用文件名（去掉.json后缀）作为键
                        key = filename.replace('.json', '')
                        data[key] = json.load(f)
                except Exception as e:
                    logger.warning(f"读取文件 {filename} 失败: {e}")
                    data[filename.replace('.json', '')] = None
            else:
                # 文件不存在时设置为None
                data[filename.replace('.json', '')] = None
        
        # 检查是否有任何数据
        if not any(data.values()):
            return JsonResponse({
                'success': False,
                'message': '文件夹中没有找到任何可视化数据文件'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'message': '数据加载成功',
            'data': data
        })
        
    except Exception as e:
        logger.error(f"获取可视化数据异常: {e}")
        return JsonResponse({
            'success': False,
            'message': f'获取可视化数据时发生错误: {str(e)}'
        }, status=500)


@require_http_methods(["GET", "HEAD"])
def get_visualization_image(request, folder_id, figure_id):
    """
    获取指定文件夹中的图片文件（适配PDF解析后的文件结构）
    
    支持多种图片格式：jpg, jpeg, png
    支持嵌套的images文件夹结构
    """
    try:
        # 构建文件夹路径 - 现在使用PDF解析结果路径
        # folder_id 实际上是解析结果的UUID路径
        if os.path.exists(folder_id):
            # 如果folder_id是完整路径，直接使用
            folder_path = folder_id
        else:
            # 否则尝试在PDF解析结果目录中查找
            folder_path = os.path.join(PDF_PARSE_OUTPUT_PATH, folder_id)
        
        # 检查文件夹是否存在
        if not os.path.exists(folder_path):
            return JsonResponse({
                'success': False,
                'message': '指定的文件夹不存在'
            }, status=404)
        
        # 支持的图片格式
        image_extensions = ['.jpg', '.jpeg', '.png']
        
        # 尝试找到图片文件 - 首先在根目录查找
        image_path = None
        for ext in image_extensions:
            potential_path = os.path.join(folder_path, f"{figure_id}{ext}")
            if os.path.exists(potential_path):
                image_path = potential_path
                break
        
        # 如果在根目录没找到，尝试在images子目录中查找
        if not image_path:
            images_dir = os.path.join(folder_path, 'images')
            if os.path.exists(images_dir):
                for ext in image_extensions:
                    potential_path = os.path.join(images_dir, f"{figure_id}{ext}")
                    if os.path.exists(potential_path):
                        image_path = potential_path
                        break
        
        if not image_path:
            return JsonResponse({
                'success': False,
                'message': f'找不到图片文件: {figure_id}'
            }, status=404)
        
        # 返回图片文件
        from django.http import FileResponse
        return FileResponse(
            open(image_path, 'rb'),
            content_type='image/jpeg' if image_path.endswith(('.jpg', '.jpeg')) else 'image/png'
        )
        
    except Exception as e:
        logger.error(f"获取图片文件异常: {e}")
        return JsonResponse({
            'success': False,
            'message': f'获取图片文件时发生错误: {str(e)}'
        }, status=500)
