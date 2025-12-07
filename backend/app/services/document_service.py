"""
文档管理服务 - 处理文档的CRUD和向量化
"""
from typing import List, Dict, Optional
import uuid
from pathlib import Path
import logging

from app.db.database import get_db
from app.db.models import Document
from app.services.vector_store import vector_store_service
from sqlalchemy import desc

logger = logging.getLogger(__name__)


class DocumentService:
    """文档管理服务"""
    
    @staticmethod
    def generate_doc_id() -> str:
        """生成文档ID"""
        return f"doc_{uuid.uuid4().hex[:16]}"
    
    @staticmethod
    def create_document(
        user_id: str,
        file_name: str,
        file_path: str,
        file_size: int,
        file_type: str
    ) -> str:
        """
        创建文档记录
        
        Returns:
            文档ID
        """
        doc_id = DocumentService.generate_doc_id()
        
        with get_db() as db:
            document = Document(
                doc_id=doc_id,
                user_id=user_id,
                file_name=file_name,
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                status='processing'
            )
            db.add(document)
        
        logger.info(f"📄 Created document record: {doc_id}")
        return doc_id
    
    @staticmethod
    def update_document_status(
        doc_id: str,
        status: str,
        num_chunks: int = 0,
        error_message: str = None
    ) -> bool:
        """更新文档状态"""
        with get_db() as db:
            document = db.query(Document).filter(
                Document.doc_id == doc_id
            ).first()
            
            if not document:
                return False
            
            document.status = status
            document.num_chunks = num_chunks
            if error_message:
                document.error_message = error_message
            
            return True
    
    @staticmethod
    async def process_document(
        file_path: str,
        user_id: str,
        file_name: str,
        file_size: int,
        file_type: str
    ) -> Dict:
        """
        完整的文档处理流程
        
        1. 创建数据库记录
        2. 摄取到向量库
        3. 更新状态
        """
        # 1. 创建记录
        doc_id = DocumentService.create_document(
            user_id=user_id,
            file_name=file_name,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type
        )
        
        try:
            # 2. 摄取到向量库
            result = vector_store_service.ingest_document(
                file_path=file_path,
                user_id=user_id,
                doc_id=doc_id
            )
            
            if result['success']:
                # 3. 更新为成功状态
                DocumentService.update_document_status(
                    doc_id=doc_id,
                    status='completed',
                    num_chunks=result['num_chunks']
                )
                
                return {
                    'success': True,
                    'doc_id': doc_id,
                    'num_chunks': result['num_chunks'],
                    'file_name': file_name
                }
            else:
                # 更新为失败状态
                DocumentService.update_document_status(
                    doc_id=doc_id,
                    status='failed',
                    error_message=result.get('error', 'Unknown error')
                )
                
                return {
                    'success': False,
                    'error': result.get('error')
                }
                
        except Exception as e:
            logger.error(f"❌ Document processing failed: {e}")
            DocumentService.update_document_status(
                doc_id=doc_id,
                status='failed',
                error_message=str(e)
            )
            
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_user_documents(user_id: str) -> List[Dict]:
        """获取用户的所有文档"""
        with get_db() as db:
            documents = db.query(Document).filter(
                Document.user_id == user_id
            ).order_by(desc(Document.created_at)).all()
            
            return [
                {
                    'doc_id': doc.doc_id,
                    'file_name': doc.file_name,
                    'file_type': doc.file_type,
                    'file_size': doc.file_size,
                    'num_chunks': doc.num_chunks,
                    'status': doc.status,
                    'error_message': doc.error_message,
                    'created_at': doc.created_at.isoformat()
                }
                for doc in documents
            ]
    
    @staticmethod
    def get_document(doc_id: str) -> Optional[Dict]:
        """获取单个文档信息"""
        with get_db() as db:
            document = db.query(Document).filter(
                Document.doc_id == doc_id
            ).first()
            
            if not document:
                return None
            
            return {
                'doc_id': document.doc_id,
                'user_id': document.user_id,
                'file_name': document.file_name,
                'file_path': document.file_path,
                'file_type': document.file_type,
                'file_size': document.file_size,
                'num_chunks': document.num_chunks,
                'status': document.status,
                'error_message': document.error_message,
                'created_at': document.created_at.isoformat()
            }
    
    @staticmethod
    def delete_document(doc_id: str, user_id: str) -> bool:
        """
        删除文档
        
        1. 从向量库删除
        2. 删除文件
        3. 删除数据库记录
        """
        with get_db() as db:
            document = db.query(Document).filter(
                Document.doc_id == doc_id,
                Document.user_id == user_id
            ).first()
            
            if not document:
                return False
            
            try:
                # 1. 从向量库删除
                vector_store_service.delete_document(user_id, doc_id)
                
                # 2. 删除文件
                file_path = Path(document.file_path)
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"🗑️  Deleted file: {file_path}")
                
                # 3. 删除数据库记录
                db.delete(document)
                
                logger.info(f"✅ Document {doc_id} deleted successfully")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to delete document: {e}")
                return False
    
    @staticmethod
    def get_stats(user_id: str) -> Dict:
        """获取用户的文档统计"""
        with get_db() as db:
            total = db.query(Document).filter(
                Document.user_id == user_id
            ).count()
            
            completed = db.query(Document).filter(
                Document.user_id == user_id,
                Document.status == 'completed'
            ).count()
            
            processing = db.query(Document).filter(
                Document.user_id == user_id,
                Document.status == 'processing'
            ).count()
            
            failed = db.query(Document).filter(
                Document.user_id == user_id,
                Document.status == 'failed'
            ).count()
            
            total_chunks = db.query(Document).filter(
                Document.user_id == user_id,
                Document.status == 'completed'
            ).with_entities(
                db.func.sum(Document.num_chunks)
            ).scalar() or 0
            
            return {
                'total_documents': total,
                'completed': completed,
                'processing': processing,
                'failed': failed,
                'total_chunks': total_chunks
            }