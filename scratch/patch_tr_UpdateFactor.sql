-- ==========================================
-- Patch to prevent DolarBCV from being NULLed
-- on 0-row updates to SACONF.
-- Date: 2026-06-23
-- ==========================================
ALTER TRIGGER tr_UpdateFactor ON dbo.SACONF AFTER UPDATE
AS BEGIN
    SET NOCOUNT ON;
    
    -- Prevent execution if no rows were actually affected
    IF NOT EXISTS (SELECT 1 FROM inserted)
        RETURN;

    IF UPDATE(Factor)
    BEGIN
        DECLARE @newFactor FLOAT;
        SELECT @newFactor = Factor FROM inserted;

        -- Extra safety check
        IF @newFactor IS NULL
            RETURN;

        IF EXISTS (SELECT 1 FROM dolartoday WHERE CAST(fecha AS DATE) = CAST(GETDATE() AS DATE))
        BEGIN
            UPDATE dolartoday
            SET DolarBCV = @newFactor,
                DifCamb = CASE WHEN Dolartoday IS NOT NULL AND @newFactor > 0 THEN ROUND(Dolartoday / @newFactor, 6) ELSE DifCamb END
            WHERE id = (SELECT TOP 1 id FROM dolartoday WHERE CAST(fecha AS DATE) = CAST(GETDATE() AS DATE) ORDER BY id DESC);
        END
        ELSE
        BEGIN
            INSERT INTO dolartoday (Fecha, _fecha, _hora, Dolartoday, DolarBCV, pendiente, DifCamb)
            VALUES (GETDATE(), dbo.sfAA_FechaClarion(GETDATE()), dbo.sfAA_HoraClarion(GETDATE()), NULL, @newFactor, 1, NULL);
        END
    END
END;
