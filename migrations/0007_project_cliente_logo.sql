-- Migration 0007: Add cliente field to projects

ALTER TABLE projects
    ADD COLUMN IF NOT EXISTS cliente TEXT;

CREATE INDEX IF NOT EXISTS idx_projects_cliente ON projects(cliente);
