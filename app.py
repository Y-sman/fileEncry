"""
简历向量化服务
使用Flask提供独立的向量化服务，调用Ollama+Qwen3 8B进行文本向量化，使用FAISS存储向量
"""
import os
import json
import pickle
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import faiss
import requests
from typing import List, Dict, Tuple

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen3-embedding:8b')  # 使用Qwen3 Embedding 8B模型
# qwen3-embedding:8b 的向量维度是 4096
VECTOR_DIMENSION = int(os.getenv('VECTOR_DIMENSION', 4096))  # 向量维度，根据模型调整
FAISS_INDEX_PATH = os.getenv('FAISS_INDEX_PATH', './faiss_index.bin')
RESUME_MAPPING_PATH = os.getenv('RESUME_MAPPING_PATH', './resume_mapping.json')

# 全局变量
faiss_index = None
resume_mapping = {}  # {vector_index: resume_id}
next_index = 0


def init_faiss_index():
    """初始化FAISS索引"""
    global faiss_index, next_index, resume_mapping
    
    if os.path.exists(FAISS_INDEX_PATH):
        try:
            faiss_index = faiss.read_index(FAISS_INDEX_PATH)
            next_index = faiss_index.ntotal
            loaded_dimension = faiss_index.d
            print(f"加载FAISS索引，当前向量数量: {next_index}，向量维度: {loaded_dimension}")
            
            # 检查维度是否匹配
            if loaded_dimension != VECTOR_DIMENSION:
                print(f"警告：已加载的索引维度 ({loaded_dimension}) 与配置的维度 ({VECTOR_DIMENSION}) 不匹配！")
                print(f"这会导致搜索失败。请删除索引文件重新创建：")
                print(f"  删除文件: {FAISS_INDEX_PATH}")
                print(f"  删除文件: {RESUME_MAPPING_PATH}")
                print(f"然后重启服务，系统会自动创建新的索引。")
        except Exception as e:
            print(f"加载FAISS索引失败: {e}，创建新索引")
            faiss_index = faiss.IndexFlatL2(VECTOR_DIMENSION)
    else:
        faiss_index = faiss.IndexFlatL2(VECTOR_DIMENSION)
        print(f"创建新的FAISS索引，向量维度: {VECTOR_DIMENSION}")
    
    # 加载简历映射
    if os.path.exists(RESUME_MAPPING_PATH):
        try:
            with open(RESUME_MAPPING_PATH, 'r', encoding='utf-8') as f:
                resume_mapping = json.load(f)
            print(f"加载简历映射，当前映射数量: {len(resume_mapping)}")
        except Exception as e:
            print(f"加载简历映射失败: {e}")
            resume_mapping = {}


def save_faiss_index():
    """保存FAISS索引"""
    try:
        faiss.write_index(faiss_index, FAISS_INDEX_PATH)
        with open(RESUME_MAPPING_PATH, 'w', encoding='utf-8') as f:
            json.dump(resume_mapping, f, ensure_ascii=False, indent=2)
        print("FAISS索引和映射已保存")
    except Exception as e:
        print(f"保存FAISS索引失败: {e}")


def get_embedding(text: str) -> np.ndarray:
    """
    使用Ollama获取文本向量
    """
    # 调用Ollama的embeddings接口
    response = requests.post(
        f'{OLLAMA_BASE_URL}/api/embeddings',
        json={
            'model': OLLAMA_MODEL,
            'prompt': text
        },
        timeout=60
    )
    
    if response.status_code == 200:
        embedding = response.json().get('embedding', [])
        if embedding:
            vector = np.array(embedding, dtype=np.float32)
            # 检查向量维度
            actual_dimension = len(vector)
            if actual_dimension != VECTOR_DIMENSION:
                print(f"警告：模型返回的向量维度 ({actual_dimension}) 与配置的维度 ({VECTOR_DIMENSION}) 不匹配！")
                print(f"建议更新 VECTOR_DIMENSION 环境变量为 {actual_dimension}，或删除旧索引文件重新创建。")
            return vector
        else:
            raise ValueError("返回的向量为空")
    else:
        error_msg = response.text
        try:
            error_data = response.json()
            if 'error' in error_data:
                error_msg = error_data['error']
        except:
            pass
        raise Exception(f"Ollama API错误: {response.status_code} - {error_msg}")


@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'ollama_url': OLLAMA_BASE_URL,
        'model': OLLAMA_MODEL,
        'vector_count': faiss_index.ntotal if faiss_index else 0
    })


@app.route('/api/vectorize', methods=['POST'])
def vectorize():
    """
    向量化简历内容
    POST /api/vectorize
    {
        "resume_id": 1,
        "content": "简历内容文本..."
    }
    """
    global faiss_index, next_index, resume_mapping
    
    try:
        data = request.json
        resume_id = data.get('resume_id')
        content = data.get('content', '')
        
        if not resume_id:
            return jsonify({'error': '缺少resume_id'}), 400
        
        if not content:
            return jsonify({'error': '缺少content'}), 400
        
        # 检查是否已存在该简历的向量
        existing_index = None
        for idx, rid in resume_mapping.items():
            if rid == resume_id:
                existing_index = int(idx)
                break
        
        # 获取向量
        print(f"正在向量化简历 {resume_id}...")
        vector = get_embedding(content)
        
        if existing_index is not None:
            # 更新现有向量
            faiss_index.reconstruct(existing_index, vector)
            print(f"更新简历 {resume_id} 的向量，索引: {existing_index}")
        else:
            # 添加新向量
            vector = vector.reshape(1, -1)
            faiss_index.add(vector)
            resume_mapping[str(next_index)] = resume_id
            existing_index = next_index
            next_index += 1
            print(f"添加简历 {resume_id} 的向量，索引: {existing_index}")
        
        # 保存索引
        save_faiss_index()
        
        return jsonify({
            'success': True,
            'resume_id': resume_id,
            'vector_index': existing_index,
            'vector_dimension': VECTOR_DIMENSION
        })
        
    except Exception as e:
        print(f"向量化失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/search', methods=['POST'])
def search():
    """
    智能搜索简历
    POST /api/search
    {
        "query": "搜索关键词或岗位描述...",
        "top_k": 10
    }
    """
    global faiss_index, resume_mapping
    
    try:
        data = request.json
        query = data.get('query', '')
        top_k = int(data.get('top_k', 10))
        
        if not query:
            return jsonify({'success': False, 'error': '缺少query'}), 400
        
        if faiss_index is None or faiss_index.ntotal == 0:
            return jsonify({'success': True, 'query': query, 'results': []})
        
        # 获取查询向量
        print(f"正在搜索: {query}")
        query_vector = None
        try:
            query_vector = get_embedding(query)
        except Exception as e:
            import traceback
            error_msg = f"获取向量失败: {str(e)}"
            error_detail = traceback.format_exc()
            print(error_msg)
            print(f"详细错误信息: {error_detail}")
            # 直接返回错误响应，不继续执行后续代码
            # 使用明确的return，确保不会继续执行
            error_response = jsonify({'success': False, 'error': error_msg, 'detail': error_detail})
            return error_response, 500
        
        # 检查向量是否成功获取（双重检查，确保安全）
        if query_vector is None:
            error_msg = '获取向量失败，返回值为None'
            print(error_msg)
            return jsonify({'success': False, 'error': error_msg}), 500
        
        # 只有在成功获取向量后才执行以下代码
        try:
            # 检查向量维度
            if len(query_vector.shape) == 1:
                query_vector = query_vector.reshape(1, -1)
            elif len(query_vector.shape) != 2 or query_vector.shape[0] != 1:
                error_msg = f"向量形状不正确: {query_vector.shape}，期望 (1, {VECTOR_DIMENSION})"
                print(error_msg)
                return jsonify({'success': False, 'error': error_msg}), 500
            
            # 检查向量维度是否匹配
            if query_vector.shape[1] != VECTOR_DIMENSION:
                error_msg = f"向量维度不匹配: {query_vector.shape[1]}，期望 {VECTOR_DIMENSION}"
                print(error_msg)
                return jsonify({'success': False, 'error': error_msg}), 500
                
        except Exception as e:
            import traceback
            error_msg = f"向量reshape失败: {str(e)}"
            error_detail = traceback.format_exc()
            print(error_msg)
            print(f"详细错误信息: {error_detail}")
            return jsonify({'success': False, 'error': error_msg, 'detail': error_detail}), 500
        
        # 搜索最相似的向量
        try:
            # 检查faiss_index是否有效
            if faiss_index is None:
                error_msg = "FAISS索引未初始化"
                print(error_msg)
                return jsonify({'success': False, 'error': error_msg}), 500
            
            if faiss_index.ntotal == 0:
                return jsonify({'success': True, 'query': query, 'results': []})
            
            k = min(top_k, faiss_index.ntotal)
            
            # 检查向量维度是否与索引匹配
            if query_vector.shape[1] != faiss_index.d:
                error_msg = f"查询向量维度 ({query_vector.shape[1]}) 与FAISS索引维度 ({faiss_index.d}) 不匹配。"
                error_msg += f" 请删除索引文件 ({FAISS_INDEX_PATH}) 和映射文件 ({RESUME_MAPPING_PATH})，然后重启服务重新创建索引。"
                print(error_msg)
                return jsonify({
                    'success': False, 
                    'error': error_msg,
                    'query_dimension': int(query_vector.shape[1]),
                    'index_dimension': int(faiss_index.d),
                    'solution': f'删除索引文件并重启服务，或设置 VECTOR_DIMENSION={query_vector.shape[1]} 环境变量'
                }), 500
            
            distances, indices = faiss_index.search(query_vector, k)
            
        except Exception as e:
            import traceback
            error_msg = f"FAISS搜索失败: {str(e)}"
            error_detail = traceback.format_exc()
            print(error_msg)
            print(f"详细错误信息: {error_detail}")
            print(f"查询向量形状: {query_vector.shape if 'query_vector' in locals() else 'N/A'}")
            print(f"FAISS索引维度: {faiss_index.d if faiss_index else 'N/A'}")
            print(f"FAISS索引向量数: {faiss_index.ntotal if faiss_index else 'N/A'}")
            return jsonify({'success': False, 'error': error_msg, 'detail': error_detail}), 500
        
        # 构建结果
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx < 0:  # FAISS返回-1表示没有足够的结果
                continue
            
            resume_id = resume_mapping.get(str(idx))
            if resume_id:
                # 将距离转换为相似度分数（0-1）
                # L2距离越小，相似度越高
                score = 1.0 / (1.0 + float(distance))
                
                results.append({
                    'resume_id': resume_id,
                    'vector_index': int(idx),
                    'score': score,
                    'distance': float(distance),
                    'rank': i + 1
                })
        
        return jsonify({
            'success': True,
            'query': query,
            'results': results
        })
        
    except Exception as e:
        error_msg = f"搜索失败: {str(e)}"
        print(error_msg)
        return jsonify({'success': False, 'error': error_msg}), 500


@app.route('/api/delete', methods=['POST'])
def delete_resume():
    """
    删除简历向量
    POST /api/delete
    {
        "resume_id": 1
    }
    """
    global faiss_index, resume_mapping
    
    try:
        data = request.json
        resume_id = data.get('resume_id')
        
        if not resume_id:
            return jsonify({'error': '缺少resume_id'}), 400
        
        # 查找并删除
        indices_to_remove = []
        for idx, rid in list(resume_mapping.items()):
            if rid == resume_id:
                indices_to_remove.append(int(idx))
                del resume_mapping[idx]
        
        if indices_to_remove:
            # 注意：FAISS不支持直接删除，需要重建索引
            # 这里简化处理，标记为已删除
            print(f"删除简历 {resume_id} 的向量，索引: {indices_to_remove}")
            save_faiss_index()
            return jsonify({'success': True, 'deleted_indices': indices_to_remove})
        else:
            return jsonify({'error': '未找到该简历的向量'}), 404
        
    except Exception as e:
        print(f"删除失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def stats():
    """获取统计信息"""
    return jsonify({
        'vector_count': faiss_index.ntotal if faiss_index else 0,
        'resume_count': len(resume_mapping),
        'vector_dimension': VECTOR_DIMENSION,
        'ollama_url': OLLAMA_BASE_URL,
        'model': OLLAMA_MODEL
    })


if __name__ == '__main__':
    # 初始化FAISS索引
    init_faiss_index()
    
    # 启动服务
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"启动简历向量化服务...")
    print(f"Ollama URL: {OLLAMA_BASE_URL}")
    print(f"模型: {OLLAMA_MODEL}")
    print(f"向量维度: {VECTOR_DIMENSION}")
    print(f"服务端口: {port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

