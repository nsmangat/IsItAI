-- Metadata per image
create table if not exists images (
    id uuid primary key default gen_random_uuid(),
    source text not null,              
    is_ai boolean not null,
    attribution text not null default '',
    public_url text not null,
    created_at timestamptz not null default now()
);

-- Analysis data to evaluate how likely an image was AI generated and why
create table if not exists analyses (
    id uuid primary key default gen_random_uuid(),
    image_id uuid not null references images(id) on delete cascade,
    confidence float not null,
    signals jsonb not null default '[]',
    created_at timestamptz not null default now()
);

-- Public reads for frontend to be able to access
alter table images enable row level security;
alter table analyses enable row level security;

create policy "Public read access" on images
    for select using (true);

create policy "Public read access" on analyses
    for select using (true);
