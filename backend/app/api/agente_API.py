"""
FastAPI Application - Agente IA
Kometa Prueba Técnica - Reto C
"""

from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Cargar variables de entorno
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Importar funciones del agente
from app.agent.agente_ia import (
    create_tables,
    get_project,
    create_project,
    execute_workflow,
    get_db_connection,
    get_saved_team_profile,
    TEAM_PROFILE,
)

# Inicializar tablas
create_tables()

# ============================================
# API ROUTES
# ============================================
router = APIRouter(prefix="/api/agente_ia", tags=["agente_ia"])


class AgenteAction(BaseModel):
    """Acción para el agente."""
    action: str = "next"
    feedback: Optional[str] = None


class TeamProfileUpdate(BaseModel):
    """Perfil del equipo para actualizar."""
    team_profile: str


@router.post("/project", status_code=201)
async def create_agente_project():
    """Crea un nuevo proyecto de agente."""
    project_id = create_project()
    return {"project_id": project_id, "message": "Proyecto creado"}


@router.get("/project/{project_id}")
async def get_agente_project(project_id: int):
    """Obtiene el estado del proyecto."""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return project


@router.post("/project/{project_id}")
async def execute_agente_action(project_id: int, request: AgenteAction):
    """Ejecuta una acción en el proyecto."""
    result = execute_workflow(
        project_id,
        action=request.action,
        feedback=request.feedback
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Error"))
    
    return result


@router.get("/config/team-profile")
async def get_team_profile():
    """Obtiene el perfil del equipo configurable."""
    profile = get_saved_team_profile()
    return {"team_profile": profile}


@router.post("/config/team-profile")
async def update_team_profile(request: TeamProfileUpdate):
    """Actualiza el perfil del equipo para proyectos nuevos."""
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO decano_projects (current_step, team_profile) VALUES ('start', ?)",
        (request.team_profile,)
    )
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "Perfil del equipo guardado"}


# ============================================
# FASTAPI APP
# ============================================
app = FastAPI(
    title="Kometa - Agente IA",
    description="Reto C: Agente Académico VentaMax S.A.S.",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002", "http://127.0.0.1:3000", "http://127.0.1:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Kometa - Agente IA"}


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy"}


# Incluir rutas del agente
app.include_router(router)