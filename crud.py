from sqlalchemy.orm import Session
from models import Item
from schemas import ItemCreate, ItemUpdate
from typing import List, Optional

class ItemCRUD:
    @staticmethod
    def create_item(db: Session, item: ItemCreate) -> Item:
        """Crear un nuevo item"""
        db_item = Item(**item.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    
    @staticmethod
    def get_item(db: Session, item_id: int) -> Optional[Item]:
        """Obtener un item por ID"""
        return db.query(Item).filter(Item.id == item_id).first()
    
    @staticmethod
    def get_items(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Item]:
        """Obtener lista de items con paginación"""
        query = db.query(Item)
        if active_only:
            query = query.filter(Item.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_item(db: Session, item_id: int, item_update: ItemUpdate) -> Optional[Item]:
        """Actualizar un item existente"""
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if not db_item:
            return None
        
        update_data = item_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_item, field, value)
        
        db.commit()
        db.refresh(db_item)
        return db_item
    
    @staticmethod
    def delete_item(db: Session, item_id: int) -> bool:
        """Eliminar un item (eliminación física)"""
        db_item = db.query(Item).filter(Item.id == item_id).first()
        if not db_item:
            return False
        
        db.delete(db_item)
        db.commit()
        return True
    
    @staticmethod
    def soft_delete_item(db: Session, item_id: int) -> Optional[Item]:
        """Eliminación lógica (marcar como inactivo)"""
        return ItemCRUD.update_item(db, item_id, ItemUpdate(is_active=False))