-- Extract CFE service addresses for all RPUs with at least one CFDI on file.
-- Read-only. Run against the main project (or dev once data is seeded) to refresh sites.json.
-- Address lives in the CFE addenda block clsRegArchFact of each bill XML:
--   CALLE1 / CALLE2 = "between streets" (often a landmark, e.g. "HOTEL FIESTA INN")
--   COLONIA carries CFE layout junk suffixes; CODIGO_POSTAL is the service CP (reliable).
WITH latest AS (
  SELECT DISTINCT ON (rpu) rpu, xml
  FROM raw_clients.cfdi
  ORDER BY rpu, loaded_at DESC
), parsed AS (
  SELECT rpu,
    substring(xml from '<CALLE1>([^<]*)</CALLE1>')               AS calle1,
    substring(xml from '<CALLE2>([^<]*)</CALLE2>')               AS calle2,
    substring(xml from '<COLONIA>([^<]*)</COLONIA>')             AS colonia,
    substring(xml from '<CODIGO_POSTAL>([^<]*)</CODIGO_POSTAL>') AS cp
  FROM latest
)
SELECT json_build_object(
  'rpu', p.rpu,
  'client_name', r.client_name,
  'tariff', r.tariff,
  'calle1', trim(p.calle1),
  'calle2', trim(p.calle2),
  'colonia', trim(regexp_replace(p.colonia, '\s{2,}.*$', '')),  -- drop CFE suffix junk
  'cp', p.cp,
  'municipio', (SELECT s.municipio FROM ref.sepomex_cp s WHERE s.cp = p.cp LIMIT 1),
  'estado',    (SELECT s.estado    FROM ref.sepomex_cp s WHERE s.cp = p.cp LIMIT 1)
)
FROM parsed p
LEFT JOIN client.rpu r ON r.rpu = p.rpu
ORDER BY p.rpu;
