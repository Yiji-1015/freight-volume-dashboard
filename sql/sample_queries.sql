-- Customer-level freight volume used by the original dashboard workflow.

SELECT
    c.CU_NM,
    c.CU_ADD,
    c.SIG_KOR_NM,
    c.LAT_NO,
    c.LON_NO,
    SUM(o.BOX_TOT) AS BOX_TOT
FROM KYO_CU_MST c
JOIN KYO_OUT o
    ON o.STO_NM = c.CU_NM
GROUP BY
    c.CU_NM,
    c.CU_ADD,
    c.SIG_KOR_NM,
    c.LAT_NO,
    c.LON_NO
ORDER BY BOX_TOT DESC;

-- Monthly regional trend for dashboard line/bar charts.

SELECT
    c.REGION_GROUP,
    o.SHIP_YM,
    SUM(o.BOX_TOT) AS BOX_TOT,
    SUM(o.ORDER_CNT) AS ORDER_CNT,
    SUM(o.WEIGHT_KG) AS WEIGHT_KG
FROM KYO_CU_MST c
JOIN KYO_OUT o
    ON o.STO_NM = c.CU_NM
GROUP BY
    c.REGION_GROUP,
    o.SHIP_YM
ORDER BY
    o.SHIP_YM,
    c.REGION_GROUP;

-- Top destination districts.

SELECT
    c.SIG_KOR_NM,
    COUNT(DISTINCT c.CU_ID) AS CUSTOMER_CNT,
    SUM(o.BOX_TOT) AS BOX_TOT
FROM KYO_CU_MST c
JOIN KYO_OUT o
    ON o.STO_NM = c.CU_NM
GROUP BY c.SIG_KOR_NM
ORDER BY BOX_TOT DESC
FETCH FIRST 20 ROWS ONLY;
