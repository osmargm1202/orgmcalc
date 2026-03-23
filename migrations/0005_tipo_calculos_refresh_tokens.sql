-- Migration 0005: Calculation types and refresh tokens
-- Creates: tipo_calculos table with predefined calculation types
-- Updates: auth_sessions to support refresh tokens with 2-hour inactivity expiry

-- Calculation types (predefined list - cannot be created arbitrarily)
CREATE TABLE IF NOT EXISTS tipo_calculos (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    codigo TEXT UNIQUE NOT NULL, -- e.g., 'BT', 'SPT', 'AC', 'ILUM', 'CARGAS'
    nombre TEXT NOT NULL, -- e.g., 'Cálculo de Baja Tensión'
    descripcion TEXT,
    categoria TEXT, -- e.g., 'electricidad', 'mecanica', 'climatizacion'
    icono TEXT, -- emoji or icon name
    color TEXT, -- hex color for UI
    orden INTEGER DEFAULT 0, -- display order
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert predefined calculation types
INSERT INTO tipo_calculos (codigo, nombre, descripcion, categoria, icono, color, orden) VALUES
    ('BT', 'Cálculo de Baja Tensión', 'Cálculo de instalaciones eléctricas de baja tensión (120V-480V)', 'electricidad', '⚡', '#FFD700', 1),
    ('SPT', 'Sistema de Puesta a Tierra', 'Cálculo y diseño de sistemas de puesta a tierra', 'electricidad', '🌍', '#8B4513', 2),
    ('AC', 'Capacidad de Aire Acondicionado', 'Cálculo de carga térmica y selección de equipos de climatización', 'climatizacion', '❄️', '#00BFFF', 3),
    ('ILUM', 'Cálculo de Iluminación', 'Cálculo de niveles de iluminación y diseño lumínico', 'electricidad', '💡', '#FFFF00', 4),
    ('CARGAS', 'Cálculo de Cargas Eléctricas', 'Balance de cargas, demanda y factor de diversidad', 'electricidad', '📊', '#FF6347', 5),
    ('TDF', 'Transformadores', 'Selección y cálculo de transformadores', 'electricidad', '🔌', '#4682B4', 6),
    ('CCM', 'Centros de Carga', 'Distribución y protección en centros de carga motores', 'electricidad', '⚙️', '#696969', 7),
    ('DESC', 'Descargas Atmosféricas', 'Sistema de protección contra descargas atmosféricas (SPDA)', 'electricidad', '⛈️', '#4B0082', 8),
    ('EMER', 'Sistemas de Emergencia', 'Cálculo de sistemas de iluminación y alimentación de emergencia', 'electricidad', '🚨', '#FF0000', 9),
    ('FOTOV', 'Sistemas Fotovoltaicos', 'Cálculo de sistemas solares fotovoltaicos', 'electricidad', '☀️', '#FFA500', 10)
ON CONFLICT (codigo) DO NOTHING;

-- Update calculos table to reference tipo_calculos
ALTER TABLE calculos 
    ADD COLUMN IF NOT EXISTS tipo_calculo_id TEXT REFERENCES tipo_calculos(id) ON DELETE RESTRICT,
    ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1,
    ADD COLUMN IF NOT EXISTS parametros JSONB DEFAULT '{}'::jsonb; -- calculation-specific parameters

-- Index for tipo_calculos
CREATE INDEX IF NOT EXISTS idx_tipo_calculos_activo ON tipo_calculos(activo) WHERE activo = TRUE;
CREATE INDEX IF NOT EXISTS idx_tipo_calculos_orden ON tipo_calculos(orden);
CREATE INDEX IF NOT EXISTS idx_tipo_calculos_categoria ON tipo_calculos(categoria);
CREATE INDEX IF NOT EXISTS idx_calculos_tipo ON calculos(tipo_calculo_id);

-- Update auth_sessions to support refresh tokens with sliding expiry
ALTER TABLE auth_sessions 
    ADD COLUMN IF NOT EXISTS refresh_token_hash VARCHAR(255) UNIQUE,
    ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ADD COLUMN IF NOT EXISTS max_inactive_hours INTEGER DEFAULT 2; -- expire after 2 hours of inactivity

-- Create index for refresh token lookups
CREATE INDEX IF NOT EXISTS idx_auth_sessions_refresh_token ON auth_sessions(refresh_token_hash) WHERE refresh_token_hash IS NOT NULL;

-- Function to update last_activity_at on token use
CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_activity_at = NOW();
    -- Reset expires_at to 2 hours from now (sliding window)
    NEW.expires_at = NOW() + INTERVAL '2 hours';
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update activity timestamp
DROP TRIGGER IF EXISTS trg_update_session_activity ON auth_sessions;
CREATE TRIGGER trg_update_session_activity
    BEFORE UPDATE ON auth_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_session_activity();
