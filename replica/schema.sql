-- Schéma PostgreSQL initial du produit karaoké indépendant.
-- À appliquer au projet Supabase géré une fois Auth et Storage configurés.
-- Les médias du catalogue exigent des autorisations effectives; des lignes
-- insérées ne prouvent aucun droit. Ne pas appliquer cette migration avec des
-- licences ou des morceaux fictifs.

create schema if not exists app;

create type app.performance_status as enum (
  'draft',
  'processing',
  'ready',
  'published',
  'failed',
  'deleted'
);

create type app.asset_status as enum (
  'uploading',
  'processing',
  'ready',
  'failed',
  'deleted'
);

create type app.asset_purpose as enum (
  'vocal_take',
  'edited_vocal'
);

create type app.audio_effect_preset as enum (
  'none',
  'clean',
  'warm',
  'bright',
  'room'
);

create type app.track_asset_kind as enum (
  'composition',
  'lyrics',
  'backing_recording',
  'artist_master',
  'artist_likeness'
);

create type app.duet_status as enum (
  'invited',
  'recording',
  'processing',
  'complete',
  'cancelled'
);

create type app.duet_participant_status as enum (
  'invited',
  'accepted',
  'declined',
  'recording',
  'submitted',
  'withdrawn'
);

create type app.account_deletion_status as enum (
  'queued',
  'processing',
  'failed',
  'complete'
);

create table app.user_profiles (
  user_id uuid primary key references auth.users (id) on delete cascade,
  display_name text not null check (char_length(display_name) between 1 and 80),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table app.catalog_tracks (
  id uuid primary key default gen_random_uuid(),
  title text not null check (char_length(title) between 1 and 200),
  primary_artist text not null check (char_length(primary_artist) between 1 and 200),
  language_code text not null check (language_code ~ '^[a-z]{2,3}(-[A-Z]{2})?$'),
  duration_ms integer not null check (duration_ms between 1000 and 900000),
  published boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (id, language_code)
);

create index catalog_tracks_published_language_idx
  on app.catalog_tracks (language_code, id)
  where published;

create table app.track_rights (
  id uuid primary key default gen_random_uuid(),
  track_id uuid not null references app.catalog_tracks (id) on delete cascade,
  asset_kind app.track_asset_kind not null,
  territory_code text not null check (territory_code ~ '^[A-Z]{2}$'),
  valid_from timestamptz not null,
  valid_until timestamptz,
  grant_reference text not null check (char_length(grant_reference) between 1 and 200),
  created_at timestamptz not null default now(),
  check (valid_until is null or valid_until > valid_from),
  unique (track_id, asset_kind, territory_code, valid_from)
);

create index track_rights_entitlement_lookup_idx
  on app.track_rights (track_id, territory_code, asset_kind, valid_from, valid_until);

create table app.catalog_assets (
  id uuid primary key default gen_random_uuid(),
  track_id uuid not null references app.catalog_tracks (id) on delete cascade,
  asset_kind app.track_asset_kind not null
    check (asset_kind in ('lyrics', 'backing_recording', 'artist_master')),
  bucket_name text not null default 'licensed-catalog'
    check (bucket_name = 'licensed-catalog'),
  object_key text not null unique
    check (object_key !~ '(^/|(^|/)\.\.?(/|$))'),
  content_type text not null check (
    content_type in (
      'audio/mp4',
      'audio/aac',
      'application/json',
      'application/vnd.apple.mpegurl',
      'text/vtt'
    )
  ),
  size_bytes bigint not null check (size_bytes between 1 and 1073741824),
  checksum_sha256 text not null check (checksum_sha256 ~ '^[a-f0-9]{64}$'),
  created_at timestamptz not null default now(),
  unique (id, track_id, asset_kind)
);

create index catalog_assets_track_kind_idx
  on app.catalog_assets (track_id, asset_kind);

create table app.performances (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references app.user_profiles (user_id) on delete cascade,
  track_id uuid not null references app.catalog_tracks (id) on delete restrict,
  status app.performance_status not null default 'draft',
  visible_to_public boolean not null default false,
  idempotency_key uuid not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (user_id, idempotency_key),
  unique (id, user_id),
  check (not visible_to_public or status = 'published'),
  check (status <> 'published' or visible_to_public)
);

create index performances_owner_recent_idx
  on app.performances (user_id, created_at desc);

create index performances_track_owner_idx
  on app.performances (track_id, user_id);

create index performances_published_recent_idx
  on app.performances (created_at desc)
  where visible_to_public and status = 'published';

create table app.performance_edits (
  id uuid primary key default gen_random_uuid(),
  performance_id uuid not null,
  user_id uuid not null,
  version integer not null check (version > 0),
  effect_preset app.audio_effect_preset not null default 'none',
  pitch_semitones numeric(4, 2) not null default 0
    check (pitch_semitones between -12 and 12),
  noise_reduction_enabled boolean not null default false,
  cue_offset_ms integer not null default 0
    check (cue_offset_ms between -10000 and 10000),
  created_at timestamptz not null default now(),
  unique (performance_id, version),
  unique (id, performance_id, user_id),
  foreign key (performance_id, user_id)
    references app.performances (id, user_id) on delete cascade
);

create index performance_edits_owner_idx
  on app.performance_edits (user_id, performance_id);

create index performance_edits_performance_owner_idx
  on app.performance_edits (performance_id, user_id);

create table app.performance_assets (
  id uuid primary key default gen_random_uuid(),
  performance_id uuid not null,
  user_id uuid not null,
  purpose app.asset_purpose not null,
  edit_id uuid,
  status app.asset_status not null default 'uploading',
  bucket_name text not null default 'private-recordings'
    check (bucket_name = 'private-recordings'),
  object_key text not null unique
    check (object_key !~ '(^/|(^|/)\.\.?(/|$))'),
  idempotency_key uuid not null,
  content_type text not null check (content_type in ('audio/mp4', 'audio/aac', 'audio/mpeg', 'audio/wav')),
  size_bytes bigint not null check (size_bytes between 1 and 52428800),
  duration_ms integer check (duration_ms between 1 and 900000),
  checksum_sha256 text check (checksum_sha256 is null or checksum_sha256 ~ '^[a-f0-9]{64}$'),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  foreign key (performance_id, user_id)
    references app.performances (id, user_id) on delete cascade,
  foreign key (edit_id, performance_id, user_id)
    references app.performance_edits (id, performance_id, user_id) on delete cascade,
  check (
    (purpose = 'vocal_take' and edit_id is null)
    or (purpose = 'edited_vocal' and edit_id is not null)
  ),
  unique (user_id, idempotency_key),
  unique (id, user_id)
);

create index performance_assets_owner_idx
  on app.performance_assets (user_id, performance_id);

create index performance_assets_performance_owner_idx
  on app.performance_assets (performance_id, user_id);

create index performance_assets_edit_owner_idx
  on app.performance_assets (edit_id, performance_id, user_id)
  where edit_id is not null;

create index performance_assets_pending_idx
  on app.performance_assets (updated_at)
  where status in ('uploading', 'processing');

create table app.duet_sessions (
  id uuid primary key default gen_random_uuid(),
  owner_user_id uuid not null references app.user_profiles (user_id) on delete cascade,
  track_id uuid not null references app.catalog_tracks (id) on delete restrict,
  status app.duet_status not null default 'invited',
  idempotency_key uuid not null,
  result_asset_id uuid,
  completion_key uuid unique,
  expires_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (owner_user_id, idempotency_key),
  unique (id, owner_user_id),
  check (expires_at is null or expires_at > created_at),
  check (status <> 'complete' or result_asset_id is not null),
  foreign key (result_asset_id, owner_user_id)
    references app.performance_assets (id, user_id) on delete cascade,
  unique (result_asset_id)
);

create index duet_sessions_owner_recent_idx
  on app.duet_sessions (owner_user_id, created_at desc);

create index duet_sessions_track_idx
  on app.duet_sessions (track_id);

create table app.duet_participants (
  duet_session_id uuid not null,
  owner_user_id uuid not null,
  user_id uuid not null references app.user_profiles (user_id) on delete cascade,
  participant_status app.duet_participant_status not null default 'invited',
  performance_id uuid,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (duet_session_id, user_id),
  unique (duet_session_id, performance_id),
  foreign key (duet_session_id, owner_user_id)
    references app.duet_sessions (id, owner_user_id) on delete cascade,
  foreign key (performance_id, user_id)
    references app.performances (id, user_id) on delete restrict,
  check (performance_id is null or participant_status in ('recording', 'submitted', 'withdrawn'))
);

create index duet_participants_user_recent_idx
  on app.duet_participants (user_id, updated_at desc);

create index duet_participants_owner_session_idx
  on app.duet_participants (owner_user_id, duet_session_id);

create index duet_participants_session_owner_idx
  on app.duet_participants (duet_session_id, owner_user_id);

create index duet_participants_performance_user_idx
  on app.duet_participants (performance_id, user_id)
  where performance_id is not null;

create table app.performance_shares (
  id uuid primary key default gen_random_uuid(),
  performance_id uuid not null,
  user_id uuid not null,
  token_hash text not null unique check (token_hash ~ '^[a-f0-9]{64}$'),
  expires_at timestamptz not null,
  revoked_at timestamptz,
  idempotency_key uuid not null,
  created_at timestamptz not null default now(),
  foreign key (performance_id, user_id)
    references app.performances (id, user_id) on delete cascade,
  unique (user_id, idempotency_key),
  check (expires_at > created_at),
  check (revoked_at is null or revoked_at >= created_at)
);

create index performance_shares_owner_recent_idx
  on app.performance_shares (user_id, created_at desc);

create index performance_shares_performance_owner_idx
  on app.performance_shares (performance_id, user_id);

create index performance_shares_live_expiry_idx
  on app.performance_shares (expires_at)
  where revoked_at is null;

-- Une entrée de suivi minimale subsiste après la suppression du compte Auth
-- pour confirmer et relancer l’effacement des fichiers sans conserver de
-- renseignements personnels sur l’utilisateur.
create table app.account_deletion_requests (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users (id) on delete set null,
  idempotency_key uuid not null,
  status app.account_deletion_status not null default 'queued',
  error_code text check (error_code is null or char_length(error_code) between 1 and 80),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  completed_at timestamptz,
  unique (user_id, idempotency_key),
  check ((status = 'complete') = (completed_at is not null))
);

create index account_deletion_requests_pending_idx
  on app.account_deletion_requests (updated_at)
  where status in ('queued', 'processing', 'failed');

create function app.set_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at := pg_catalog.now();
  return new;
end;
$$;

create trigger user_profiles_set_updated_at
  before update on app.user_profiles
  for each row execute function app.set_updated_at();

create trigger catalog_tracks_set_updated_at
  before update on app.catalog_tracks
  for each row execute function app.set_updated_at();

create trigger performances_set_updated_at
  before update on app.performances
  for each row execute function app.set_updated_at();

create trigger performance_assets_set_updated_at
  before update on app.performance_assets
  for each row execute function app.set_updated_at();

create trigger duet_sessions_set_updated_at
  before update on app.duet_sessions
  for each row execute function app.set_updated_at();

create trigger duet_participants_set_updated_at
  before update on app.duet_participants
  for each row execute function app.set_updated_at();

create trigger account_deletion_requests_set_updated_at
  before update on app.account_deletion_requests
  for each row execute function app.set_updated_at();

alter table app.user_profiles enable row level security;
alter table app.catalog_tracks enable row level security;
alter table app.catalog_assets enable row level security;
alter table app.track_rights enable row level security;
alter table app.performances enable row level security;
alter table app.performance_edits enable row level security;
alter table app.performance_assets enable row level security;
alter table app.duet_sessions enable row level security;
alter table app.duet_participants enable row level security;
alter table app.performance_shares enable row level security;
alter table app.account_deletion_requests enable row level security;

-- Les clients lisent leurs propres lignes privées et modifient seulement leur
-- nom affiché. Toutes les mutations du catalogue, des enregistrements, des
-- téléversements, des duos et des partages passent par des fonctions Edge
-- fiables qui vérifient l’identité, la propriété, l’état et les droits en
-- vigueur avant d’effectuer les changements dans une transaction.
create policy "profiles_select_self"
  on app.user_profiles for select to authenticated
  using (user_id = (select auth.uid()));

create policy "profiles_insert_self"
  on app.user_profiles for insert to authenticated
  with check (user_id = (select auth.uid()));

create policy "profiles_update_self"
  on app.user_profiles for update to authenticated
  using (user_id = (select auth.uid()))
  with check (user_id = (select auth.uid()));

create policy "performances_select_owner"
  on app.performances for select to authenticated
  using (user_id = (select auth.uid()));

create policy "performance_edits_select_owner"
  on app.performance_edits for select to authenticated
  using (user_id = (select auth.uid()));

create policy "performance_assets_select_owner"
  on app.performance_assets for select to authenticated
  using (user_id = (select auth.uid()));

create policy "duet_sessions_select_member"
  on app.duet_sessions for select to authenticated
  using (
    owner_user_id = (select auth.uid())
    or exists (
      select 1
      from app.duet_participants dp
      where dp.duet_session_id = duet_sessions.id
        and dp.owner_user_id = duet_sessions.owner_user_id
        and dp.user_id = (select auth.uid())
        and dp.participant_status in ('invited', 'accepted', 'recording', 'submitted')
    )
  );

create policy "duet_participants_select_member"
  on app.duet_participants for select to authenticated
  using (
    owner_user_id = (select auth.uid())
    or user_id = (select auth.uid())
  );

create policy "performance_shares_select_owner"
  on app.performance_shares for select to authenticated
  using (user_id = (select auth.uid()));

create policy "account_deletion_requests_select_self"
  on app.account_deletion_requests for select to authenticated
  using (user_id = (select auth.uid()));

revoke all on schema app from public, anon, authenticated;
grant usage on schema app to anon, authenticated;
grant select on app.user_profiles to authenticated;
grant insert (user_id, display_name) on app.user_profiles to authenticated;
grant update (display_name) on app.user_profiles to authenticated;
grant select on app.account_deletion_requests to authenticated;
grant select on app.performances to authenticated;
grant select on app.performance_edits to authenticated;
grant select on app.performance_assets to authenticated;
grant select on app.duet_sessions to authenticated;
grant select on app.duet_participants to authenticated;
grant select on app.performance_shares to authenticated;

-- Le rôle de l’API fiable accède aux données après vérification du JWT, de la
-- propriété des lignes, des transitions d’état et des droits territoriaux en
-- vigueur. Il est réservé au serveur; ne jamais transmettre ses identifiants
-- à une application cliente.
grant usage on schema app to service_role;
grant all privileges on all tables in schema app to service_role;
grant execute on function app.set_updated_at() to service_role;
alter default privileges in schema app
  grant all privileges on tables to service_role;
