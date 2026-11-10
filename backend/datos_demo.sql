-- Ejecutar en pgAdmin sobre la base de datos de Django después de migrate.
-- Datos ficticios. Si se repite la carga, se conservan los registros existentes.
BEGIN;

INSERT INTO complejos_complejo (nombre, descripcion, ciudad, direccion, activo)
VALUES
    ('Demo Norte', 'Complejo ficticio para pruebas', 'Quito', 'Sector norte', TRUE),
    ('Demo Sur', 'Complejo ficticio para pruebas', 'Quito', 'Sector sur', TRUE)
ON CONFLICT (LOWER(nombre), LOWER(ciudad)) DO NOTHING;

INSERT INTO complejos_cancha (complejo_id, nombre, deporte, capacidad, activa)
SELECT complejo.id, demo.cancha, demo.deporte, demo.capacidad, TRUE
FROM (VALUES
    ('Demo Norte', 'Fútbol Norte', 'FUTBOL', 14),
    ('Demo Norte', 'Pádel Norte', 'PADEL', 4),
    ('Demo Sur', 'Básquet Sur', 'BASQUET', 10),
    ('Demo Sur', 'Vóley Sur', 'VOLEY', 12)
) AS demo(complejo, cancha, deporte, capacidad)
JOIN complejos_complejo AS complejo
    ON LOWER(complejo.nombre) = LOWER(demo.complejo)
    AND LOWER(complejo.ciudad) = 'quito'
ON CONFLICT (LOWER(nombre), complejo_id) DO NOTHING;

-- Lunes (0) a domingo (6), de 08:00 a 20:00.
INSERT INTO complejos_horarioatencion (cancha_id, dia_semana, apertura, cierre)
SELECT cancha.id, dia.numero, TIME '08:00', TIME '20:00'
FROM complejos_cancha AS cancha
JOIN complejos_complejo AS complejo ON complejo.id = cancha.complejo_id
CROSS JOIN generate_series(0, 6) AS dia(numero)
WHERE LOWER(complejo.ciudad) = 'quito'
    AND (LOWER(complejo.nombre), LOWER(cancha.nombre)) IN (
        ('demo norte', 'fútbol norte'), ('demo norte', 'pádel norte'),
        ('demo sur', 'básquet sur'), ('demo sur', 'vóley sur')
    )
    AND NOT EXISTS (
        SELECT 1
        FROM complejos_horarioatencion AS horario
        WHERE horario.cancha_id = cancha.id AND horario.dia_semana = dia.numero
            AND horario.apertura < TIME '20:00' AND horario.cierre > TIME '08:00'
    );

-- Tarifa por cancha y día para todo el horario de atención.
INSERT INTO complejos_tarifa (cancha_id, dia_semana, inicio, fin, valor_hora, activa)
SELECT cancha.id, dia.numero, TIME '08:00', TIME '20:00', demo.valor_hora, TRUE
FROM (VALUES
    ('demo norte', 'fútbol norte', 25.00),
    ('demo norte', 'pádel norte', 18.00),
    ('demo sur', 'básquet sur', 20.00),
    ('demo sur', 'vóley sur', 16.00)
) AS demo(complejo, cancha, valor_hora)
JOIN complejos_complejo AS complejo
    ON LOWER(complejo.nombre) = demo.complejo AND LOWER(complejo.ciudad) = 'quito'
JOIN complejos_cancha AS cancha
    ON cancha.complejo_id = complejo.id AND LOWER(cancha.nombre) = demo.cancha
CROSS JOIN generate_series(0, 6) AS dia(numero)
WHERE NOT EXISTS (
    SELECT 1
    FROM complejos_tarifa AS tarifa
    WHERE tarifa.cancha_id = cancha.id AND tarifa.dia_semana = dia.numero
        AND tarifa.inicio < TIME '20:00' AND tarifa.fin > TIME '08:00'
);

COMMIT;
