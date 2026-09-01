CREATE TABLE IF NOT EXISTS breweries (
    id UUID PRIMARY KEY,
    brewery_type TEXT NOT NULL,
    name TEXT NOT NULL,
    address_1 TEXT,
    address_2 TEXT,
    address_3 TEXT,
    city TEXT NOT NULL,
    state_province TEXT NOT NULL,
    postal_code TEXT NOT NULL,
    country TEXT NOT NULL,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    phone TEXT,
    website_url TEXT
);
