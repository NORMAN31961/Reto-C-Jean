"""
Agente IA Decano - Reto C
 workflow: Diagnóstico → Correo → Syllabus → Facilitadores → Reporte
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from openai import OpenAI


# ============================================
# DATABASE
# ============================================
def get_db_path():
    """Get database path."""
    return Path(__file__).parent.parent.parent / "data.db"


def get_db_connection():
    """Conexión a SQLite."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    """Crea las tablas necesarias si no estan creadas ."""
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS decano_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            current_step TEXT NOT NULL DEFAULT 'start',
            team_profile TEXT,
            diagnosis TEXT,
            email_draft TEXT,
            syllabus TEXT,
            facilitators TEXT,
            final_report TEXT,
            user_feedback TEXT,
            approved INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# ============================================
# DATOS DEL EQUIPO
# ============================================
TEAM_PROFILE = """
EQUIPO DE VENTAS DE VENTAMAX S.A.S.

• 150 empleados, fuerza de ventas de 40 personas
• Experiencia: 6 meses a 5 años
• Mercado: Colombia,México, Perú
• Productos: Software B2B para PyMEs
• Meta actual: $1000M/mes
• Tasa cierre: 18% subir al 30%
• Problema principal: dificultad para manejar objeciones de precio, cierre de ventas y prospeccion
• Formación actual: Solo onboarding inicial

PERFILES DETECTADOS:
- 50 vendedores nuevos (< 1 año): Necesitan cierre y objeciones
- 60 vendedores intermedios (1-3 años): Técnicas avanzadas
- 40 vendedores senior (+3 años): Mentoría y liderazgo
"""


# ============================================
# OPENAI CLIENT
# ============================================
def get_openai_client():
    """Get OpenAI client."""
    
    return OpenAI()

# ============================================
# STEP FUNCTIONS
# ============================================
def step1_diagnosis(feedback: str = None) -> str:
    """Paso 1: Diagnóstico del equipo."""
    try:
        client = get_openai_client() 
        
        # Usar perfil guardado en DB (o el default)
        team_profile = get_saved_team_profile()
        
        # Agregar contexto de memoria si hay proyectos anteriores
        memory_context = get_project_memory_context()
        
        prompt = f"""Eres un Decano Académico de VentaMax S.A.S. Analiza el perfil del equipo de ventas y detecta las brechas de conocimiento más importantes. 
        
        Perfil del equipo: {team_profile} 
        
        Proporciona un diagnóstico que incluya: 
        1. Fortalezas del equipo 
        2. Brechas identificadas (mínimo 5) 
        3. Áreas críticas a mejorar 
        4. Recomendaciones de formación 
        Formato estructurado: 
        
        **Responde en texto plano, sin formato Markdown ni caracteres especiales (no uses *, , #, guiones ni listas)**
        """
        if feedback:
            prompt += f"\n\nNOTA DEL USUARIO (resolver en el diagnóstico): {feedback}"
        
        if memory_context:
            prompt += memory_context

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return f"ERROR: {str(e)}"


def step2_email(diagnosis: str, feedback: str = None) -> str:
    """Paso 2: Correo de convocatoria."""
    client = get_openai_client()
    
    memory_context = get_project_memory_context()
    
    prompt = f"""Eres el Decano Académico de VentaMax S.A.S. Redacta un correo de convocatoria 
    al equipo de ventas para el programa de formación.

    Contexto del diagnóstico:
    {diagnosis[:1000]}

    El correo debe incluir:
    1. Asunto atractivo
    2. Saludo formal
    3. Introducción sobre la importancia de la formación
    4. Beneficios para ellos
    5. Fechas sugeridas
    6. Llamado a la acción
    7. Firma: "Equipo de Formación VentaMax"

    Formato de correo completo:
    **Responde en texto plano, sin formato Markdown ni caracteres especiales (no uses *, , #, guiones ni listas)**
    """

    if feedback:
        prompt += f"\n\nNOTA DEL USUARIO (corregir en el correo): {feedback}"
    
    if memory_context:
        prompt += memory_context

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return response.choices[0].message.content


def step3_syllabus(diagnosis: str, feedback: str = None) -> str:
    """Paso 3: Syllabus del programa."""
    client = get_openai_client()
    
    memory_context = get_project_memory_context()
    
    prompt = f"""Eres el Decano Académico de VentaMax S.A.S. Diseña un programa de formación 
    para el equipo de ventas basado en el diagnóstico.

    Diagnóstico:
    {diagnosis[:1000]}

    El programa debe tener MÍNIMO 6 módulos con:
    - Nombre del módulo
    - Duración (horas)
    - Descripción breve
    - Objetivos de aprendizaje
    - Metodología

    Estructura el syllabus completo:
    **Responde en texto plano, sin formato Markdown ni caracteres especiales (no uses *, , #, guiones ni listas)**
    
    """

    if feedback:
        prompt += f"\n\nNOTA DEL USUARIO (aplicar al syllabus): {feedback}"
    
    if memory_context:
        prompt += memory_context

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response.choices[0].message.content


def step4_facilitators(syllabus: str, feedback: str = None) -> str:
    """Paso 4: Asignación de facilitadores."""
    client = get_openai_client()
    
    memory_context = get_project_memory_context()
    
    prompt = f"""Eres el Decano Académico de VentaMax S.A.S. Asigna un facilitador interno 
    adecuado para cada módulo del programa.

    Programa de formación:
    {syllabus[:1500]}

    PERFILES DE FACILITADORES INTERNOS:
    • María González (5 años): Experta en cierre y negociación
    • Carlos Ruiz (4 años): Especialista en producto B2B
    • Ana Martínez (3 años): Técnica de manejo de objeciones
    • Pedro Suárez (4 años): Líder de ventas, mentoría
    • Laura Chen (3 años): Negociación corporativa

    Asigna a cada módulo un facilitador y justifica por qué es la mejor elección. No dejes ningun módulo sin facilitador.
    **Responde en texto plano, sin formato Markdown ni caracteres especiales (no uses *, , #, guiones ni listas)**
    """

    if feedback:
        prompt += f"\n\nNOTA DEL USUARIO (ajustar asignación): {feedback}"
    
    if memory_context:
        prompt += memory_context

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response.choices[0].message.content


def step5_report(project_data: dict, feedback: str = None) -> str:
    """Paso 5: Reporte final."""
    client = get_openai_client()
    
    memory_context = get_project_memory_context()
    
    prompt = f"""Eres el Decano Académico de VentaMax S.A.S. Genera un reporte de avance 
    del programa de formación con métricas simuladas.

    DATOS DEL PROYECTO:
    - Diagnóstico: {project_data.get('diagnosis', '')[:500]}
    - Syllabus: {project_data.get('syllabus', '')[:500]}
    - Facilitadores: {project_data.get('facilitators', '')[:500]}

    Genera un reporte ejecutivo que incluya:
    1. Resumen ejecutivo
    2. Métricas de participación (simuladas)
    3. Métricas de logro esperadas
    4. Próximos pasos
    5. Indicadores de éxito

    Formatea profesionalmente:
    **Responde en texto plano, sin formato Markdown ni caracteres especiales (no uses *, , #, guiones ni listas)**
    """

    if feedback:
        prompt += f"\n\nNOTA DEL USUARIO: {feedback}"
    
    if memory_context:
        prompt += memory_context

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )
    return response.choices[0].message.content


# ============================================
# PROJECT FUNCTIONS
# ============================================
def get_saved_team_profile() -> str:
    """Obtiene el último perfil de equipo guardado."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT team_profile FROM decano_projects WHERE team_profile IS NOT NULL AND team_profile != '' ORDER BY id DESC LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["team_profile"]
    return TEAM_PROFILE


def create_project() -> int:
    """Crea un nuevo proyecto."""
    #Usa el perfil del equipo guardado o el perfil por defecto
    profile = get_saved_team_profile()
    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO decano_projects (current_step, team_profile) VALUES ('start', ?)",
        (profile,)
    )
    conn.commit()
    project_id = cursor.lastrowid
    conn.close()
    return project_id


def get_project(project_id: int) -> dict:
    """Obtiene un proyecto."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM decano_projects WHERE id = ?",
        (project_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_project(project_id: int, **kwargs) -> None:
    """Actualiza un proyecto."""
    conn = get_db_connection()
    set_clauses = ["updated_at = ?"]
    values = [datetime.now().isoformat()]
    
    for key, value in kwargs.items():
        set_clauses.append(f"{key} = ?")
        values.append(value)
    
    values.append(project_id)
    conn.execute(
        f"UPDATE decano_projects SET {', '.join(set_clauses)} WHERE id = ?",
        values
    )
    conn.commit()
    conn.close()


# ============================================
# MEMORY FUNCTIONS
# ============================================
def get_all_projects(limit: int = 10) -> list:
    """Obtiene todos los proyectos (para historial)."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT id, current_step, created_at, updated_at FROM decano_projects ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_similar_profiles(limit: int = 3) -> list:
    """Busca perfiles de equipo similares en proyectos anteriores."""
    conn = get_db_connection()
    cursor = conn.execute(
        """SELECT id, diagnosis, email_draft, syllabus, facilitators 
           FROM decano_projects 
           WHERE diagnosis IS NOT NULL AND diagnosis != ''
           ORDER BY id DESC 
           LIMIT ?""",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_project_memory_context() -> str:
    """Genera contexto de memoria para los prompts basedo en proyectos anteriores."""
    similar = get_similar_profiles(limit=3)
    
    context = "\n\n--- CONTEXTO DE PROYECTOS ANTERIORES ---\n"
    context += "El agente tiene acceso a proyectos anteriores similares:\n\n"
    context += "Usa esta información para mejorar tus respuestas, pero no la copies directamente.\n\n"
    for p in similar:
        context += f"Proyecto {p['id']}:\n"
        if p.get('diagnosis'):
            context += f"  Diagnóstico: {p['diagnosis'][:300]}...\n"
        if p.get('syllabus'):
            context += f"  Syllabus: {p['syllabus'][:200]}...\n"
        if p.get('facilitators'):
            context += f"  Facilitadores: {p['facilitators'][:200]}...\n"
        context += "\n"
    
    context += "--- FIN CONTEXTO ---\n"
    return context


# ============================================
# workflow ENGINE
# ============================================
def execute_workflow(project_id: int, action: str = "next", feedback: str = None) -> dict:
    """Ejecuta el workflow del agente decano."""
    
    project = get_project(project_id)
    
    if not project:
        project_id = create_project()
        project = get_project(project_id)
    
    current_step = project["current_step"]
    
    # Handle reset - create a new project
    if action == "reset":
        # Create a new project instead of clearing the current one
        new_project_id = create_project()
        new_project = get_project(new_project_id)
        return {"success": True, "step": "start", "project_id": new_project_id, "message": "Nuevo proyecto creado"}
    
    # Handle approve - advance to next step AND generate it
    if action == "approve":
        update_project(project_id, approved=1)
        
        if current_step == "start":
            diagnosis = step1_diagnosis()
            update_project(project_id, current_step="diagnosis", diagnosis=diagnosis)
            return {"success": True, "step": "diagnosis", "diagnosis": diagnosis}
        
        elif current_step == "diagnosis":
            diagnosis = project["diagnosis"]
            email = step2_email(diagnosis)
            update_project(project_id, current_step="email", email_draft=email)
            return {"success": True, "step": "email", "email": email}
        
        elif current_step == "email":
            diagnosis = project["diagnosis"]
            syllabus = step3_syllabus(diagnosis)
            update_project(project_id, current_step="syllabus", syllabus=syllabus)
            return {"success": True, "step": "syllabus", "syllabus": syllabus}
        
        elif current_step == "syllabus":
            syllabus = project["syllabus"]
            facilitators = step4_facilitators(syllabus)
            update_project(project_id, current_step="facilitators", facilitators=facilitators)
            return {"success": True, "step": "facilitators", "facilitators": facilitators}
        
        elif current_step == "facilitators":
            report = step5_report(project)
            update_project(project_id, current_step="completed", final_report=report)
            return {"success": True, "step": "completed", "report": report}
        
        return {"success": True, "step": current_step}
    
    if action == "reject":
        if not feedback:
            return {"success": False, "error": "Feedback requerido para rechazado"}
        update_project(project_id, user_feedback=feedback)
        
        # Regenerar paso actual CON feedback
        if current_step == "diagnosis":
            diagnosis = step1_diagnosis(feedback=feedback)
            update_project(project_id, diagnosis=diagnosis)
            return {"success": True, "step": "diagnosis", "diagnosis": diagnosis}
        
        elif current_step == "email":
            diagnosis = project["diagnosis"]
            email = step2_email(diagnosis, feedback=feedback)
            update_project(project_id, email_draft=email)
            return {"success": True, "step": "email", "email": email}
        
        elif current_step == "syllabus":
            diagnosis = project["diagnosis"]
            syllabus = step3_syllabus(diagnosis, feedback=feedback)
            update_project(project_id, syllabus=syllabus)
            return {"success": True, "step": "syllabus", "syllabus": syllabus}
        
        elif current_step == "facilitators":
            syllabus = project["syllabus"]
            facilitators = step4_facilitators(syllabus, feedback=feedback)
            update_project(project_id, facilitators=facilitators)
            return {"success": True, "step": "facilitators", "facilitators": facilitators}
        
        return {"success": True, "step": current_step}
    
    # Handle "next" - Ejecuta el siguiente paso
    if action == "next":
        if current_step == "start":
            diagnosis = step1_diagnosis()
            update_project(project_id, current_step="diagnosis", diagnosis=diagnosis)
            return {"success": True, "step": "diagnosis", "diagnosis": diagnosis}
        
        elif current_step == "diagnosis":
            diagnosis = project["diagnosis"]
            email = step2_email(diagnosis)
            update_project(project_id, current_step="email", email_draft=email)
            return {"success": True, "step": "email", "email": email}
        
        elif current_step == "email":
            diagnosis = project["diagnosis"]
            syllabus = step3_syllabus(diagnosis)
            update_project(project_id, current_step="syllabus", syllabus=syllabus)
            return {"success": True, "step": "syllabus", "syllabus": syllabus}
        
        elif current_step == "syllabus":
            syllabus = project["syllabus"]
            facilitators = step4_facilitators(syllabus)
            update_project(project_id, current_step="facilitators", facilitators=facilitators)
            return {"success": True, "step": "facilitators", "facilitators": facilitators}
        
        elif current_step == "facilitators":
            report = step5_report(project)
            update_project(project_id, current_step="completed", final_report=report)
            return {"success": True, "step": "completed", "report": report}
        
        return {"success": False, "error": f"No hay acción para step: {current_step}"}
    
    return {"success": False, "error": "Acción desconocida"}


create_tables()