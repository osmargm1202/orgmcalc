-- Migration 0001: Consolidated initial schema (development reset)
-- Final state includes clientes + current runtime domain model.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Companies / Empresas (global registry)
CREATE TABLE IF NOT EXISTS empresas (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    logo_url TEXT,
    url TEXT,
    contacto TEXT,
    telefono TEXT,
    correo TEXT,
    direccion TEXT,
    ciudad TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Project clients (can reference empresa, fallback data, or both)
CREATE TABLE IF NOT EXISTS clientes (
    id TEXT PRIMARY KEY,
    empresa_id TEXT REFERENCES empresas(id) ON DELETE RESTRICT,
    nombre TEXT,
    ubicacion TEXT,
    telefono TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Projects (each project can reference one cliente)
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    cliente_id TEXT REFERENCES clientes(id) ON DELETE SET NULL,
    ubicacion TEXT,
    fecha DATE,
    estado TEXT DEFAULT 'activo',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Engineers / Ingenieros (global registry)
CREATE TABLE IF NOT EXISTS ingenieros (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    email TEXT,
    telefono TEXT,
    codia TEXT,
    id_empresas TEXT DEFAULT '',
    foto_perfil_url TEXT,
    foto_carnet_url TEXT,
    foto_certificacion_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Calculation types catalog
CREATE TABLE IF NOT EXISTS tipo_calculos (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    categoria TEXT,
    icono TEXT,
    color TEXT,
    orden INTEGER DEFAULT 0,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

INSERT INTO tipo_calculos (codigo, nombre, descripcion, categoria, icono, color, orden) VALUES
    ('BT', 'Cálculo de Baja Tensión', 'Cálculo de instalaciones eléctricas de baja tensión (120V-480V)', 'electricidad', '⚡', '#FFD700', 1),
    ('SPT', 'Sistema de Puesta a Tierra de Subestación', 'Cálculo y diseño de sistemas de puesta a tierra para subestaciones eléctricas', 'subestacion', '🌍', '#8B4513', 2),
    ('AC', 'Capacidad de Aire Acondicionado', 'Cálculo de carga térmica y selección de equipos de climatización', 'climatizacion', '❄️', '#00BFFF', 3),
    ('ILUM', 'Cálculo de Iluminación', 'Cálculo de niveles de iluminación y diseño lumínico', 'electricidad', '💡', '#FFFF00', 4),
    ('TDF', 'Transformadores', 'Selección y cálculo de transformadores', 'electricidad', '🔌', '#4682B4', 5),
    ('CCM', 'Centros de Carga', 'Distribución y protección en centros de carga motores', 'electricidad', '⚙️', '#696969', 6),
    ('DESC', 'Descargas Atmosféricas', 'Sistema de protección contra descargas atmosféricas (SPDA)', 'electricidad', '⛈️', '#4B0082', 7),
    ('LTMT', 'Líneas de Transmisión Media Tensión', 'Cálculo y diseño de líneas de transmisión en media tensión (13.8kV - 34.5kV)', 'transmision', '🏗️', '#9370DB', 8),
    ('LTAT', 'Líneas de Transmisión Alta Tensión', 'Cálculo y diseño de líneas de transmisión en alta tensión (>34.5kV)', 'transmision', '🔺', '#DC143C', 9),
    ('SAUX', 'Servicios Auxiliares de Subestación', 'Cálculo de servicios auxiliares para subestaciones (iluminación, fuerza, HVAC)', 'subestacion', '🔧', '#20B2AA', 10),
    ('FOTOV', 'Sistemas Fotovoltaicos', 'Cálculo de sistemas solares fotovoltaicos', 'electricidad', '☀️', '#FFA500', 11)
ON CONFLICT (codigo) DO UPDATE SET
    nombre = EXCLUDED.nombre,
    descripcion = EXCLUDED.descripcion,
    categoria = EXCLUDED.categoria,
    icono = EXCLUDED.icono,
    color = EXCLUDED.color,
    orden = EXCLUDED.orden,
    activo = TRUE;

UPDATE tipo_calculos SET activo = FALSE WHERE codigo IN ('EMER', 'CARGAS');

-- Calculations per project (one empresa + one ingeniero per cálculo)
CREATE TABLE IF NOT EXISTS calculos (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    tipo_calculo_id TEXT REFERENCES tipo_calculos(id) ON DELETE RESTRICT,
    codigo TEXT NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    estado TEXT DEFAULT 'borrador',
    fecha_creacion DATE DEFAULT CURRENT_DATE,
    empresa_id TEXT NOT NULL REFERENCES empresas(id) ON DELETE RESTRICT,
    ingeniero_id TEXT NOT NULL REFERENCES ingenieros(id) ON DELETE RESTRICT,
    parametros JSONB DEFAULT '{}'::jsonb,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(project_id, codigo),
    CONSTRAINT chk_calculo_has_empresa CHECK (empresa_id IS NOT NULL),
    CONSTRAINT chk_calculo_has_ingeniero CHECK (ingeniero_id IS NOT NULL)
);

-- Documents per project
CREATE TABLE IF NOT EXISTS documentos (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    nombre_documento TEXT NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- File assets metadata
CREATE TABLE IF NOT EXISTS file_assets (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    owner_type TEXT NOT NULL,
    owner_id TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    filename TEXT NOT NULL,
    original_name TEXT,
    content_type TEXT,
    size_bytes INTEGER,
    storage_key TEXT NOT NULL,
    storage_bucket TEXT NOT NULL DEFAULT 'orgmcalc-uploads',
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    uploaded_by TEXT,
    CONSTRAINT unique_active_asset UNIQUE NULLS NOT DISTINCT (owner_type, owner_id, asset_type, is_active)
    DEFERRABLE INITIALLY DEFERRED
);

-- Indexes for common lookups
CREATE INDEX IF NOT EXISTS idx_empresas_nombre ON empresas(nombre);

CREATE INDEX IF NOT EXISTS idx_clientes_empresa ON clientes(empresa_id);
CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON clientes(nombre);

CREATE INDEX IF NOT EXISTS idx_projects_nombre ON projects(nombre);
CREATE INDEX IF NOT EXISTS idx_projects_cliente_id ON projects(cliente_id);

CREATE INDEX IF NOT EXISTS idx_ingenieros_nombre ON ingenieros(nombre);
CREATE INDEX IF NOT EXISTS idx_ingenieros_email ON ingenieros(email);
CREATE INDEX IF NOT EXISTS idx_ingenieros_empresas ON ingenieros(id_empresas) WHERE id_empresas != '';

CREATE INDEX IF NOT EXISTS idx_tipo_calculos_activo ON tipo_calculos(activo) WHERE activo = TRUE;
CREATE INDEX IF NOT EXISTS idx_tipo_calculos_orden ON tipo_calculos(orden);
CREATE INDEX IF NOT EXISTS idx_tipo_calculos_categoria ON tipo_calculos(categoria);

CREATE INDEX IF NOT EXISTS idx_calculos_project ON calculos(project_id);
CREATE INDEX IF NOT EXISTS idx_calculos_codigo ON calculos(codigo);
CREATE INDEX IF NOT EXISTS idx_calculos_empresa ON calculos(empresa_id);
CREATE INDEX IF NOT EXISTS idx_calculos_ingeniero ON calculos(ingeniero_id);
CREATE INDEX IF NOT EXISTS idx_calculos_tipo ON calculos(tipo_calculo_id);

CREATE INDEX IF NOT EXISTS idx_documentos_project ON documentos(project_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_file_assets_active_unique
ON file_assets(owner_type, owner_id, asset_type)
WHERE is_active = TRUE AND is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_file_assets_owner ON file_assets(owner_type, owner_id);
CREATE INDEX IF NOT EXISTS idx_file_assets_storage ON file_assets(storage_key);
CREATE INDEX IF NOT EXISTS idx_file_assets_active ON file_assets(is_active) WHERE is_active = TRUE;
