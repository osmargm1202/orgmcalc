-- Migration 0002: Calculations and relationships
-- Creates: calculos, calculo_empresas, calculo_ingenieros
-- NOTE: Using TEXT for IDs to maintain compatibility with orgmbt UUIDs

-- Calculations per project
CREATE TABLE IF NOT EXISTS calculos (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    codigo TEXT NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    estado TEXT DEFAULT 'borrador',
    fecha_creacion DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, codigo)
);

-- Editable company links per calculation
CREATE TABLE IF NOT EXISTS calculo_empresas (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    calculo_id TEXT NOT NULL REFERENCES calculos(id) ON DELETE CASCADE,
    empresa_id TEXT NOT NULL REFERENCES empresas(id) ON DELETE RESTRICT,
    rol TEXT, -- e.g., 'constructor', 'interventor', 'disenador'
    orden INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(calculo_id, empresa_id, rol)
);

-- Editable engineer links per calculation
CREATE TABLE IF NOT EXISTS calculo_ingenieros (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    calculo_id TEXT NOT NULL REFERENCES calculos(id) ON DELETE CASCADE,
    ingeniero_id TEXT NOT NULL REFERENCES ingenieros(id) ON DELETE RESTRICT,
    rol TEXT, -- e.g., 'responsable', 'revisor', 'calculista'
    orden INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(calculo_id, ingeniero_id, rol)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_calculos_project ON calculos(project_id);
CREATE INDEX IF NOT EXISTS idx_calculos_codigo ON calculos(codigo);
CREATE INDEX IF NOT EXISTS idx_calculo_empresas_calculo ON calculo_empresas(calculo_id);
CREATE INDEX IF NOT EXISTS idx_calculo_empresas_empresa ON calculo_empresas(empresa_id);
CREATE INDEX IF NOT EXISTS idx_calculo_ingenieros_calculo ON calculo_ingenieros(calculo_id);
CREATE INDEX IF NOT EXISTS idx_calculo_ingenieros_ingeniero ON calculo_ingenieros(ingeniero_id);
