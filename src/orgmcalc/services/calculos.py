"""Calculos service - business logic with empresa/ingeniero validation."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status

from orgmcalc.db.connection import get_sync_connection
from orgmcalc.repositories.calculos import CalculosRepository


class CalculosService:
    """Service for calculation business logic.

    Validates that:
    1. Each calculation has exactly one empresa and one ingeniero
    2. The ingeniero can work for the assigned empresa (or works for all)
    """

    @staticmethod
    async def list_calculos(
        project_id: str, offset: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        """List calculations for a project."""
        return await CalculosRepository.list_by_project(project_id, offset, limit)

    @staticmethod
    async def get_calculo(calculo_id: str) -> dict[str, Any] | None:
        """Get calculation by ID."""
        return await CalculosRepository.get_by_id(calculo_id)

    @staticmethod
    def _validate_ingeniero_can_work_for_empresa(ingeniero_id: str, empresa_id: str) -> bool:
        """Check if engineer can work for the given company.

        In orgmbt, ingenieros.id_empresas can be:
        - Empty string: works for all companies
        - Comma-separated list: works only for those specific companies
        """
        conn = get_sync_connection()
        try:
            with conn.cursor() as cur:
                # Get ingeniero's allowed empresas
                cur.execute("SELECT id_empresas FROM ingenieros WHERE id = %s", (ingeniero_id,))
                row = cur.fetchone()

                if not row:
                    return False

                id_empresas = row[0] or ""

                # Empty string means works for all
                if not id_empresas or id_empresas.strip() == "":
                    return True

                # Check if empresa_id is in the list
                allowed_empresas = [e.strip() for e in id_empresas.split(",")]
                return empresa_id in allowed_empresas
        finally:
            conn.close()

    @staticmethod
    def _empresa_exists(empresa_id: str) -> bool:
        """Check if empresa exists."""
        conn = get_sync_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM empresas WHERE id = %s", (empresa_id,))
                return cur.fetchone() is not None
        finally:
            conn.close()

    @staticmethod
    def _ingeniero_exists(ingeniero_id: str) -> bool:
        """Check if ingeniero exists."""
        conn = get_sync_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM ingenieros WHERE id = %s", (ingeniero_id,))
                return cur.fetchone() is not None
        finally:
            conn.close()

    @staticmethod
    async def create_calculo(data: dict[str, Any]) -> dict[str, Any]:
        """Create calculation with empresa and ingeniero validation."""
        empresa_id = data.get("empresa_id")
        ingeniero_id = data.get("ingeniero_id")

        # Validate empresa exists
        if not empresa_id or not CalculosService._empresa_exists(empresa_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Empresa con ID '{empresa_id}' no existe",
            )

        # Validate ingeniero exists
        if not ingeniero_id or not CalculosService._ingeniero_exists(ingeniero_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ingeniero con ID '{ingeniero_id}' no existe",
            )

        # Validate ingeniero can work for this empresa
        if not CalculosService._validate_ingeniero_can_work_for_empresa(ingeniero_id, empresa_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El ingeniero '{ingeniero_id}' no está autorizado a trabajar para la empresa '{empresa_id}'",
            )

        # Check unique codigo per project
        existing = await CalculosRepository.get_by_codigo_and_project(
            data["project_id"], data["codigo"]
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un cálculo con el código '{data['codigo']}' en este proyecto",
            )

        return await CalculosRepository.create(data)

    @staticmethod
    async def update_calculo(calculo_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
        """Update calculation with empresa/ingeniero validation if changed."""
        empresa_id = data.get("empresa_id")
        ingeniero_id = data.get("ingeniero_id")

        # If empresa is being changed, validate it exists
        if empresa_id is not None:
            if not CalculosService._empresa_exists(empresa_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Empresa con ID '{empresa_id}' no existe",
                )

        # If ingeniero is being changed, validate it exists and can work for empresa
        if ingeniero_id is not None:
            if not CalculosService._ingeniero_exists(ingeniero_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ingeniero con ID '{ingeniero_id}' no existe",
                )

            # If changing ingeniero, need to check against current or new empresa
            check_empresa_id = empresa_id
            if check_empresa_id is None and ingeniero_id is not None:
                # Get current empresa from existing calculation
                existing = await CalculosRepository.get_by_id(calculo_id)
                if existing:
                    check_empresa_id = existing.get("empresa_id")

            if check_empresa_id and not CalculosService._validate_ingeniero_can_work_for_empresa(
                ingeniero_id, check_empresa_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El ingeniero '{ingeniero_id}' no está autorizado a trabajar para la empresa '{check_empresa_id}'",
                )

        # If codigo is being changed, check uniqueness
        if "codigo" in data and data["codigo"] is not None:
            existing = await CalculosRepository.get_by_id(calculo_id)
            if existing and existing.get("codigo") != data["codigo"]:
                conflict = await CalculosRepository.get_by_codigo_and_project(
                    existing["project_id"], data["codigo"]
                )
                if conflict:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Ya existe un cálculo con el código '{data['codigo']}' en este proyecto",
                    )

        return await CalculosRepository.update(calculo_id, data)

    @staticmethod
    async def delete_calculo(calculo_id: str) -> bool:
        """Delete calculation."""
        return await CalculosRepository.delete(calculo_id)

    @staticmethod
    async def calculo_exists(calculo_id: str) -> bool:
        """Check if calculation exists."""
        return await CalculosRepository.exists(calculo_id)


class CalculoEmpresasService:
    """DEPRECATED: Service for calculation-company association logic.

    This service is kept for backward compatibility but should not be used.
    Use CalculosService instead - each calculation now has empresa_id directly.
    """

    pass


class CalculoIngenierosService:
    """DEPRECATED: Service for calculation-engineer association logic.

    This service is kept for backward compatibility but should not be used.
    Use CalculosService instead - each calculation now has ingeniero_id directly.
    """

    pass
