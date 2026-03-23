-- Migration 0006: Fix calculos relationships
-- Changes the model from 'calculo has many empresas/ingenieros' 
-- to 'calculo has one empresa and one ingeniero'
-- Also removes empresa/ingeniero from projects

-- Add empresa_id and ingeniero_id directly to calculos
ALTER TABLE calculos 
    ADD COLUMN IF NOT EXISTS empresa_id TEXT REFERENCES empresas(id) ON DELETE RESTRICT,
    ADD COLUMN IF NOT EXISTS ingeniero_id TEXT REFERENCES ingenieros(id) ON DELETE RESTRICT;

-- Create indexes for the new FKs
CREATE INDEX IF NOT EXISTS idx_calculos_empresa ON calculos(empresa_id);
CREATE INDEX IF NOT EXISTS idx_calculos_ingeniero ON calculos(ingeniero_id);

-- Remove empresa/ingeniero from projects (they shouldn't be there)
ALTER TABLE projects 
    DROP COLUMN IF EXISTS id_empresa,
    DROP COLUMN IF EXISTS id_ingeniero;

-- Add constraint to ensure calculo has both empresa and ingeniero
-- Note: This is a business rule - every calculation must have an assigned company and engineer
ALTER TABLE calculos 
    ADD CONSTRAINT chk_calculo_has_empresa CHECK (empresa_id IS NOT NULL),
    ADD CONSTRAINT chk_calculo_has_ingeniero CHECK (ingeniero_id IS NOT NULL);

-- Drop the old many-to-many tables (optional - if you want to keep history, skip this)
-- Uncomment if you want to completely remove them:
-- DROP TABLE IF EXISTS calculo_empresas CASCADE;
-- DROP TABLE IF EXISTS calculo_ingenieros CASCADE;

-- For now, we'll keep them but deprecate them
COMMENT ON TABLE calculo_empresas IS 'DEPRECATED: Use calculos.empresa_id instead';
COMMENT ON TABLE calculo_ingenieros IS 'DEPRECATED: Use calculos.ingeniero_id instead';
