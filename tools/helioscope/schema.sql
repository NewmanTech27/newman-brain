-- Results table for the HelioScope route. APPLY ON THE dev BRANCH ONLY (never main/staging).
create table if not exists client.helioscope_site (
  rpu text primary key references client.rpu(rpu),
  lat double precision,
  lng double precision,
  place_id text,
  confidence smallint not null,          -- 0-100
  tier text not null check (tier in ('HIGH','MEDIUM','LOW')),
  evidence jsonb not null default '[]',  -- human-readable signals behind the score
  solar_roof_m2 numeric,
  solar_max_panels integer,
  helioscope_project_id text,
  helioscope_design_id text,
  helioscope_simulation_id text,
  status text not null default 'pending',-- pending | designed | needs_review | rejected
  reviewed_by text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table client.helioscope_site enable row level security;
