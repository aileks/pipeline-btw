from pipeline_btw.db.connection import get_connection


def load_data(data):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO breweries (
                    id,
                    brewery_type,
                    name,
                    address_1,
                    address_2,
                    address_3,
                    city,
                    state_province,
                    postal_code,
                    country,
                    longitude,
                    latitude,
                    phone,
                    website_url
                )
                VALUES (
                    %(id)s,
                    %(brewery_type)s,
                    %(name)s,
                    %(address_1)s,
                    %(address_2)s,
                    %(address_3)s,
                    %(city)s,
                    %(state_province)s,
                    %(postal_code)s,
                    %(country)s,
                    %(longitude)s,
                    %(latitude)s,
                    %(phone)s,
                    %(website_url)s
                )
                ON CONFLICT UPDATE
                """,
                data,
            )
