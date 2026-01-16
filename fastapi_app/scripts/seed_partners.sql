-- Seed data for the Partner table (PostgreSQL).
-- This script inserts a fixed set plus generated fake records.

INSERT INTO partner (
    external_id,
    name,
    vat,
    email,
    phone,
    street,
    city,
    country_code,
    score,
    updated_at,
    created_at
) VALUES
    ('ext-1001', 'Comercial Andina', '20123456789', 'ventas@andina.pe', '+51 1 555-0101', 'Av. Los Olivos 123', 'Lima', 'PE', 0.72, NOW(), NOW()),
    ('ext-1002', 'Servicios Amazonia', '10456789123', 'contacto@amazonia.pe', '+51 1 555-0102', 'Jr. Amazonas 456', 'Iquitos', 'PE', 0.63, NOW(), NOW()),
    ('ext-1003', 'Insumos Pacifico', '20567891234', 'ventas@pacifico.pe', '+51 1 555-0103', 'Av. Grau 789', 'Trujillo', 'PE', 0.81, NOW(), NOW());

INSERT INTO partner (
    external_id,
    name,
    vat,
    email,
    phone,
    street,
    city,
    country_code,
    score,
    updated_at,
    created_at
)
SELECT
    'ext-' || (2000 + gs)::text,
    'Empresa Demo ' || gs::text,
    (10000000000 + floor(random() * 89999999999))::bigint::text,
    'contacto' || gs::text || '@demo.pe',
    '+51 1 55' || lpad(gs::text, 2, '0') || '-0' || lpad((gs % 100)::text, 2, '0'),
    'Calle Falsa ' || (10 + gs)::text,
    (ARRAY['Lima', 'Arequipa', 'Cusco', 'Piura', 'Iquitos'])[1 + floor(random() * 5)]::text,
    'PE',
    round((random() * 0.7 + 0.2)::numeric, 2),
    NOW() - (random() * interval '30 days'),
    NOW() - (random() * interval '30 days')
FROM generate_series(1, 50) AS gs;
