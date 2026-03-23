-- Migration 0001: Initial schema
-- Creates: schema_migrations (managed by runner), projects, empresas, ingenieros
-- NOTE: Using TEXT for IDs to maintain compatibility with orgmbt UUIDs

-- Projects table
-- NOTE: Projects don't have empresa/ingeniero directly.
-- Each calculation (calculo) has its own empresa and ingeniero assignment.
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    ubicacion TEXT,
    fecha DATE,
    estado TEXT DEFAULT 'activo',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Companies/Empresas (global registry)
CREATE TABLE IF NOT EXISTS empresas (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    logo_url TEXT,
    contacto TEXT,
    telefono TEXT,
    correo TEXT,
    direccion TEXT,
    ciudad TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Engineers/Ingenieros (global registry)
-- id_empresas: empty string = works for all companies, comma-separated list = specific companies
CREATE TABLE IF NOT EXISTS ingenieros (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT,
    telefono TEXT,
    profesion TEXT,
    id_empresas TEXT DEFAULT '', -- comma-separated list or empty for all
    foto_perfil_url TEXT,
    foto_carnet_url TEXT,
    foto_certificacion_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for common lookups
CREATE INDEX IF NOT EXISTS idx_projects_nombre ON projects(nombre);
CREATE INDEX IF NOT EXISTS idx_empresas_nombre ON empresas(nombre);
CREATE INDEX IF NOT EXISTS idx_ingenieros_nombre ON ingenieros(nombre);
CREATE INDEX IF NOT EXISTS idx_ingenieros_email ON ingenieros(email);
CREATE INDEX IF NOT EXISTS idx_ingenieros_empresas ON ingenieros(id_empresas) WHERE id_empresas != '';
