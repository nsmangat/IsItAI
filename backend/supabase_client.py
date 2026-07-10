from supabase import Client, create_client

import config

"""
Creates a Supabase client for the pipeline scripts to read/write with
Uses the service_role key so writes (fetch/analyze/upload scripts) bypass RLS
ONLY USED SERVER SIDE WITH SECRET KEY
"""

def get_client() -> Client:

    if not config.SUPABASE_URL or not config.SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_URL / SUPABASE_KEY in .env not set. "
            "Get these from Supabase project dashboard (Project Settings -> API Keys) "
        )

    return create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
