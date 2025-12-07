"""
向量存储服务 - RAG核心组件
"""
from typing import List, Dict, Optional
from pathlib import Path
import logging
from datetime import datetime

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    Docx2txtLoader,
    TextLoader
)
from langchain.schema import Document

logger = logging.getLogger(__name__)


class VectorStoreService:
    """向量数据库服务 - 使用ChromaDB"""
    
    _instance = None  # 单例模式
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, persist_directory: str = "./data/vector_db"):
        """初始化向量库"""
        if self._initialized:
            return
        
        self.persist_directory = persist_directory
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # 初始化Embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"  # 更便宜的模型
        )
        
        # 初始化向量库
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings,
            collection_name="documents"
        )
        
        # 文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,        # 每块1000字符
            chunk_overlap=200,      # 重叠200字符
            length_function=len,
            separators=["\n\n", "\n", "。", "!", "?", "；", " ", ""]
        )
        
        self._initialized = True
        logger.info("✅ VectorStoreService initialized")
    
    def load_document(self, file_path: str) -> List[Document]:
        """
        根据文件类型加载文档
        
        支持格式：.pdf, .md, .docx, .txt
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 文件类型映射
        loaders = {
            '.pdf': PyPDFLoader,
            '.md': UnstructuredMarkdownLoader,
            '.markdown': UnstructuredMarkdownLoader,
            '.docx': Docx2txtLoader,
            '.txt': TextLoader
        }
        
        loader_class = loaders.get(file_path.suffix.lower())
        if not loader_class:
            raise ValueError(
                f"不支持的文件类型: {file_path.suffix}\n"
                f"支持的类型: {', '.join(loaders.keys())}"
            )
        
        try:
            loader = loader_class(str(file_path))
            documents = loader.load()
            logger.info(f"📄 Loaded {len(documents)} pages from {file_path.name}")
            return documents
        except Exception as e:
            logger.error(f"❌ Failed to load {file_path}: {e}")
            raise
    
    def ingest_document(
        self,
        file_path: str,
        user_id: str,
        doc_id: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        摄取文档到向量库
        
        Args:
            file_path: 文件路径
            user_id: 用户ID
            doc_id: 文档ID（用于后续删除）
            metadata: 额外的元数据
            
        Returns:
            摄取结果字典
        """
        try:
            # 1. 加载文档
            documents = self.load_document(file_path)
            
            # 2. 分块
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"📝 Split into {len(chunks)} chunks")
            
            # 3. 添加元数据
            base_metadata = {
                'user_id': user_id,
                'doc_id': doc_id,
                'source': str(file_path),
                'file_name': Path(file_path).name,
                'file_type': Path(file_path).suffix,
                'ingested_at': datetime.now().isoformat()
            }
            
            if metadata:
                base_metadata.update(metadata)
            
            for i, chunk in enumerate(chunks):
                chunk.metadata.update(base_metadata)
                chunk.metadata['chunk_id'] = f"{doc_id}_chunk_{i}"
            
            # 4. 向量化并存储
            self.vectorstore.add_documents(chunks)
            
            logger.info(f"✅ Ingested {Path(file_path).name}: {len(chunks)} chunks")
            
            return {
                'success': True,
                'num_chunks': len(chunks),
                'file_name': Path(file_path).name,
                'doc_id': doc_id
            }
            
        except Exception as e:
            logger.error(f"❌ Document ingestion failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search(
        self,
        query: str,
        user_id: str,
        k: int = 3,
        score_threshold: float = 0.5
    ) -> List[Dict]:
        """
        搜索相关文档
        
        Args:
            query: 查询文本
            user_id: 用户ID（只返回该用户的文档）
            k: 返回结果数量
            score_threshold: 相似度阈值（0-1）
            
        Returns:
            搜索结果列表
        """
        try:
            # 相似度搜索（带分数）
            results = self.vectorstore.similarity_search_with_score(
                query,
                k=k * 2,  # 多获取一些，然后过滤
                filter={'user_id': user_id}
            )
            
            # 转换分数（ChromaDB返回的是距离，需要转换为相似度）
            filtered_results = []
            for doc, distance in results:
                # 距离越小越相似，转换为0-1的相似度分数
                similarity = 1 / (1 + distance)
                
                if similarity >= score_threshold:
                    filtered_results.append({
                        'content': doc.page_content,
                        'metadata': doc.metadata,
                        'score': similarity
                    })
            
            # 限制返回数量
            filtered_results = filtered_results[:k]
            
            logger.info(f"🔍 Search '{query}': found {len(filtered_results)} results")
            return filtered_results
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}")
            return []
    
    def delete_document(self, user_id: str, doc_id: str) -> bool:
        """
        删除文档的所有向量块
        
        Args:
            user_id: 用户ID
            doc_id: 文档ID
            
        Returns:
            是否删除成功
        """
        try:
            # ChromaDB的delete方法需要指定IDs
            # 我们通过元数据查询找到所有chunk_ids
            results = self.vectorstore.get(
                where={
                    "user_id": user_id,
                    "doc_id": doc_id
                }
            )
            
            if results and 'ids' in results:
                ids_to_delete = results['ids']
                self.vectorstore.delete(ids=ids_to_delete)
                logger.info(f"🗑️  Deleted {len(ids_to_delete)} chunks for doc {doc_id}")
                return True
            else:
                logger.warning(f"⚠️  No chunks found for doc {doc_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Delete failed: {e}")
            return False
    
    def get_stats(self, user_id: str) -> Dict:
        """
        获取用户的向量库统计信息
        
        Returns:
            统计信息字典
        """
        try:
            # 获取所有该用户的文档
            results = self.vectorstore.get(
                where={"user_id": user_id}
            )
            
            total_chunks = len(results['ids']) if results and 'ids' in results else 0
            
            # 统计文档数（通过doc_id去重）
            doc_ids = set()
            if results and 'metadatas' in results:
                for metadata in results['metadatas']:
                    if 'doc_id' in metadata:
                        doc_ids.add(metadata['doc_id'])
            
            return {
                'total_documents': len(doc_ids),
                'total_chunks': total_chunks,
                'user_id': user_id
            }
            
        except Exception as e:
            logger.error(f"❌ Get stats failed: {e}")
            return {
                'total_documents': 0,
                'total_chunks': 0,
                'user_id': user_id
            }


# 单例实例（全局使用）
vector_store_service = VectorStoreService()