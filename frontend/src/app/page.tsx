"use client";

import { useState, useEffect } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Project {
  id: number;
  current_step: string;
  team_profile: string;
  diagnosis: string;
  email_draft: string;
  syllabus: string;
  facilitators: string;
  final_report: string;
}

const stepLabels: Record<string, string> = {
  start: "Inicio",
  diagnosis: "1. Diagnóstico",
  email: "2. Correo de Convocatoria",
  syllabus: "3. Syllabus",
  facilitators: "4. Facilitadores",
  completed: "5. Reporte Final",
};

// Perfil del equipo por defecto caso de prueba
const DEFAULT_TEAM_PROFILE = `EQUIPO DE VENTAS DE VENTAMAX S.A.S.

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
- 40 vendedores senior (+3 años): Mentoría y liderazgo`;

export default function Home() {
  const [projectId, setProjectId] = useState<number | null>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [teamProfile, setTeamProfile] = useState("");
  const [isEditingProfile, setIsEditingProfile] = useState(false);

  // Crear proyecto al iniciar
  useEffect(() => {
    fetchTeamProfile();
    createProject();
  }, []);

  const fetchTeamProfile = async () => {
    try {
      const res = await fetch(`${API_URL}/api/agente_ia/config/team-profile`);
      const data = await res.json();
      setTeamProfile(data.team_profile);
    } catch (e) {
      setTeamProfile(DEFAULT_TEAM_PROFILE);
    }
  };

  const saveTeamProfile = async () => {
    try {
      await fetch(`${API_URL}/api/agente_ia/config/team-profile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ team_profile: teamProfile }),
      });
      setIsEditingProfile(false);
    } catch (e) {
      console.error("Error saving team profile:", e);
    }
  };

  const createProject = async () => {
    try {
      const res = await fetch(`${API_URL}/api/agente_ia/project`, { method: "POST" });
      const data = await res.json();
      setProjectId(data.project_id);
      await fetchProject(data.project_id);
    } catch (e) {
      console.error("Error creating project:", e);
    }
  };

  const fetchProject = async (id: number) => {
    try {
      const res = await fetch(`${API_URL}/api/agente_ia/project/${id}`);
      const data = await res.json();
      setProject(data);
    } catch (e) {
      console.error("Error fetching project:", e);
    }
  };

  const executeAction = async (action: string, feedbackText?: string) => {
    if (!projectId) return;
    
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/agente_ia/project/${projectId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, feedback: feedbackText || null }),
      });
      const data = await res.json();
      
      // Si el reset creó un nuevo proyecto, cambiar a él
      if (data.project_id && action === "reset") {
        setProjectId(data.project_id);
        await fetchProject(data.project_id);
      } else {
        await fetchProject(projectId);
      }
      setFeedback("");
    } catch (e) {
      console.error("Error executing action:", e);
    } finally {
      setIsLoading(false);
    }
  };

  const renderContent = () => {
    if (!project) return <div className="loading">Cargando...</div>;

    const step = project.current_step;

    // Selección de paso basada en el estado actual
    if (step === "start") {
      return (
        <div className="step-content">
          <p>Este agente simula el rol de un Decano Académico para VentaMax S.A.S.</p>
          
          {/* Sección de perfil del equipo */}
          <div className="team-profile-section">
            <div className="section-header">
              <h4>Perfil del Equipo</h4>
              <button 
                className="btn btn-small"
                onClick={() => setIsEditingProfile(!isEditingProfile)}
              >
                {isEditingProfile ? "Cancelar" : "Editar"}
              </button>
            </div>
            
            {isEditingProfile ? (
              <div className="profile-edit">
                <textarea
                  className="profile-textarea"
                  value={teamProfile}
                  onChange={(e) => setTeamProfile(e.target.value)}
                />
                <button 
                  className="btn btn-primary"
                  onClick={saveTeamProfile}
                  style={{ marginTop: "10px" }}
                >
                  Guardar Perfil
                </button>
              </div>
            ) : (
              <pre className="profile-display">{teamProfile}</pre>
            )}
          </div>
          
          <button 
            className="btn btn-primary" 
            onClick={() => executeAction("next")}
            style={{ marginTop: "20px" }}
            disabled={isLoading}
          >
            {isLoading ? "Ejecutando..." : "Iniciar Workflow →"}
          </button>
        </div>
      );
    }

    if (step === "diagnosis") {
      return (
        <div className="step-content">
          <h3>1. Diagnóstico del Equipo</h3>
          <div className="content-box">
            <pre>{project.diagnosis}</pre>
          </div>
          <div className="step-actions">
            <button 
              className="btn btn-primary" 
              onClick={() => executeAction("approve")}
              disabled={isLoading}
            >
              ✓ Aprobar y Continuar
            </button>
            <button 
              className="btn btn-danger" 
              onClick={() => executeAction("reject", feedback)}
              disabled={isLoading || !feedback}
            >
              ✗ Rechazar
            </button>
            <textarea
              className="feedback-input"
              placeholder="Feedback (requerido para rechazar)..."
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
            />
          </div>
        </div>
      );
    }

    if (step === "email") {
      return (
        <div className="step-content">
          <h3>2. Correo de Convocatoria</h3>
          <div className="email-box">
            <pre>{project.email_draft}</pre>
          </div>
          <div className="step-actions">
            <button 
              className="btn btn-primary" 
              onClick={() => executeAction("approve")}
              disabled={isLoading}
            >
              ✓ Aprobar y Continuar
            </button>
            <button 
              className="btn btn-danger" 
              onClick={() => executeAction("reject", feedback)}
              disabled={isLoading || !feedback}
            >
              ✗ Rechazar
            </button>
            <textarea
              className="feedback-input"
              placeholder="Feedback para modificar el correo..."
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
            />
          </div>
        </div>
      );
    }

    if (step === "syllabus") {
      return (
        <div className="step-content">
          <h3>3. Syllabus - Contenidos del Programa</h3>
          <div className="content-box">
            <pre>{project.syllabus}</pre>
          </div>
          <div className="step-actions">
            <button 
              className="btn btn-primary" 
              onClick={() => executeAction("approve")}
              disabled={isLoading}
            >
              ✓ Aprobar Syllabus
            </button>
            <button 
              className="btn btn-danger" 
              onClick={() => executeAction("reject", feedback)}
              disabled={isLoading || !feedback}
            >
              ✗ Rechazar Módulo
            </button>
            <textarea
              className="feedback-input"
              placeholder="Qué módulo modificar..."
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
            />
          </div>
        </div>
      );
    }

    if (step === "facilitators") {
      return (
        <div className="step-content">
          <h3>4. Asignación de Facilitadores</h3>
          <div className="content-box">
            <pre>{project.facilitators}</pre>
          </div>
          <div className="step-actions">
            <button 
              className="btn btn-primary" 
              onClick={() => executeAction("approve")}
              disabled={isLoading}
            >
              ✓ Aprobar y Generar Reporte
            </button>
            <button 
              className="btn btn-danger" 
              onClick={() => executeAction("reject", feedback)}
              disabled={isLoading || !feedback}
            >
              ✗ Rechazar
            </button>
            <textarea
              className="feedback-input"
              placeholder="Feedback..."
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
            />
          </div>
        </div>
      );
    }

    if (step === "completed") {
      return (
        <div className="step-content completed">
          <h3>5. Reporte Final</h3>
          <div className="content-box final-report">
            <pre>{project.final_report}</pre>
          </div>
          <div className="success-box">
            ✓ Workflow Completado
          </div>
          <button 
            className="btn btn-secondary" 
            onClick={() => executeAction("reset")}
            style={{ marginTop: "20px" }}
          >
            Nuevo Proyecto
          </button>
        </div>
      );
    }

    return <div>Cargando paso...</div>;
  };

  return (
    <>
      <header className="header">
        <div className="container">
          <h1>Kometa — Agente IA Decano</h1>
          <p>Reto C: Decano Académico VentaMax S.A.S. by Jean Carlo Sanchez Parra</p>
        </div>
      </header>

      <main className="main">
        <div className="container">
          {/* Progress Steps */}
          <div className="steps">
            {Object.entries(stepLabels).map(([key, label]) => (
              <div 
                key={key} 
                className={`step ${project?.current_step === key ? "active" : ""} ${["start","diagnosis","email","syllabus","facilitators","completed"].includes(key) ? "done" : ""}`}
              >
                {label}
              </div>
            ))}
          </div>

          {/* Current Step Indicator */}
          <div className="current-step">
            Paso actual: <strong>{stepLabels[project?.current_step || "start"]}</strong>
          </div>

          {/* Content */}
          <div className="card main-content">
            {renderContent()}
          </div>
        </div>
      </main>
    </>
  );
}