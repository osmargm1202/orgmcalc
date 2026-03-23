-- Migration 0003: File assets metadata
-- Creates: file_assets for metadata-driven file status

CREATE TABLE IF NOT EXISTS file_assets (
    id SERIAL PRIMARY KEY,
    -- Polymorphic owner reference
    owner_type TEXT NOT NULL, -- 'project', 'empresa', 'ingeniero', 'calculo', 'documento'
    owner_id INTEGER NOT NULL,
    
    -- File metadata
    asset_type TEXT NOT NULL, -- 'logo', 'perfil', 'carnet', 'certificacion', 'documento', 'adjunto'
    filename TEXT NOT NULL,
    original_name TEXT,
    content_type TEXT,
    size_bytes INTEGER,
    
    -- Storage reference
    storage_key TEXT NOT NULL, -- Path in R2/S3 bucket
    storage_bucket TEXT NOT NULL DEFAULT 'orgmcalc-uploads',
    
    -- Status tracking (single-active replacement)
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Audit
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    uploaded_by INTEGER, -- Future: link to users table
    
    -- Soft unique constraint: only one active asset per owner+type
    CONSTRAINT unique_active_asset UNIQUE NULLS NOT DISTINCT (owner_type, owner_id, asset_type, is_active)
    DEFERRABLE INITIALLY DEFERRED
);

-- Partial index to enforce single-active semantics efficiently
CREATE UNIQUE INDEX IF NOT EXISTS idx_file_assets_active_unique
ON file_assets(owner_type, owner_id, asset_type)
WHERE is_active = TRUE AND is_deleted = FALSE;

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_file_assets_owner ON file_assets(owner_type, owner_id);
CREATE INDEX IF NOT EXISTS idx_file_assets_storage ON file_assets(storage_key);
CREATE INDEX IF NOT EXISTS idx_file_assets_active ON file_assets(is_active) WHERE is_active = TRUE;
