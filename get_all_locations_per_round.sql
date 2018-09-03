use WaSSCollections

SELECT
    MAP_X as x,
    MAP_Y as y,
    LLPG_LatLng_Lat AS lat,
    LLPG_LatLng_Lng AS lng,
    ADDRESS_STR AS addr,
    STREETNAME AS street,
    TOWN_NAME AS town,
    PCODE AS postcode,
    UPRN as uprn,
    REF as REF,
    RECY as RECY,
    MIX as MIX,
    GLASS as GLASS,
    GW as GW
FROM (
    SELECT
        xy.MAP_X,
        xy.MAP_Y,
        xy.ADDRESS_STR,
        xy.STREETNAME,
        xy.TOWN_NAME,
        xy.PCODE,
        xy.UPRN,
        ll.LLPG_LatLng_Lat,
        ll.LLPG_LatLng_Lng,
        CASE
			WHEN newREF = 0 THEN NULL 
            WHEN newREF <> 0 AND oldREF <> newREF THEN newREF
            ELSE NULL 
        END AS REF,
        CASE 
            WHEN newRECY = 0 THEN NULL 
            WHEN newRECY <> 0 AND oldRECY <> newRECY THEN newRECY
            ELSE NULL 
        END AS RECY,
        CASE 
			WHEN newMIX = 0 THEN NULL 
            WHEN newMIX <> 0 AND oldMIX <> newMIX THEN newMIX
            ELSE NULL 
        END AS MIX,
        CASE 
			WHEN newGLASS = 0 THEN NULL 
            WHEN newGLASS <> 0 AND oldGLASS <> newGLASS THEN newGLASS
			ELSE NULL 
        END AS GLASS,
        CASE 
            WHEN newGW = 0 THEN NULL 
            WHEN newGW <> 0 AND oldGW <> newGW THEN newGW
            ELSE NULL 
        END AS GW
    FROM
        dbo.MV_HDC_LLPG_ADDRESSES_CURRENT xy
        INNER JOIN
        WaSSCollections.dbo.LLPG_LatLng AS ll
        ON
            xy.UPRN = ll.LLPG_LatLng_UPRN
        LEFT JOIN (
            SELECT
            UPRN,
            ISNULL([REF], 0) AS oldREF,
            ISNULL([RECY], 0) AS oldRECY,
            ISNULL([MIX], 0) AS oldMIX,
            ISNULL([GLASS], 0) AS oldGLASS,
            ISNULL([GW], 0) AS oldGW
        FROM (
                  SELECT
                UPRN,
                psr.ServiceID,
                MIN(r.RoundID) AS RoundID
            FROM dbo.PropertyServiceRounds_I_180831_102636 psr
                LEFT JOIN (
                        SELECT *
                FROM dbo.Rounds
                WHERE roundera = 2
                  ) r
                ON psr.RoundID = r.RoundID AND psr.ServiceID = r.ServiceID
            WHERE psr.RoundEra = 2
            GROUP BY UPRN, psr.ServiceID
            ) a
            PIVOT (
                  MIN(RoundID)
                  FOR serviceid
                  IN ([REF], [RECY], [MIX], [GLASS], [GW])
            ) pvt 
    ) o on xy.uprn = o.uprn
        LEFT JOIN (
            SELECT
            UPRN,
            ISNULL([REF], 0) AS newREF,
            ISNULL([RECY], 0) AS newRECY,
            ISNULL([MIX], 0) AS newMIX,
            ISNULL([GLASS], 0) AS newGLASS,
            ISNULL([GW], 0) AS newGW
            FROM (
                SELECT
                    UPRN,
                    psr.ServiceID,
                    MIN(r.RoundID) as RoundID
                FROM dbo.PropertyServiceRounds psr
                    LEFT JOIN (
                        SELECT *
                        FROM dbo.Rounds
                        WHERE roundera = 2
                    ) r
                    ON psr.RoundID = r.RoundID and psr.ServiceID = r.ServiceID
                WHERE psr.RoundEra = 2
                GROUP BY uprn, psr.ServiceID
            ) a
            PIVOT (
                MIN(RoundID)
                FOR serviceid IN ([REF], [RECY], [MIX], [GLASS], [GW])
            ) pvt 
        ) n
        ON xy.uprn = n.uprn
    WHERE (
        oldREF <> newREF OR
        oldRECY <> newRECY OR
        oldMIX <> newMIX OR
        oldGLASS <> newGLASS OR
        oldGW <> newGW
    )
) a
WHERE GW = 1