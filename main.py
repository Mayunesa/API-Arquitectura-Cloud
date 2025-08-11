from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import uvicorn
from models import Item

from database import get_db, create_tables
from schemas import ItemCreate, ItemUpdate, ItemResponse
from crud import ItemCRUD

# Crear tablas al iniciar
create_tables()

# Inicializar FastAPI
app = FastAPI(
    title="Items CRUD API",
    description="API completa para gestión de items con operaciones CRUD",
    version="1.0.0"
)

# Instancia de CRUD
crud = ItemCRUD()

# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Endpoint de bienvenida"""
    return {
        "message": "API de Items - CRUD Completo",
        "docs": "/docs",
        "version": "1.0.0"
    }

# CREATE - Crear nuevo item
@app.post("/items/", response_model=ItemResponse, tags=["Items"])
async def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo item
    
    - **name**: Nombre del item (requerido)
    - **description**: Descripción opcional del item
    - **price**: Precio del item (debe ser mayor a 0)
    - **quantity**: Cantidad disponible (por defecto 0)
    - **is_active**: Estado del item (por defecto True)
    """
    return crud.create_item(db=db, item=item)

# READ - Obtener todos los items
@app.get("/items/", response_model=List[ItemResponse], tags=["Items"])
async def read_items(
    skip: int = Query(0, ge=0, description="Número de items a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de items a retornar"),
    active_only: bool = Query(False, description="Mostrar solo items activos"),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de items con paginación
    
    - **skip**: Número de registros a saltar para paginación
    - **limit**: Máximo número de registros a retornar
    - **active_only**: Si es True, solo retorna items activos
    """
    items = crud.get_items(db=db, skip=skip, limit=limit, active_only=active_only)
    return items

# READ - Obtener item por ID
@app.get("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
async def read_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtener un item específico por su ID
    
    - **item_id**: ID único del item
    """
    db_item = crud.get_item(db=db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return db_item

# UPDATE - Actualizar item
@app.put("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un item existente
    
    - **item_id**: ID del item a actualizar
    - Solo se actualizarán los campos proporcionados (actualización parcial)
    """
    db_item = crud.update_item(db=db, item_id=item_id, item_update=item_update)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return db_item

# DELETE - Eliminación física
@app.delete("/items/{item_id}", tags=["Items"])
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Eliminar un item permanentemente de la base de datos
    
    - **item_id**: ID del item a eliminar
    """
    success = crud.delete_item(db=db, item_id=item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return {"message": "Item eliminado exitosamente"}

# DELETE - Eliminación lógica (soft delete)
@app.patch("/items/{item_id}/deactivate", response_model=ItemResponse, tags=["Items"])
async def deactivate_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Desactivar un item (eliminación lógica)
    
    - **item_id**: ID del item a desactivar
    - El item permanece en la base de datos pero se marca como inactivo
    """
    db_item = crud.soft_delete_item(db=db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return db_item

# Endpoint adicional para estadísticas
@app.get("/items/stats/summary", tags=["Statistics"])
async def get_items_stats(db: Session = Depends(get_db)):
    """
    Obtener estadísticas básicas de los items
    """
    total_items = db.query(Item).count()
    active_items = db.query(Item).filter(Item.is_active == True).count()
    inactive_items = total_items - active_items
    
    return {
        "total_items": total_items,
        "active_items": active_items,
        "inactive_items": inactive_items
    }

# =============================================================================
# EJECUTAR SERVIDOR
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Recarga automática en desarrollo
    )