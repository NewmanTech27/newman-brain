--
-- PostgreSQL database dump
--

\restrict bHMvRlOVdsRvAhzdxbyRECFHA7uEGz9i7XVJ9dUtFhgUjeXtWVnSb24jIUNKyY2

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.10 (Ubuntu 17.10-1.pgdg24.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: crm; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA crm;


--
-- Name: collateral_status; Type: TYPE; Schema: crm; Owner: -
--

CREATE TYPE crm.collateral_status AS ENUM (
    'draft',
    'pending_approval',
    'active',
    'released',
    'rejected'
);


--
-- Name: collateral_type; Type: TYPE; Schema: crm; Owner: -
--

CREATE TYPE crm.collateral_type AS ENUM (
    'fideicomiso_garantia',
    'fideicomiso_administracion',
    'garantia_mobiliaria',
    'dsra_cash_reserve',
    'aval_obligado_solidario',
    'cesion_derechos_cfe'
);


--
-- Name: dd_status; Type: TYPE; Schema: crm; Owner: -
--

CREATE TYPE crm.dd_status AS ENUM (
    'not_started',
    'in_progress',
    'cleared',
    'blocked'
);


--
-- Name: deal_stage; Type: TYPE; Schema: crm; Owner: -
--

CREATE TYPE crm.deal_stage AS ENUM (
    'lead',
    'earlies',
    'forwards',
    'docs',
    'in_signing',
    'closed',
    'stand_by',
    'perdido'
);


--
-- Name: itp_status; Type: TYPE; Schema: crm; Owner: -
--

CREATE TYPE crm.itp_status AS ENUM (
    'pending',
    'submitted',
    'inspected_pass',
    'inspected_fail',
    'conditional'
);


--
-- Name: line_type; Type: TYPE; Schema: crm; Owner: -
--

CREATE TYPE crm.line_type AS ENUM (
    'epc',
    'ppa',
    'bess',
    'arrendamiento'
);


--
-- Name: perfection_status; Type: TYPE; Schema: crm; Owner: -
--

CREATE TYPE crm.perfection_status AS ENUM (
    'unperfected',
    'in_process',
    'perfected'
);


--
-- Name: po_status; Type: TYPE; Schema: crm; Owner: -
--

CREATE TYPE crm.po_status AS ENUM (
    'draft',
    'pending_approval',
    'issued',
    'partially_received',
    'received',
    'invoiced',
    'closed',
    'cancelled'
);


--
-- Name: proposal_status; Type: TYPE; Schema: crm; Owner: -
--

CREATE TYPE crm.proposal_status AS ENUM (
    'draft',
    'sent',
    'viewed',
    'signed',
    'declined',
    'expired',
    'void'
);


--
-- Name: rel_type; Type: TYPE; Schema: crm; Owner: -
--

CREATE TYPE crm.rel_type AS ENUM (
    'parent',
    'subsidiary',
    'guarantor',
    'affiliate'
);


--
-- Name: todo_status; Type: TYPE; Schema: crm; Owner: -
--

CREATE TYPE crm.todo_status AS ENUM (
    'pipeline',
    'in_progress',
    'done',
    'blocker'
);


--
-- Name: user_role; Type: TYPE; Schema: crm; Owner: -
--

CREATE TYPE crm.user_role AS ENUM (
    'admin',
    'member',
    'guest',
    'compliance'
);


--
-- Name: _band_dscr(numeric); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._band_dscr(v numeric) RETURNS integer
    LANGUAGE sql IMMUTABLE
    AS $$
  select case when v is null then 3 when v>=1.40 then 5 when v>=1.25 then 4 when v>=1.15 then 3 when v>=1.05 then 2 else 1 end $$;


--
-- Name: _band_dsdown(numeric); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._band_dsdown(v numeric) RETURNS integer
    LANGUAGE sql IMMUTABLE
    AS $$
  select case when v is null then 3 when v>=1.20 then 5 when v>=1.10 then 4 when v>=1.00 then 3 when v>=0.90 then 2 else 1 end $$;


--
-- Name: _band_tenor(integer); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._band_tenor(m integer) RETURNS integer
    LANGUAGE sql IMMUTABLE
    AS $$
  select case when m is null then 3 when m<=60 then 5 when m<=84 then 4 when m<=120 then 3 when m<=180 then 2 else 1 end $$;


--
-- Name: _book_ead(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._book_ead() RETURNS numeric
    LANGUAGE sql STABLE
    SET search_path TO 'crm', 'public'
    AS $$
  select coalesce(sum(principal_mxn - coalesce((select sum(allocated_principal) from crm.repayment r where r.facility_id=f.id),0)),0)
  from crm.facility f where f.status in ('active','npl','restructured');
$$;


--
-- Name: _deal_channel_target(uuid, text); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._deal_channel_target(p_deal uuid, p_channel text) RETURNS text
    LANGUAGE sql STABLE
    SET search_path TO 'crm', 'public'
    AS $$
  select case when p_channel='email'
    then (select value_norm from crm.comms_identity where deal_id=p_deal and kind='email' order by created_at desc limit 1)
    else coalesce((select value_norm from crm.comms_identity where deal_id=p_deal and kind='phone' order by created_at desc limit 1),
                  (select regexp_replace(c.phone,'[^0-9]','','g') from crm.contact c join crm.comms_identity i on i.contact_id=c.id where i.deal_id=p_deal limit 1)) end;
$$;


--
-- Name: _deal_ead(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._deal_ead(p_deal uuid) RETURNS numeric
    LANGUAGE sql STABLE
    SET search_path TO 'crm', 'public'
    AS $$
  select coalesce(
    (select f.principal_mxn - coalesce((select sum(allocated_principal) from crm.repayment r where r.facility_id=f.id),0)
       from crm.facility f where f.deal_id=p_deal),
    (select nullif(snapshot->>'ead','')::numeric from crm.credit_memo where deal_id=p_deal order by version desc limit 1),
    0);
$$;


--
-- Name: _deal_tech(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._deal_tech(p_deal uuid) RETURNS text
    LANGUAGE sql STABLE
    SET search_path TO 'crm', 'public'
    AS $$
  select case when exists (select 1 from crm.deal_line_item where deal_id=p_deal and item_type='bess') then 'BESS' else 'PV' end;
$$;


--
-- Name: _emit_activity_event(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._emit_activity_event() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
begin
  if new.direction='inbound' and new.deal_id is not null then
    insert into crm.automation_event(event_type, entity_id, payload)
      values ('inbound_received', new.deal_id, jsonb_build_object('deal_id', new.deal_id, 'type', new.type));
  end if;
  return new;
end $$;


--
-- Name: _emit_deal_event(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._emit_deal_event() RETURNS trigger
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
begin
  if coalesce(current_setting('crm.suppress_events', true),'') = 'on' then return new; end if;
  if new.stage is distinct from old.stage then
    insert into crm.automation_event(event_type, entity_id, payload)
      values ('stage_enter', new.id, jsonb_build_object('stage', new.stage::text, 'deal_id', new.id));
  end if;
  if new.ecl_stage is distinct from old.ecl_stage and new.ecl_stage >= 2 then
    insert into crm.automation_event(event_type, entity_id, payload)
      values ('stage3_migration', new.id, jsonb_build_object('ecl_stage', new.ecl_stage, 'deal_id', new.id));
  end if;
  return new;
end $$;


--
-- Name: _estado_risk(text); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._estado_risk(p text) RETURNS integer
    LANGUAGE sql IMMUTABLE
    AS $$
  select case when p is null then 2
    when lower(p) = any(array['tamaulipas','sinaloa','michoacán','michoacan','guerrero','sonora','baja california','chihuahua','zacatecas','colima']) then 3
    else 1 end $$;


--
-- Name: _fire_action(jsonb, uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._fire_action(p_action jsonb, p_deal uuid) RETURNS text
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $_$
declare a text; cfg jsonb; v_owner text; v_to text; v_seq uuid; v_delay int;
begin
  a := p_action->>'action_type'; cfg := coalesce(p_action->'action_config','{}'::jsonb);
  if a='create_task' then
    select u.email into v_owner from crm.deal d left join crm.app_user u on u.id=d.owner_id where d.id=p_deal;
    insert into crm.task(deal_id, assignee, title, detail, due_at, is_next_step, created_by)
      values (p_deal, coalesce(nullif(cfg->>'assignee',''), v_owner, 'web'), coalesce(nullif(cfg->>'title',''),'Seguimiento'),
              cfg->>'detail', now() + make_interval(hours => coalesce(nullif(cfg->>'offset_hours','')::int, 24)),
              coalesce((cfg->>'is_next_step')::boolean,true), 'automation');
    return 'task';
  elsif a='queue_comms' then
    v_to := coalesce(nullif(cfg->>'to_address',''), crm._deal_channel_target(p_deal, coalesce(cfg->>'channel','whatsapp')));
    if v_to is null then return 'comms_skip_no_target'; end if;
    insert into crm.comms_outbox(deal_id, channel, to_address, subject, body, created_by)
      values (p_deal, coalesce(cfg->>'channel','whatsapp'), v_to, nullif(cfg->>'subject',''), crm._render(cfg->>'template', p_deal), 'automation');
    return 'comms';
  elsif a='set_stage' then
    update crm.deal set stage=(cfg->>'stage')::crm.deal_stage, stage_changed_at=now() where id=p_deal; return 'stage';
  elsif a='set_field' then
    execute format('update crm.deal set %I = $1 where id=$2', cfg->>'field') using cfg->>'value', p_deal; return 'field';
  elsif a='notify_user' then
    insert into crm.notification(recipient_email, kind, title, body, entity_type, entity_id, deal_id)
      select coalesce(nullif(cfg->>'to',''), u.email), 'automation', coalesce(cfg->>'title','Automatización'), crm._render(cfg->>'body', p_deal), 'deal', p_deal, p_deal
      from crm.deal d left join crm.app_user u on u.id=d.owner_id where d.id=p_deal;
    return 'notify';
  elsif a='enroll_sequence' then
    v_seq := (cfg->>'sequence_id')::uuid;
    select delay_hours into v_delay from crm.sequence_step where sequence_id=v_seq and step_no=1;
    insert into crm.sequence_enrollment(sequence_id, deal_id, next_action_at)
      values (v_seq, p_deal, now() + make_interval(hours => coalesce(v_delay,0)))
      on conflict (sequence_id, deal_id) do nothing;
    return 'enroll';
  end if;
  return 'noop';
end $_$;


--
-- Name: _grade_of(numeric); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._grade_of(c numeric) RETURNS text
    LANGUAGE sql IMMUTABLE
    AS $$
  select case when c>=4.5 then 'A1' when c>=4.0 then 'A2' when c>=3.5 then 'B1' when c>=3.0 then 'B2'
              when c>=2.5 then 'C1' when c>=2.0 then 'C2' else 'D' end $$;


--
-- Name: _lifetime_pd(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._lifetime_pd(p_deal uuid) RETURNS numeric
    LANGUAGE sql STABLE
    SET search_path TO 'crm', 'public'
    AS $$
  select max(t.cumulative_pd) from crm.pd_term_structure t
  where t.rating_id = (select id from crm.pd_rating where deal_id=p_deal order by computed_at desc limit 1);
$$;


--
-- Name: _mask_name(text); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._mask_name(t text) RETURNS text
    LANGUAGE sql IMMUTABLE
    AS $$ select case when t is null or t='' then t else left(t,1)||'•••' end $$;


--
-- Name: _mask_rfc(text); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._mask_rfc(t text) RETURNS text
    LANGUAGE sql IMMUTABLE
    AS $$ select case when t is null or t='' then t else left(t,3)||'••••••' end $$;


--
-- Name: _match_conditions(uuid, jsonb); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._match_conditions(p_deal uuid, p_conds jsonb) RETURNS boolean
    LANGUAGE plpgsql STABLE
    SET search_path TO 'crm', 'public'
    AS $$
declare v_row jsonb; c jsonb; f text; op text; val text; actual text;
begin
  if p_conds is null or jsonb_array_length(p_conds)=0 then return true; end if;
  select to_jsonb(d) into v_row from crm.deal d where d.id=p_deal;
  for c in select * from jsonb_array_elements(p_conds) loop
    f := c->>'field'; op := coalesce(c->>'op','eq'); val := c->>'value'; actual := v_row->>f;
    if op='eq' and coalesce(actual,'') <> coalesce(val,'') then return false;
    elsif op='neq' and coalesce(actual,'') = coalesce(val,'') then return false;
    elsif op='contains' and position(lower(coalesce(val,'')) in lower(coalesce(actual,''))) = 0 then return false;
    elsif op='gt' and not (coalesce(actual,'0')::numeric > coalesce(val,'0')::numeric) then return false;
    elsif op='lt' and not (coalesce(actual,'0')::numeric < coalesce(val,'0')::numeric) then return false;
    end if;
  end loop;
  return true;
end $$;


--
-- Name: _norm(text); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._norm(t text) RETURNS text
    LANGUAGE sql
    SET search_path TO 'crm', 'public', 'extensions'
    AS $$
  select btrim(regexp_replace(upper(unaccent(coalesce(t,''))), '[^A-Z0-9]+', ' ', 'g'));
$$;


--
-- Name: _notify_approvers(text, text, text, text, uuid, uuid, text, text, timestamp with time zone, integer, text); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._notify_approvers(p_kind text, p_title text, p_body text, p_entity_type text, p_entity_id uuid, p_deal uuid, p_action_type text, p_route text, p_due timestamp with time zone, p_priority integer, p_dedupe text) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'crm', 'public'
    AS $$
declare u record;
begin
  for u in select email from crm.app_user where active and role in ('admin','compliance') and coalesce(email,'') <> '' loop
    perform crm._notify_user(u.email, p_kind, p_title, p_body, p_entity_type, p_entity_id, p_deal,
      p_action_type, p_route, p_due, p_priority, p_dedupe || ':' || u.email);
  end loop;
end $$;


--
-- Name: _notify_compliance(text, text, text, uuid, uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._notify_compliance(p_kind text, p_title text, p_body text, p_cp uuid, p_deal uuid DEFAULT NULL::uuid) RETURNS void
    LANGUAGE sql
    SET search_path TO 'crm', 'public'
    AS $$
  insert into crm.notification(recipient_email, kind, title, body, entity_type, entity_id, deal_id)
  select email, p_kind, p_title, p_body, 'counterparty', p_cp, p_deal
  from crm.app_user where role in ('admin','compliance') and active and email is not null;
$$;


--
-- Name: _notify_user(text, text, text, text, text, uuid, uuid, text, text, timestamp with time zone, integer, text); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._notify_user(p_email text, p_kind text, p_title text, p_body text, p_entity_type text, p_entity_id uuid, p_deal uuid, p_action_type text, p_route text, p_due timestamp with time zone, p_priority integer, p_dedupe text) RETURNS void
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'crm', 'public'
    AS $$
begin
  if coalesce(p_email,'') = '' then return; end if;
  insert into crm.notification(recipient_email, kind, title, body, entity_type, entity_id, deal_id,
      action_type, action_state, route, due_at, priority, dedupe_key)
  values (p_email, p_kind, p_title, p_body, p_entity_type, p_entity_id, p_deal,
      p_action_type, case when p_action_type is null then 'none' else 'pending' end, p_route, p_due, p_priority, p_dedupe)
  on conflict (dedupe_key) where dedupe_key is not null
  do update set title = excluded.title, body = excluded.body, due_at = excluded.due_at,
      priority = excluded.priority, route = excluded.route
  where crm.notification.action_state = 'pending';
end $$;


--
-- Name: _npv(numeric, numeric[]); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._npv(p_rate numeric, p_cf numeric[]) RETURNS numeric
    LANGUAGE sql IMMUTABLE
    AS $$
  select coalesce(sum(cf / power(1+p_rate, i)), 0) from unnest(p_cf) with ordinality as t(cf, i);
$$;


--
-- Name: _pd_of_grade(text); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._pd_of_grade(g text) RETURNS numeric
    LANGUAGE sql IMMUTABLE
    AS $$
  select case g when 'A1' then 0.003 when 'A2' then 0.006 when 'B1' then 0.012 when 'B2' then 0.025
                when 'C1' then 0.05 when 'C2' then 0.10 else 0.25 end $$;


--
-- Name: _performance(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._performance(p_pid uuid) RETURNS jsonb
    LANGUAGE plpgsql STABLE
    SET search_path TO 'crm', 'public'
    AS $$
declare v_exp numeric; v_act numeric; v_months int; v_pr numeric; v_short numeric;
begin
  select coalesce(sum(a.kwh_actual),0), count(*) into v_act, v_months from crm.generation_actual a where a.project_id=p_pid;
  -- expected over the same observed months: sum of (baseline year kwh / 12) for each actual period's year
  select coalesce(sum(b.expected_kwh/12.0),0) into v_exp
    from crm.generation_actual a join crm.generation_baseline b on b.project_id=a.project_id and b.year_no=a.year_no where a.project_id=p_pid;
  v_pr := case when v_exp > 0 then round(v_act/v_exp, 3) end;
  v_short := greatest(0, v_exp - v_act);
  return jsonb_build_object('expected_kwh',round(v_exp),'actual_kwh',round(v_act),'months',v_months,'pr',v_pr,'shortfall_kwh',round(v_short));
end $$;


--
-- Name: _pit_pd(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._pit_pd(p_deal uuid) RETURNS numeric
    LANGUAGE sql STABLE
    SET search_path TO 'crm', 'public'
    AS $$
  select pit_pd from crm.pd_rating where deal_id=p_deal order by computed_at desc limit 1;
$$;


--
-- Name: _provision_app_user(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._provision_app_user() RETURNS trigger
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'crm', 'public'
    AS $$
begin
  update crm.app_user set auth_uid = new.id
    where auth_uid is null and lower(email) = lower(new.email);
  -- No auto-create: access is admin-provisioned. A stranger's auth row simply has
  -- no app_user, so RLS shows them nothing and the login gate signs them out.
  return new;
end $$;


--
-- Name: _recompute_counterparty_risk(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._recompute_counterparty_risk(p_id uuid) RETURNS void
    LANGUAGE plpgsql
    AS $$
declare v_fail int; v_review int; v_pass int; v_cur crm.dd_status; v_clr text;
begin
  select count(*) filter (where status='fail'), count(*) filter (where status='manual_review'),
         count(*) filter (where status='pass' and check_type in ('rfc_format','efos_69b','sanctions_pep','lpb'))
    into v_fail, v_review, v_pass from crm.dd_check where counterparty_id=p_id;
  select dd_status, clearance_status into v_cur, v_clr from crm.counterparty where id=p_id;
  update crm.counterparty set
    dd_status=(case when v_fail>0 then 'blocked' when v_cur='cleared' and v_clr='approved' then 'cleared' else 'in_progress' end)::crm.dd_status,
    risk_tier=case when v_fail>0 then 'D' when v_cur='cleared' and v_clr='approved' then 'A' when v_review>0 then 'C' when v_pass>=4 then 'B' else 'C' end,
    risk_score=case when v_fail>0 then 20 when v_cur='cleared' and v_clr='approved' then 95 when v_review>0 then 50 when v_pass>=4 then 72 else 45 end,
    updated_at=now() where id=p_id;
end $$;


--
-- Name: _reeval_sanctions(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._reeval_sanctions(p_cp uuid) RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare v_true int; v_strong int; v_pend int; v_pep int; v_status text; v_detail text;
begin
  select count(*) filter (where disposition='true_match'),
         count(*) filter (where disposition='pending' and match_score>=0.85),
         count(*) filter (where disposition='pending')
    into v_true, v_strong, v_pend
  from crm.dd_screening_hit where counterparty_id=p_cp;
  select count(*) into v_pep from crm.dd_ubo where counterparty_id=p_cp and is_pep;

  if v_true>0 then v_status:='fail'; v_detail:=v_true||' coincidencia(s) confirmada(s)';
  elsif v_strong>0 then v_status:='fail'; v_detail:=v_strong||' coincidencia(s) fuerte(s) sin dictaminar';
  elsif v_pend>0 or v_pep>0 then v_status:='manual_review';
    v_detail:=coalesce(nullif(v_pend,0)||' posible(s); ','')||(case when v_pep>0 then v_pep||' PEP' else 'revisar' end);
  else v_status:='pass'; v_detail:='Sin coincidencias vigentes'; end if;

  insert into crm.dd_check(counterparty_id, check_type, status, detail, source, performed_by)
  values (p_cp,'sanctions_pep',v_status,v_detail,'opensanctions','system')
  on conflict (counterparty_id, check_type) do update set status=excluded.status, detail=excluded.detail, performed_at=now();
  perform crm._recompute_counterparty_risk(p_cp);
end $$;


--
-- Name: _refresh_auto_cps(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._refresh_auto_cps(p_deal uuid) RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
begin
  update crm.cp_item cp set status='satisfied', satisfied_by='auto', satisfied_at=now(), verified_by='auto'
  where cp.deal_id=p_deal and cp.status='pending' and (
    (cp.auto_source='dd_status' and exists (select 1 from crm.counterparty c join crm.deal d on d.counterparty_id=c.id where d.id=p_deal and c.dd_status='cleared'))
    or (cp.auto_source='collateral' and exists (select 1 from crm.collateral where deal_id=p_deal and status='active' and perfection_status='perfected'))
    or (cp.auto_source='milestone' and exists (select 1 from crm.project pr join crm.project_milestone m on m.project_id=pr.id where pr.deal_id=p_deal and m.name like 'Estudio / convenio%' and m.status='certified')));
end $$;


--
-- Name: _render(text, uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._render(p_tpl text, p_deal uuid) RETURNS text
    LANGUAGE sql STABLE
    SET search_path TO 'crm', 'public'
    AS $$
  select replace(replace(coalesce(p_tpl,''), '{{deal.name}}', coalesce((select name from crm.deal where id=p_deal),'')),
                 '{{deal.stage}}', coalesce((select stage::text from crm.deal where id=p_deal),''));
$$;


--
-- Name: _rescreen_all(integer); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._rescreen_all(p_ttl_days integer DEFAULT 365) RETURNS jsonb
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare r record; v_reopened int:=0; v_expired int:=0; v_res text; v_n int:=0;
begin
  for r in select id from crm.counterparty where clearance_status in ('approved','requested') or dd_status in ('cleared','in_progress') loop
    v_res := crm._rescreen_counterparty(r.id, p_ttl_days); v_n := v_n+1;
    if v_res='reopened' then v_reopened:=v_reopened+1; elsif v_res='expired' then v_expired:=v_expired+1; end if;
  end loop;
  return jsonb_build_object('screened',v_n,'reopened',v_reopened,'expired',v_expired,'at',now());
end $$;


--
-- Name: _rescreen_counterparty(uuid, integer); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._rescreen_counterparty(p_cp uuid, p_ttl_days integer DEFAULT 365) RETURNS text
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public', 'extensions'
    AS $$
declare v_clr text; v_cleared_at timestamptz; v_name text; v_new text; u record; v_deal uuid;
begin
  select clearance_status, cleared_at, name into v_clr, v_cleared_at, v_name from crm.counterparty where id=p_cp;
  select id into v_deal from crm.deal where counterparty_id=p_cp limit 1;
  if v_clr='approved' and v_cleared_at is not null and v_cleared_at < now() - make_interval(days => p_ttl_days) then
    update crm.counterparty set clearance_status='expired', updated_at=now() where id=p_cp;
    insert into crm.dd_decision(counterparty_id,kind,decision,reason,actor) values (p_cp,'clearance_expired','expired','vigencia de dictamen vencida','system');
    perform crm._notify_compliance('clearance_expired','Dictamen DD vencido', coalesce(v_name,'Contraparte')||' — re-validar', p_cp, v_deal);
    perform crm._recompute_counterparty_risk(p_cp);
    return 'expired';
  end if;
  delete from crm.dd_screening_hit where counterparty_id=p_cp and disposition='pending';
  perform crm._screen_name(p_cp,'entity',v_name);
  for u in select name from crm.dd_ubo where counterparty_id=p_cp loop perform crm._screen_name(p_cp,'ubo',u.name); end loop;
  perform crm._reeval_sanctions(p_cp);
  select status into v_new from crm.dd_check where counterparty_id=p_cp and check_type='sanctions_pep';
  if v_clr='approved' and v_new is distinct from 'pass' then
    update crm.counterparty set clearance_status='reopened', updated_at=now() where id=p_cp;
    insert into crm.dd_decision(counterparty_id,kind,decision,reason,actor) values (p_cp,'auto_reopen',v_new,'nueva coincidencia en lista de sanciones','system');
    perform crm._notify_compliance('dd_reopen','Contraparte reabierta por re-screening', coalesce(v_name,'Contraparte')||' — nueva coincidencia en listas', p_cp, v_deal);
    perform crm._recompute_counterparty_risk(p_cp);
    return 'reopened';
  end if;
  return 'unchanged';
end $$;


--
-- Name: _rollup_po_costs(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._rollup_po_costs(p_project uuid) RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
begin
  -- committed = sum of live (issued/received/invoiced) POs on each cost line
  update crm.project_cost c set committed = coalesce((
    select sum(po.mxn_committed) from crm.purchase_order po
    where po.cost_id=c.id and po.status in ('issued','partially_received','received','invoiced','closed')),0)
  where c.project_id=p_project and exists (select 1 from crm.purchase_order po where po.cost_id=c.id);
  -- actual = sum of 3-way-matched invoices (converted at the PO rate) on each cost line
  update crm.project_cost c set actual = coalesce((
    select sum(i.invoice_amount_fx * po.fx_rate_po) from crm.po_invoice i join crm.purchase_order po on po.id=i.po_id
    where po.cost_id=c.id and i.three_way_matched),0)
  where c.project_id=p_project and exists (
    select 1 from crm.po_invoice i join crm.purchase_order po on po.id=i.po_id where po.cost_id=c.id and i.three_way_matched);
end $$;


--
-- Name: _rollup_subcontract_costs(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._rollup_subcontract_costs(p_project uuid) RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
begin
  update crm.project_cost c set
    committed = coalesce((select sum(po.mxn_committed) from crm.purchase_order po where po.cost_id=c.id and po.status in ('issued','partially_received','received','invoiced','closed')),0)
              + coalesce((select sum(s.contract_value_mxn) from crm.subcontract s where s.cost_id=c.id and s.status in ('issued','active','closed')),0),
    actual = coalesce((select sum(i.invoice_amount_fx * po.fx_rate_po) from crm.po_invoice i join crm.purchase_order po on po.id=i.po_id where po.cost_id=c.id and i.three_way_matched),0)
           + coalesce((select sum(pc.net_certified) from crm.sub_payment_claim pc join crm.subcontract s on s.id=pc.subcontract_id where s.cost_id=c.id and pc.status='certified'),0)
  where c.project_id=p_project
    and (exists (select 1 from crm.purchase_order po where po.cost_id=c.id) or exists (select 1 from crm.subcontract s where s.cost_id=c.id));
end $$;


--
-- Name: _scenario_lgd_mult(numeric); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._scenario_lgd_mult(fx numeric) RETURNS numeric
    LANGUAGE sql IMMUTABLE
    AS $$ select greatest(0.6, 1 + 0.8*greatest(0, fx/18.0 - 1)) $$;


--
-- Name: _scenario_pd_mult(numeric, numeric, numeric, numeric); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._scenario_pd_mult(fx numeric, tariff numeric, rate_bps numeric, gen numeric) RETURNS numeric
    LANGUAGE sql IMMUTABLE
    AS $$
  select greatest(0.25, 1
    + 2.0*greatest(0, fx/18.0 - 1)               -- peso weaker than 18 base
    + 1.5*greatest(0, -tariff)                    -- tariff cut hurts savings/capacity to pay
    + 0.5*greatest(0, rate_bps/10000.0)           -- higher domestic rates
    + 1.0*greatest(0, 1 - gen)                    -- generation shortfall (P90)
    - 0.8*greatest(0, 1 - fx/18.0)                -- peso stronger → relief
    - 0.8*greatest(0, tariff)) $$;


--
-- Name: _screen_lpb(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._screen_lpb(p_cp uuid) RETURNS integer
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public', 'extensions'
    AS $$
declare v_name text; v_rfc text; v_hits int := 0; r record; u record;
begin
  select name, upper(btrim(rfc)) into v_name, v_rfc from crm.counterparty where id=p_cp;
  -- exact RFC match
  if v_rfc is not null and v_rfc <> '' then
    for r in select nombre from crm.dd_lpb where upper(rfc)=v_rfc loop
      insert into crm.dd_screening_hit(counterparty_id,subject,subject_name,list_source,matched_name,match_score,dataset)
      values (p_cp,'entity',v_name,'uif_lpb',r.nombre,1.0,'LPB'); v_hits:=v_hits+1;
    end loop;
  end if;
  -- fuzzy name match (entity + UBOs)
  for r in select crm._norm(v_name) nn union select crm._norm(name) from crm.dd_ubo where counterparty_id=p_cp loop
    continue when r.nn is null or length(r.nn) < 4;
    for u in select nombre, similarity(norm_name, r.nn) sc from crm.dd_lpb where norm_name % r.nn order by sc desc limit 3 loop
      if u.sc >= 0.6 then
        insert into crm.dd_screening_hit(counterparty_id,subject,subject_name,list_source,matched_name,match_score,dataset)
        values (p_cp,'entity',v_name,'uif_lpb',u.nombre,round(u.sc::numeric,3),'LPB'); v_hits:=v_hits+1;
      end if;
    end loop;
  end loop;
  return v_hits;
end $$;


--
-- Name: _screen_name(uuid, text, text); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._screen_name(p_cp uuid, p_subject text, p_name text) RETURNS integer
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public', 'extensions'
    AS $$
declare v_norm text; v_hits int := 0; r record;
begin
  v_norm := crm._norm(p_name);
  if length(v_norm) < 4 then return 0; end if;
  for r in
    select target_name, alt_name, dataset, source,
           similarity(norm_name, v_norm) as score
    from crm.sanctions_entry
    where norm_name % v_norm
    order by score desc
    limit 5
  loop
    if r.score >= 0.55 then
      insert into crm.dd_screening_hit(counterparty_id, subject, subject_name, list_source, matched_name, match_score, dataset)
      values (p_cp, p_subject, p_name, r.source, r.target_name, round(r.score::numeric,3), r.dataset);
      v_hits := v_hits + 1;
    end if;
  end loop;
  return v_hits;
end $$;


--
-- Name: _sector_risk(text); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._sector_risk(p text) RETURNS integer
    LANGUAGE sql IMMUTABLE
    AS $$
  select case when p is null then 2
    when lower(p) = any(array['construcción','construccion','inmobiliario','casa de cambio','minería','mineria','juegos','apuestas','joyería','joyeria']) then 3
    else 1 end $$;


--
-- Name: _seed_itp(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._seed_itp(p_pid uuid) RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare v_cv numeric; v_cod date;
begin
  if exists (select 1 from crm.itp_item where project_id=p_pid) then return; end if;
  insert into crm.itp_item(project_id, milestone_id, description, weight_pct, hold_point)
    select p_pid, m.id, m.name, m.pct_value, m.seq in (5,6)  -- energización + prueba de capacidad are hold points
    from crm.project_milestone m where m.project_id=p_pid;
  select contract_value_mxn into v_cv from crm.project where id=p_pid;
  v_cod := (select max(planned_date) from crm.project_milestone where project_id=p_pid);
  insert into crm.ld_accrual(project_id, cod_target, ld_rate_per_day, ld_cap_pct)
    values (p_pid, v_cod, round(coalesce(v_cv,0)*0.001), 0.10)   -- 0.1%/day, cap 10% of contract
    on conflict (project_id) do nothing;
end $$;


--
-- Name: _seed_post_cod(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._seed_post_cod(p_pid uuid) RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare v_deal uuid; v_gen numeric; v_cod date; y int;
begin
  select deal_id into v_deal from crm.project where id=p_pid;
  select coalesce(nullif(assumptions->>'generation_kwh','')::numeric, nullif(results#>>'{annual,0,generation}','')::numeric, 0)
    into v_gen from crm.deal_financials where deal_id=v_deal;
  if not exists (select 1 from crm.generation_baseline where project_id=p_pid) and coalesce(v_gen,0) > 0 then
    for y in 1..10 loop
      insert into crm.generation_baseline(project_id, year_no, expected_kwh)
        values (p_pid, y, round(v_gen * power(1-0.005, y-1))) on conflict do nothing;
    end loop;
  end if;
  select cod_actual into v_cod from crm.ld_accrual where project_id=p_pid;
  if not exists (select 1 from crm.dlp_clock where project_id=p_pid) then
    insert into crm.dlp_clock(project_id, cod_date, expires_at)
      values (p_pid, v_cod, (coalesce(v_cod, current_date) + interval '24 months')::date) on conflict do nothing;
  end if;
end $$;


--
-- Name: _seed_project_costs(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._seed_project_costs(p_pid uuid) RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare v_cv numeric; v_bac numeric;
begin
  if exists (select 1 from crm.project_cost where project_id=p_pid) then return; end if;
  select contract_value_mxn into v_cv from crm.project where id=p_pid;
  v_bac := coalesce(v_cv,0) * 0.82;
  insert into crm.project_cost(project_id, cost_code, bac) values
    (p_pid,'Módulos FV', v_bac*0.35),(p_pid,'Inversores', v_bac*0.12),
    (p_pid,'Estructura / montaje', v_bac*0.12),(p_pid,'BOS eléctrico', v_bac*0.10),
    (p_pid,'Obra civil', v_bac*0.08),(p_pid,'Mano de obra / instalación', v_bac*0.13),
    (p_pid,'Interconexión CFE', v_bac*0.05),(p_pid,'Ingeniería / gestión', v_bac*0.05);
end $$;


--
-- Name: _seed_schedule(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._seed_schedule(p_pid uuid) RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare m record; v_prev uuid; v_equipo uuid; po record; v_dur numeric; v_aid uuid;
begin
  if exists (select 1 from crm.schedule_activity where project_id=p_pid) then return; end if;
  v_prev := null;
  for m in select * from crm.project_milestone where project_id=p_pid order by seq loop
    v_dur := greatest(15, coalesce(m.pct_value,10) * 3);   -- rough calendar days ~ weight
    insert into crm.schedule_activity(project_id, code, name, activity_type, baseline_duration_days, is_terminal, seq,
        pct_complete, linked_itp_item_id)
      values (p_pid, 'M'||m.seq, m.name, 'milestone', v_dur, (m.seq=7), m.seq,
        coalesce((select verified_pct from crm.itp_item i where i.project_id=p_pid and i.milestone_id=m.id limit 1),0),
        (select id from crm.itp_item i where i.project_id=p_pid and i.milestone_id=m.id limit 1))
      returning id into v_aid;
    if v_prev is not null then insert into crm.schedule_dependency(project_id, predecessor_id, successor_id) values (p_pid, v_prev, v_aid); end if;
    if m.seq=3 then v_equipo := v_aid; end if;   -- 'Equipo adquirido'
    v_prev := v_aid;
  end loop;
  -- procurement activities from POs → predecessors of 'Equipo adquirido'
  for po in select * from crm.purchase_order where project_id=p_pid and status not in ('cancelled') loop
    insert into crm.schedule_activity(project_id, code, name, activity_type, baseline_duration_days, linked_po_id, seq,
        pct_complete)
      values (p_pid, 'PO', 'Suministro: '||po.category||' ('||po.supplier_name||')', 'procurement',
        greatest(15, coalesce(po.expected_delivery_date - current_date, 60)),
        po.id, 0, case when po.status in ('received','invoiced') then 100 else 0 end)
      returning id into v_aid;
    if v_equipo is not null then insert into crm.schedule_dependency(project_id, predecessor_id, successor_id) values (p_pid, v_aid, v_equipo); end if;
  end loop;
end $$;


--
-- Name: _spawn_facility(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._spawn_facility(p_deal uuid) RETURNS uuid
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare v_fid uuid; v_cp uuid; v_res jsonb; v_asm jsonb; v_prin numeric; v_rate numeric; v_ten int; v_grace int; v_dscr numeric; v_ccy text; v_date date;
begin
  select id into v_fid from crm.facility where deal_id=p_deal;
  if v_fid is not null then return v_fid; end if;
  select counterparty_id, currency, coalesce(close_date, won_date, current_date) into v_cp, v_ccy, v_date from crm.deal where id=p_deal;
  select results, assumptions into v_res, v_asm from crm.deal_financials where deal_id=p_deal;
  v_prin := coalesce(nullif(v_res->>'max_debt_mxn','')::numeric, nullif(v_res#>>'{el,ead}','')::numeric, 0);
  v_rate := coalesce(nullif(v_res->>'priced_rate','')::numeric, nullif(v_asm->>'debt_rate','')::numeric, 0.14);
  v_ten  := round(coalesce(nullif(v_asm->>'tenor_years','')::numeric, 5) * 12)::int;
  v_grace := round(coalesce(nullif(v_asm->>'construction_months','')::numeric, 0))::int;
  v_dscr := coalesce(nullif(v_asm->>'target_dscr','')::numeric, 1.30);
  insert into crm.facility(deal_id, counterparty_id, currency, principal_mxn, annual_rate, tenor_months, grace_months, dscr_target, disburse_date, created_by)
  values (p_deal, v_cp, coalesce(v_ccy,'MXN'), v_prin, v_rate, greatest(v_ten,1), v_grace, v_dscr, v_date, 'system')
  returning id into v_fid;
  perform crm.build_schedule(v_fid);
  return v_fid;
end $$;


--
-- Name: _spawn_project(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm._spawn_project(p_deal uuid) RETURNS uuid
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare v_pid uuid; v_name text; v_cp uuid; v_kwp numeric; v_val numeric;
begin
  select id into v_pid from crm.project where deal_id = p_deal;
  if v_pid is not null then return v_pid; end if;
  select d.name, d.counterparty_id, s.total_kwp, coalesce((f.results->>'capex_mxn')::numeric, s.total_epc_value*18)
    into v_name, v_cp, v_kwp, v_val
  from crm.deal d left join crm.deal_summary s on s.id=d.id left join crm.deal_financials f on f.deal_id=d.id where d.id=p_deal;
  insert into crm.project(deal_id, counterparty_id, name, contract_value_mxn, kwp)
  values (p_deal, v_cp, v_name, v_val, v_kwp) returning id into v_pid;
  insert into crm.project_milestone(project_id, seq, name, pct_value) values
    (v_pid,1,'Solicitud de interconexión (CFE)',0),(v_pid,2,'Estudio / convenio de interconexión',10),
    (v_pid,3,'Equipo adquirido (procurement)',30),(v_pid,4,'Terminación mecánica',30),
    (v_pid,5,'Energización',15),(v_pid,6,'Prueba de capacidad / desempeño',10),(v_pid,7,'PAC — aceptación provisional',5);
  perform crm._seed_project_costs(v_pid);
  perform crm._seed_itp(v_pid);
  return v_pid;
end $$;


--
-- Name: accrue_ld(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.accrue_ld() RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare l record; v_cv numeric; v_days int; v_acc numeric; v_cap numeric;
begin
  for l in select * from crm.ld_accrual where cod_actual is null and cod_target is not null and cod_target < current_date loop
    select contract_value_mxn into v_cv from crm.project where id=l.project_id;
    v_days := current_date - l.cod_target;
    v_cap := coalesce(v_cv,0) * l.ld_cap_pct;
    v_acc := least(v_days * l.ld_rate_per_day, v_cap);
    update crm.ld_accrual set days_late=v_days, accrued_amount=round(v_acc), capped=(v_acc >= v_cap and v_cap>0), updated_at=now() where project_id=l.project_id;
  end loop;
end $$;


--
-- Name: advance_sequences(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.advance_sequences() RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare en record; st record; nxt record; v_to text;
begin
  perform set_config('crm.suppress_events','on', true);
  for en in select * from crm.sequence_enrollment where status='active' and next_action_at is not null and next_action_at <= now() loop
    select * into st from crm.sequence_step where sequence_id=en.sequence_id and step_no=en.current_step+1;
    if not found then update crm.sequence_enrollment set status='completed' where id=en.id; continue; end if;
    if st.channel='task' then
      insert into crm.task(deal_id, assignee, title, due_at, is_next_step, created_by)
        select en.deal_id, coalesce(u.email,'web'), crm._render(st.template, en.deal_id), now(), true, 'sequence'
        from crm.deal d left join crm.app_user u on u.id=d.owner_id where d.id=en.deal_id;
    else
      v_to := crm._deal_channel_target(en.deal_id, st.channel);
      if v_to is not null then
        insert into crm.comms_outbox(deal_id, channel, to_address, body, created_by)
          values (en.deal_id, st.channel, v_to, crm._render(st.template, en.deal_id), 'sequence');
      end if;
    end if;
    select * into nxt from crm.sequence_step where sequence_id=en.sequence_id and step_no=en.current_step+2;
    update crm.sequence_enrollment set current_step=current_step+1,
      next_action_at = case when found then now() + make_interval(hours => nxt.delay_hours) else null end,
      status = case when found then 'active' else 'completed' end
      where id=en.id;
  end loop;
end $$;


--
-- Name: app_user_by_phone(text); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.app_user_by_phone(p_phone text) RETURNS uuid
    LANGUAGE sql STABLE SECURITY DEFINER
    SET search_path TO 'crm', 'public'
    AS $$
  select id from crm.app_user
   where active
     and phone is not null
     and length(regexp_replace(phone, '[^0-9]', '', 'g')) >= 10
     and right(regexp_replace(phone,   '[^0-9]', '', 'g'), 10)
       = right(regexp_replace(p_phone, '[^0-9]', '', 'g'), 10)
   order by (role = 'admin') desc, created_at
   limit 1
$$;


--
-- Name: build_schedule(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.build_schedule(p_fac uuid) RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare v_p numeric; v_rate numeric; v_n int; v_grace int; v_start date;
        v_mrate numeric; v_pay numeric; v_bal numeric; v_int numeric; v_prin numeric; i int; v_amort int;
begin
  select principal_mxn, annual_rate, tenor_months, grace_months, coalesce(disburse_date,current_date)
    into v_p, v_rate, v_n, v_grace, v_start from crm.facility where id=p_fac;
  delete from crm.facility_schedule where facility_id=p_fac;
  if coalesce(v_p,0)<=0 or coalesce(v_n,0)<=0 then return; end if;
  v_mrate := coalesce(v_rate,0)/12.0;
  v_grace := least(coalesce(v_grace,0), v_n-1);
  v_amort := v_n - v_grace;
  if v_mrate > 0 then v_pay := v_p * v_mrate / (1 - power(1+v_mrate, -v_amort));
  else v_pay := v_p / v_amort; end if;
  v_bal := v_p;
  for i in 1..v_n loop
    v_int := v_bal * v_mrate;
    v_prin := case when i <= v_grace then 0 else least(v_bal, v_pay - v_int) end;
    insert into crm.facility_schedule(facility_id, period_no, due_date, opening_balance, principal_due, interest_due, total_due, closing_balance)
    values (p_fac, i, (v_start + (i || ' months')::interval)::date, round(v_bal,2), round(v_prin,2), round(v_int,2), round(v_prin+v_int,2), round(v_bal - v_prin,2));
    v_bal := v_bal - v_prin;
  end loop;
end $$;


--
-- Name: compute_dpd(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.compute_dpd(p_fac uuid) RETURNS integer
    LANGUAGE plpgsql STABLE
    SET search_path TO 'crm', 'public'
    AS $$
declare v_paid numeric; v_due date;
begin
  select coalesce(sum(amount_mxn),0) into v_paid from crm.repayment where facility_id=p_fac and received_at<=current_date;
  select s.due_date into v_due from (
     select due_date, sum(total_due) over (order by period_no) cum
     from crm.facility_schedule where facility_id=p_fac
  ) s where s.due_date <= current_date and s.cum > v_paid
  order by s.due_date limit 1;
  if v_due is null then return 0; end if;
  return greatest(0, current_date - v_due);
end $$;


--
-- Name: compute_lgd(uuid, numeric); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.compute_lgd(p_deal uuid, p_ead numeric) RETURNS jsonb
    LANGUAGE plpgsql STABLE
    SET search_path TO 'crm', 'public'
    AS $$
declare v_secured numeric; v_residual numeric; v_lgd numeric; v_refer boolean; v_ead numeric;
begin
  v_ead := nullif(p_ead,0);
  select coalesce(sum(gross_value_mxn*(1-haircut_pct)),0) into v_secured
    from crm.collateral where deal_id=p_deal and status='active' and perfection_status='perfected';
  v_refer := exists (select 1 from crm.collateral
    where deal_id=p_deal and status in ('active','pending_approval') and gross_value_mxn>0 and perfection_status <> 'perfected');
  if v_ead is null then return jsonb_build_object('lgd',0.45,'refer',v_refer,'secured',round(v_secured),'residual',null,'ead',0); end if;
  v_residual := greatest(0, v_ead - v_secured);
  v_lgd := greatest(0.05, least(0.90, v_residual / v_ead));
  if v_refer then v_lgd := greatest(v_lgd, 0.75); end if;   -- unperfected material security → unsecured floor
  return jsonb_build_object('lgd',round(v_lgd,4),'refer',v_refer,'secured',round(v_secured),'residual',round(v_residual),'ead',round(v_ead));
end $$;


--
-- Name: compute_physical_pct(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.compute_physical_pct(p_pid uuid) RETURNS numeric
    LANGUAGE sql STABLE
    SET search_path TO 'crm', 'public'
    AS $$
  select case when coalesce(sum(weight_pct),0) > 0
              then round(sum(verified_pct*weight_pct)/sum(weight_pct), 2) end
  from crm.itp_item where project_id=p_pid;
$$;


--
-- Name: cure_scan(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.cure_scan() RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare f record; v_missed int; begin
  for f in select fe.facility_id, fa.deal_id, fe.probation_until, d.ecl_stage
           from crm.forbearance_event fe join crm.facility fa on fa.id=fe.facility_id join crm.deal d on d.id=fa.deal_id
           where fe.probation_until <= current_date and d.ecl_stage >= 2 loop
    select crm.compute_dpd(f.facility_id) into v_missed;
    if coalesce(v_missed,0) = 0 then   -- performed through probation with no arrears → cure one stage
      update crm.deal set ecl_stage = greatest(1, coalesce(ecl_stage,2)-1), updated_at=now() where id=f.deal_id;
      update crm.workout_case set status='cured' where facility_id=f.facility_id and status='forbearance';
    end if;
  end loop;
end $$;


--
-- Name: deal_from_intake(text, text, bigint); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.deal_from_intake(p_rpu text, p_name text, p_collection_request_id bigint DEFAULT NULL::bigint) RETURNS uuid
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'crm', 'public'
    AS $$
declare v_account uuid; v_deal uuid; v_name text := nullif(btrim(coalesce(p_name,'')),'');
begin
  if p_rpu is null then return null; end if;
  -- Already linked to a deal? done.
  select deal_id into v_deal from crm.deal_rpu where rpu = p_rpu limit 1;
  if v_deal is not null then return v_deal; end if;

  if v_name is not null then
    select id into v_account from crm.account where lower(name) = lower(v_name) limit 1;
    if v_account is null then
      insert into crm.account(name) values (v_name) returning id into v_account;
    end if;
    -- Reuse an open deal for this account (add the RPU to it).
    select id into v_deal from crm.deal
      where account_id = v_account and stage not in ('closed','perdido')
      order by created_at limit 1;
  end if;

  if v_deal is null then
    insert into crm.deal(name, stage, account_id, rpu, source)
      values (coalesce(v_name, p_rpu), 'lead', v_account, p_rpu, 'cfe_intake')
      returning id into v_deal;
  end if;

  insert into crm.deal_rpu(deal_id, rpu, razon_social, collection_request_id)
    values (v_deal, p_rpu, v_name, p_collection_request_id);
  return v_deal;
end $$;


--
-- Name: edd_gate(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.edd_gate(p_cp uuid) RETURNS jsonb
    LANGUAGE plpgsql STABLE
    SET search_path TO 'crm', 'public'
    AS $$
declare v_dd text; v_open int; reasons text[] := array[]::text[];
begin
  select dd_level into v_dd from crm.counterparty where id=p_cp;
  if coalesce(v_dd,'') <> 'reforzada' then return jsonb_build_object('ok',true,'reasons',reasons); end if;
  select count(*) into v_open from crm.edd_item where counterparty_id=p_cp and status='pending';
  if v_open > 0 then reasons := array_append(reasons, 'Debida diligencia reforzada: '||v_open||' pendiente(s)'); end if;
  if exists (select 1 from crm.edd_item where counterparty_id=p_cp and status='satisfied' and verified_by is null) then
    reasons := array_append(reasons, 'EDD sin verificación (cuatro ojos)'); end if;
  return jsonb_build_object('ok', array_length(reasons,1) is null, 'reasons', reasons);
end $$;


--
-- Name: huddle_apply(jsonb, jsonb); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.huddle_apply(p_doc jsonb, p_items jsonb) RETURNS jsonb
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'crm', 'public', 'extensions'
    AS $$
declare
  v_run_id       bigint;
  v_doc_id       text := p_doc->>'doc_id';
  v_meeting_date date := nullif(p_doc->>'meeting_date','')::date;
  v_item         jsonb;
  v_owner        text;
  v_owner_id     uuid;
  v_client       text;
  v_deal_id      uuid;
  v_status       crm.todo_status;
  v_blocked      boolean;
  v_action       text;
  v_detail       text;
  v_todo_id      uuid;
  v_new_deal     boolean;
  n_items int := 0; n_todos int := 0; n_deals int := 0; n_comments int := 0;
begin
  if v_doc_id is null then
    raise exception 'huddle_apply: doc_id is required';
  end if;

  insert into crm.huddle_run (doc_id, doc_title, doc_modified_at, meeting_date, model, raw_extract)
  values (v_doc_id, p_doc->>'doc_title',
          nullif(p_doc->>'doc_modified_at','')::timestamptz,
          v_meeting_date, p_doc->>'model', p_items)
  on conflict (doc_id) do nothing
  returning id into v_run_id;

  if v_run_id is null then
    return jsonb_build_object('skipped', true, 'reason', 'already_processed', 'doc_id', v_doc_id);
  end if;

  for v_item in select * from jsonb_array_elements(p_items)
  loop
    n_items := n_items + 1;
    v_owner   := btrim(coalesce(v_item->>'owner',''));
    v_action  := btrim(coalesce(v_item->>'action',''));
    v_detail  := nullif(btrim(coalesce(v_item->>'detail','')),'');
    v_client  := nullif(btrim(coalesce(v_item->>'related_client','')),'');
    v_blocked := coalesce((v_item->>'is_blocker')::boolean, false);

    -- status: explicit blocker flag wins, else provided status, else pipeline
    if v_blocked then
      v_status := 'blocker';
    else
      begin v_status := (nullif(v_item->>'status',''))::crm.todo_status;
      exception when others then v_status := 'pipeline'; end;
      v_status := coalesce(v_status, 'pipeline');
    end if;

    -- resolve owner -> app_user (group keywords => unassigned)
    v_owner_id := null;
    if v_owner <> '' and lower(v_owner) not in
        ('el grupo','the group','el equipo','the team','grupo','equipo','team','todos','all','everyone') then
      select id into v_owner_id
      from crm.app_user
      where name ilike '%'||v_owner||'%'
         or v_owner ilike '%'||split_part(name,' ',1)||'%'
      order by similarity(name, v_owner) desc
      limit 1;
      if v_owner_id is null and length(v_owner) > 2 then
        insert into crm.app_user (name, role, active)
        values (initcap(v_owner), 'member', true)
        returning id into v_owner_id;
      end if;
    end if;

    -- try to attach to an existing deal card by client name
    v_deal_id := null; v_new_deal := false;
    if v_client is not null and length(v_client) >= 3 then
      select d.id into v_deal_id
      from crm.deal d
      left join crm.account a on a.id = d.account_id
      where d.name ilike '%'||v_client||'%'
         or a.name ilike '%'||v_client||'%'
      order by greatest(similarity(d.name, v_client),
                        similarity(coalesce(a.name,''), v_client)) desc
      limit 1;

      if v_deal_id is null then
        insert into crm.deal (name, stage, source, status_note)
        values (v_client, 'lead', 'huddle',
                'Auto-created from Newman Daily Huddle '||coalesce(v_meeting_date::text,''))
        returning id into v_deal_id;
        v_new_deal := true;
        n_deals := n_deals + 1;
      end if;

      -- comment + activity on the matched/created card
      insert into crm.deal_comment (deal_id, author, body)
      values (v_deal_id, 'huddle-agent',
              format('[Huddle %s] %s%s%s',
                     coalesce(v_meeting_date::text,'?'),
                     coalesce(nullif(v_owner,''),'Team')||': '||v_action,
                     case when v_detail is not null then E'\n'||v_detail else '' end,
                     case when v_blocked then E'\n⛔ Blocker: '||coalesce(v_item->>'blocked_reason','see notes') else '' end));
      n_comments := n_comments + 1;

      insert into crm.deal_event (deal_id, actor, detail)
      values (v_deal_id, 'huddle-agent',
              case when v_new_deal then 'Card created from huddle: ' else 'Huddle note: ' end || v_action);
    end if;

    -- create the todo (idempotent via partial unique index)
    insert into crm.todo (title, detail, status, owner_id, deal_id, source,
                          source_doc_id, source_line, is_blocked, blocked_reason)
    values (v_action, v_detail, v_status, v_owner_id, v_deal_id, 'huddle',
            v_doc_id,
            coalesce(nullif(v_owner,'')||': ','')||v_action,
            v_blocked, nullif(v_item->>'blocked_reason',''))
    on conflict do nothing
    returning id into v_todo_id;
    if v_todo_id is not null then n_todos := n_todos + 1; end if;
  end loop;

  update crm.huddle_run
     set items_extracted = n_items, todos_created = n_todos,
         deals_created = n_deals, comments_created = n_comments
   where id = v_run_id;

  return jsonb_build_object(
    'skipped', false, 'doc_id', v_doc_id, 'run_id', v_run_id,
    'items', n_items, 'todos_created', n_todos,
    'deals_created', n_deals, 'comments_created', n_comments);
end;
$$;


--
-- Name: is_admin(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.is_admin() RETURNS boolean
    LANGUAGE sql STABLE SECURITY DEFINER
    SET search_path TO 'crm', 'public'
    AS $$
  select coalesce(crm.my_role() = 'admin', false);
$$;


--
-- Name: is_approver(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.is_approver() RETURNS boolean
    LANGUAGE sql STABLE
    SET search_path TO 'crm', 'public'
    AS $$
  select crm.my_role() in ('admin','compliance');
$$;


--
-- Name: is_newman(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.is_newman() RETURNS boolean
    LANGUAGE sql STABLE
    AS $$
  select split_part(lower(coalesce((auth.jwt()->>'email'),'')), '@', 2) = 'newman.re';
$$;


--
-- Name: migrate_stages(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.migrate_stages() RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare f record; v_dpd int; v_out numeric; v_stage int; v_prev int; v_pit numeric; v_life numeric; v_lgd numeric; v_prov numeric;
begin
  for f in select fa.*, d.pd, d.lgd, d.ecl_stage as prev_stage, d.counterparty_id as cp, d.name
           from crm.facility fa join crm.deal d on d.id=fa.deal_id
           where fa.status in ('active','npl','cured','restructured') loop
    v_dpd := crm.compute_dpd(f.id);
    v_out := greatest(0, f.principal_mxn - coalesce((select sum(allocated_principal) from crm.repayment where facility_id=f.id),0));
    -- forward-looking SICR: a fired covenant breach forces at least Stage 2 even at 0 dpd
    v_stage := case when v_dpd>=90 then 3 when v_dpd>=30 then 2
                    when exists (select 1 from crm.covenant_test c where c.facility_id=f.id and c.sicr_fired and c.period > current_date - 400) then 2
                    else 1 end;
    v_prev := coalesce(f.prev_stage, 1);
    v_pit := coalesce(crm._pit_pd(f.deal_id), f.pd, 0.05);
    v_life := coalesce(crm._lifetime_pd(f.deal_id), least(1, v_pit*greatest(1,f.tenor_months/12.0)));
    v_lgd := coalesce((crm.compute_lgd(f.deal_id, v_out)->>'lgd')::numeric, f.lgd, 0.45);
    if not exists (select 1 from crm.collateral where deal_id=f.deal_id and status='active') then v_lgd := coalesce(f.lgd, 0.45); end if;
    v_prov := case v_stage when 3 then v_lgd*v_out when 2 then v_life*v_lgd*v_out else v_pit*v_lgd*v_out end;
    update crm.deal set ead_mxn=round(v_out), ecl_stage=v_stage, ecl_provision=round(v_prov), el_mxn=round(v_prov), pd=v_pit, lgd=round(v_lgd,4), updated_at=now() where id=f.deal_id;
    update crm.facility set status = case when v_stage=3 then 'npl' when v_stage=1 and f.status='npl' then 'cured' else f.status end where id=f.id;
    if v_stage > v_prev and v_stage >= 2 then
      perform crm._notify_compliance('stage_migration','Migración de etapa IFRS9 — Etapa '||v_stage,
        coalesce(f.name,'Deudor')||' — '||(case when v_dpd>=30 then v_dpd||' días de mora' else 'incumplimiento de covenant DSCR (SICR prospectivo)' end)||' (Etapa '||v_prev||'→'||v_stage||')', f.cp, f.deal_id);
    end if;
  end loop;
end $$;


--
-- Name: monitor_covenants(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.monitor_covenants() RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare f record; v_sched numeric; v_paid numeric; v_proj numeric; v_cov numeric;
begin
  for f in select * from crm.facility where status in ('active','restructured') and disburse_date is not null loop
    -- scheduled vs actually-serviced over the trailing 12 periods that are due
    select coalesce(sum(total_due),0) into v_sched from crm.facility_schedule where facility_id=f.id and due_date <= current_date and due_date > current_date - interval '365 days';
    select coalesce(sum(amount_mxn),0) into v_paid from crm.repayment where facility_id=f.id and received_at > current_date - interval '365 days';
    if v_sched <= 0 then continue; end if;
    v_proj := round(v_paid / v_sched, 3);            -- realized debt-service coverage proxy
    v_cov := coalesce(f.dscr_target, 1.20);
    insert into crm.covenant_test(facility_id, projected_dscr, covenant_dscr, source, breach, sicr_fired)
      values (f.id, v_proj, v_cov, 'repayment', v_proj < v_cov, v_proj < v_cov);
  end loop;
  perform crm.migrate_stages();   -- re-stage on the fresh covenant signal
end $$;


--
-- Name: my_app_user_id(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.my_app_user_id() RETURNS uuid
    LANGUAGE sql STABLE SECURITY DEFINER
    SET search_path TO 'crm', 'public'
    AS $$
  select id from crm.app_user where auth_uid = auth.uid() and active limit 1;
$$;


--
-- Name: my_role(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.my_role() RETURNS crm.user_role
    LANGUAGE sql STABLE SECURITY DEFINER
    SET search_path TO 'crm', 'public'
    AS $$
  select role from crm.app_user where auth_uid = auth.uid() and active limit 1;
$$;


--
-- Name: norm_email(text); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.norm_email(p text) RETURNS text
    LANGUAGE sql IMMUTABLE
    AS $$
  select nullif(lower(trim(coalesce(p,''))),'') $$;


--
-- Name: norm_phone(text); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.norm_phone(p text) RETURNS text
    LANGUAGE sql IMMUTABLE
    AS $$
  select nullif(right(regexp_replace(coalesce(p,''),'[^0-9]','','g'), 10),'') $$;


--
-- Name: notification_scan(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.notification_scan() RETURNS jsonb
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'crm', 'public'
    AS $$
declare r record; n_kyb int:=0; n_sanc int:=0; n_aviso int:=0; n_task int:=0; n_draft int:=0;
begin
  for r in select id, name from crm.counterparty where clearance_status = 'requested' loop
    perform crm._notify_approvers('kyb_clearance', 'Liberación KYB pendiente',
      'Contraparte '||coalesce(r.name,'(sin nombre)')||' espera dictamen de cumplimiento.',
      'counterparty', r.id, null, 'kyb_clearance', '/avisos', null, 2, 'kyb:'||r.id);
    n_kyb := n_kyb + 1;
  end loop;
  update crm.notification set action_state='acted', acted_by='system', acted_at=now()
    where action_type='kyb_clearance' and action_state='pending'
      and entity_id not in (select id from crm.counterparty where clearance_status='requested');

  for r in select m.id, m.deal_id, d.name from crm.credit_memo m join crm.deal d on d.id=m.deal_id
           where m.status='submitted' loop
    perform crm._notify_approvers('credit_sanction', 'Sanción de crédito pendiente',
      'El memo de '||coalesce(r.name,'(deal)')||' espera sanción de un aprobador distinto.',
      'deal', r.deal_id, r.deal_id, 'credit_sanction', '/deals/'||r.deal_id, null, 3, 'sanction:'||r.id);
    n_sanc := n_sanc + 1;
  end loop;
  update crm.notification set action_state='acted', acted_by='system', acted_at=now()
    where action_type='credit_sanction' and action_state='pending'
      and entity_id not in (select deal_id from crm.credit_memo where status='submitted');

  for r in select id, periodo_anio, periodo_mes, due_date from crm.aviso_batch
           where estatus not in ('presentado','sin_operaciones') loop
    perform crm._notify_approvers('aviso_sla',
      'Aviso SPPLD '||lpad(r.periodo_mes::text,2,'0')||'/'||r.periodo_anio||
        case when r.due_date < current_date then ' — VENCIDO' else ' por presentar' end,
      'Periodo pendiente ante la UIF (fecha límite '||coalesce(r.due_date::text,'?')||').',
      'aviso', r.id, null, 'aviso_sla', '/avisos', r.due_date::timestamptz,
      case when r.due_date < current_date then 4 else 2 end, 'aviso:'||r.id);
    n_aviso := n_aviso + 1;
  end loop;
  update crm.notification set action_state='acted', acted_by='system', acted_at=now()
    where action_type='aviso_sla' and action_state='pending'
      and entity_id not in (select id from crm.aviso_batch where estatus not in ('presentado','sin_operaciones'));

  for r in select id, assignee, title, deal_id, due_at from crm.task
           where status <> 'done' and due_at is not null and due_at <= now() + interval '1 day' loop
    perform crm._notify_user(r.assignee, 'task',
      case when r.due_at < now() then 'Tarea vencida' else 'Tarea para hoy' end,
      r.title, 'task', r.id, r.deal_id, 'task',
      coalesce('/deals/'||r.deal_id, '/mi-dia'), r.due_at,
      case when r.due_at < now() then 3 else 1 end, 'task:'||r.id);
    n_task := n_task + 1;
  end loop;
  update crm.notification set action_state='acted', acted_by='system', acted_at=now()
    where action_type='task' and action_state='pending'
      and entity_id not in (select id from crm.task where status <> 'done' and due_at is not null);

  for r in select id, deal_id, created_by from crm.ai_draft where status='draft' and coalesce(created_by,'') <> '' loop
    perform crm._notify_user(r.created_by, 'ai_draft', 'Borrador IA por revisar',
      'Un borrador generado espera tu aprobación antes de enviarse.',
      'deal', r.id, r.deal_id, 'ai_draft', '/deals/'||r.deal_id, null, 1, 'aidraft:'||r.id);
    n_draft := n_draft + 1;
  end loop;
  update crm.notification set action_state='acted', acted_by='system', acted_at=now()
    where action_type='ai_draft' and action_state='pending'
      and entity_id not in (select id from crm.ai_draft where status='draft');

  return jsonb_build_object('kyb',n_kyb,'sanctions',n_sanc,'avisos',n_aviso,'tasks',n_task,'drafts',n_draft);
end $$;


--
-- Name: process_automations(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.process_automations() RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare e record; r record; act jsonb; fired text[]; lbl text;
begin
  perform set_config('crm.suppress_events','on', true);   -- prevent action-driven event storms this tx
  for e in select * from crm.automation_event where processed_at is null order by created_at limit 200 loop
    -- inbound reply exits any active sequences on this deal
    if e.event_type='inbound_received' then
      update crm.sequence_enrollment se set status='exited', exit_reason='replied'
        from crm.sequence s where s.id=se.sequence_id and s.exit_on_reply and se.deal_id=e.entity_id and se.status='active';
    end if;
    for r in select * from crm.automation_recipe where enabled and trigger_type=e.event_type loop
      -- trigger_config match (e.g. stage_enter with a specific stage) + conditions
      if (r.trigger_config->>'stage' is null or r.trigger_config->>'stage' = e.payload->>'stage')
         and crm._match_conditions(e.entity_id, r.conditions) then
        begin
          fired := array[]::text[];
          for act in select to_jsonb(a) from crm.automation_action a where a.recipe_id=r.id order by a.seq loop
            fired := fired || crm._fire_action(act, e.entity_id);
          end loop;
          insert into crm.automation_run(recipe_id, event_id, entity_id, status, actions_fired)
            values (r.id, e.id, e.entity_id, 'fired', to_jsonb(fired))
            on conflict (recipe_id, event_id) do nothing;
        exception when others then
          insert into crm.automation_run(recipe_id, event_id, entity_id, status, error)
            values (r.id, e.id, e.entity_id, 'error', sqlerrm) on conflict (recipe_id, event_id) do nothing;
        end;
      end if;
    end loop;
    update crm.automation_event set processed_at=now() where id=e.id;
  end loop;
end $$;


--
-- Name: recompute_all_coverage(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.recompute_all_coverage() RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare f record; begin
  perform set_config('crm.suppress_events','on', true);
  for f in select fa.deal_id from crm.facility fa join crm.facility_base_case b on b.facility_id=fa.id and b.active where fa.status in ('active','npl','restructured') loop
    perform public.crm_web_compute_coverage(f.deal_id, current_date);
  end loop;
end $$;


--
-- Name: refresh_schedule_forecasts(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.refresh_schedule_forecasts() RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare pr record; v_prev int; v_new jsonb;
begin
  for pr in select p.id, p.deal_id, p.name, d.counterparty_id from crm.project p join crm.deal d on d.id=p.deal_id
            where not exists (select 1 from crm.ld_accrual l where l.project_id=p.id and l.cod_actual is not null) loop
    select slip_days into v_prev from crm.schedule_forecast where project_id=pr.id order by run_at desc limit 1;
    perform set_config('crm.suppress_events','on', true);
    v_new := public.crm_web_compute_schedule(pr.deal_id);
    if (v_new->>'slip_days')::int > 0 and coalesce(v_prev,-999) <= 0 then
      perform crm._notify_compliance('cod_forecast_slip','COD pronosticado tarde — '||(v_new->>'slip_days')||'d',
        coalesce(pr.name,'Proyecto')||' — LD pronosticada '||coalesce(v_new->>'net_forecast_ld','0'), pr.counterparty_id, pr.deal_id);
    end if;
  end loop;
end $$;


--
-- Name: require_training(text); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.require_training(p_topic text) RETURNS void
    LANGUAGE plpgsql STABLE
    AS $$
begin
  if not crm.training_current(p_topic) then
    raise exception 'Capacitacion % vencida o ausente — accion bloqueada (Art.20 fr.IV LFPIORPI)', p_topic using errcode='P0001';
  end if;
end $$;


--
-- Name: resolve_comms_party(text, text); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.resolve_comms_party(p_kind text, p_value text) RETURNS TABLE(contact_id uuid, deal_id uuid, confidence numeric)
    LANGUAGE plpgsql STABLE
    SET search_path TO 'crm', 'public'
    AS $$
declare v_norm text;
begin
  v_norm := case when p_kind='phone' then crm.norm_phone(p_value) else crm.norm_email(p_value) end;
  if v_norm is null then return; end if;
  return query select i.contact_id, i.deal_id, i.confidence from crm.comms_identity i where i.kind=p_kind and i.value_norm=v_norm limit 1;
end $$;


--
-- Name: scan_aml_alerts(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.scan_aml_alerts() RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare c record; v_uma numeric; v_agg numeric; v_n int; v_pep boolean; v_estado text; v_deal uuid; v_prof record;
        v_codes text[]; v_score numeric; v_prepay numeric; v_sched numeric; v_dedup text; v_hits int;
begin
  perform set_config('crm.suppress_events','on', true);
  v_uma := crm.uma_diaria(); v_dedup := to_char(current_date,'YYYY-MM');
  for c in select id, ebr_grade, dd_status from crm.counterparty loop
    select coalesce(sum(monto_mxn),0), count(*) into v_agg, v_n from crm.dd_operation where counterparty_id=c.id and fecha > current_date - interval '6 months';
    if v_n = 0 and coalesce(c.ebr_grade,'') <> 'alto' then continue; end if;
    select bool_or(is_pep) into v_pep from crm.dd_ubo where counterparty_id=c.id;
    select d.id, d.estado into v_deal, v_estado from crm.deal d where d.counterparty_id=c.id limit 1;
    select * into v_prof from crm.transaction_profile where counterparty_id=c.id order by version desc limit 1;
    select count(*) into v_hits from crm.dd_screening_hit where counterparty_id=c.id and disposition='pending';
    v_codes := '{}'; v_score := 0;
    if coalesce(c.ebr_grade,'')='alto' and v_n>0 then v_codes := array_append(v_codes, 'ebr_alto'); v_score := v_score+0.30; end if;
    if coalesce(v_pep,false) and v_n>0 then v_codes := array_append(v_codes, 'pep_activity'); v_score := v_score+0.35; end if;
    if v_prof.expected_amount_uma_max is not null and (v_agg/v_uma) > v_prof.expected_amount_uma_max then v_codes := array_append(v_codes, 'profile_deviation'); v_score := v_score+0.40; end if;
    if v_n >= 3 and (v_agg/v_uma) > 3210 and not exists (select 1 from crm.dd_operation where counterparty_id=c.id and monto_mxn/v_uma > 3210) then v_codes := array_append(v_codes, 'fraccionamiento'); v_score := v_score+0.40; end if;
    if crm._estado_risk(v_estado) = 3 and v_n>0 then v_codes := array_append(v_codes, 'geography'); v_score := v_score+0.20; end if;
    if array_length(v_codes,1) is null or v_score < 0.30 then continue; end if;
    insert into crm.aml_alert(counterparty_id, deal_id, rule_codes, score, dedup_key, signals)
      values (c.id, v_deal, v_codes, round(v_score,2), v_dedup,
        jsonb_build_object('pep',coalesce(v_pep,false),'ebr_grade',c.ebr_grade,'estado',v_estado,'agg_6m',round(v_agg),'agg_6m_uma',round(v_agg/v_uma),'ops_6m',v_n,'screening_pending',v_hits))
      on conflict (counterparty_id, dedup_key) do update set rule_codes=excluded.rule_codes, score=excluded.score, signals=excluded.signals;
    perform crm._notify_compliance('aml_alert','Alerta de operación inusual', 'Score '||round(v_score,2)||' — '||array_to_string(v_codes,', '), c.id, v_deal);
  end loop;
end $$;


--
-- Name: scan_scheduled_automations(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.scan_scheduled_automations() RETURNS void
    LANGUAGE plpgsql
    SET search_path TO 'crm', 'public'
    AS $$
declare r record; d record; n int; act jsonb; fired text[]; v_evt uuid;
begin
  perform set_config('crm.suppress_events','on', true);
  for r in select * from crm.automation_recipe where enabled and trigger_type='deal_untouched_days' loop
    n := coalesce(nullif(r.trigger_config->>'days','')::int, 7);
    for d in select e.deal_id from crm_deal_engagement e join crm.deal dl on dl.id=e.deal_id
             where dl.stage not in ('closed','perdido') and e.last_touch < now() - make_interval(days => n) loop
      if not crm._match_conditions(d.deal_id, r.conditions) then continue; end if;
      -- one run per (recipe, deal, day) via a synthetic daily event
      insert into crm.automation_event(event_type, entity_id, payload, processed_at)
        values ('deal_untouched_days', d.deal_id, jsonb_build_object('deal_id', d.deal_id, 'day', current_date), now())
        returning id into v_evt;
      if exists (select 1 from crm.automation_run ar join crm.automation_event ae on ae.id=ar.event_id
                 where ar.recipe_id=r.id and ae.entity_id=d.deal_id and ae.event_type='deal_untouched_days'
                   and (ae.payload->>'day')::date = current_date and ar.id is not null limit 1) then continue; end if;
      fired := array[]::text[];
      for act in select to_jsonb(a) from crm.automation_action a where a.recipe_id=r.id order by a.seq loop
        fired := fired || crm._fire_action(act, d.deal_id);
      end loop;
      insert into crm.automation_run(recipe_id, event_id, entity_id, status, actions_fired)
        values (r.id, v_evt, d.deal_id, 'fired', to_jsonb(fired)) on conflict (recipe_id,event_id) do nothing;
    end loop;
  end loop;
end $$;


--
-- Name: set_updated_at(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.set_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
begin new.updated_at := now(); return new; end;
$$;


--
-- Name: training_current(text); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.training_current(p_topic text) RETURNS boolean
    LANGUAGE sql STABLE SECURITY DEFINER
    SET search_path TO 'crm', 'public'
    AS $$
  select exists (select 1 from crm.training_completion tc
    where tc.app_user_id = crm.my_app_user_id() and tc.topic = p_topic
      and coalesce(tc.expires_on, tc.completed_on + interval '12 months') >= current_date);
$$;


--
-- Name: txn_monitor_scan(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.txn_monitor_scan() RETURNS jsonb
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'crm', 'public'
    AS $$
declare cfg record; uma numeric; r record; v_evid uuid; n_or int:=0; n_fr int:=0; n_dev int:=0;
        v_period text; v_due date; v_thresh_mxn numeric;
begin
  select * into cfg from crm.uma_config where active order by created_at desc limit 1;
  if cfg.id is null then return jsonb_build_object('ok',false,'error','sin uma_config'); end if;
  uma := crm.uma_diaria();
  v_thresh_mxn := cfg.or_threshold_uma * uma;
  for r in select o.id, o.counterparty_id, o.monto_mxn, o.fecha, coalesce(o.tipo,'operacion') tipo
           from crm.dd_operation o where o.counterparty_id is not null and o.monto_mxn >= v_thresh_mxn loop
    v_period := to_char(r.fecha,'YYYY-MM'); v_due := (date_trunc('month', r.fecha) + interval '1 month' + interval '16 days')::date;
    insert into crm.txn_monitor_event(counterparty_id, event_type, window_start, window_end, aggregate_amount_mxn, uma_multiple, detail, severity, dedupe_key)
      values (r.counterparty_id,'operacion_relevante', r.fecha, r.fecha, r.monto_mxn, round(r.monto_mxn/uma), 'Operacion '||r.tipo||' >= '||cfg.or_threshold_uma||' UMA', 2, 'or:'||r.id)
      on conflict (dedupe_key) do nothing returning id into v_evid;
    if v_evid is not null then
      insert into crm.operacion_relevante(counterparty_id, period, instrument, amount_mxn, uma_multiple, trigger_event_id, due_at, dedupe_key)
        values (r.counterparty_id, v_period, r.tipo, r.monto_mxn, round(r.monto_mxn/uma), v_evid, v_due, 'oro:'||r.id) on conflict (dedupe_key) do nothing;
      n_or := n_or + 1;
    end if;
  end loop;
  for r in select counterparty_id, sum(monto_mxn) agg, count(*) n, min(fecha) f0, max(fecha) f1
           from crm.dd_operation
           where counterparty_id is not null and monto_mxn < v_thresh_mxn and monto_mxn >= cfg.structuring_uma_floor*uma
             and fecha >= current_date - (cfg.structuring_window_days||' days')::interval
           group by counterparty_id having sum(monto_mxn) >= v_thresh_mxn and count(*) >= 2 loop
    insert into crm.txn_monitor_event(counterparty_id, event_type, window_start, window_end, aggregate_amount_mxn, uma_multiple, detail, severity, dedupe_key)
      values (r.counterparty_id,'fraccionamiento', r.f0, r.f1, r.agg, round(r.agg/uma),
        r.n||' operaciones sub-umbral suman '||round(r.agg/uma)||' UMA en '||cfg.structuring_window_days||' dias', 3,
        'fr:'||r.counterparty_id||':'||to_char(current_date,'YYYYMM'))
      on conflict (dedupe_key) do nothing;
    if found then n_fr := n_fr + 1; end if;
  end loop;
  for r in select p.counterparty_id, p.expected_monthly_volume_mxn ev, p.expected_max_single_mxn emx,
                  coalesce((select sum(monto_mxn) from crm.dd_operation o where o.counterparty_id=p.counterparty_id and o.fecha >= current_date-interval '30 days'),0) actual,
                  coalesce((select max(monto_mxn) from crm.dd_operation o where o.counterparty_id=p.counterparty_id and o.fecha >= current_date-interval '30 days'),0) actual_max
           from crm.txn_profile p where p.status='approved'
             and p.version = (select max(version) from crm.txn_profile p2 where p2.counterparty_id=p.counterparty_id and p2.status='approved') loop
    if (r.ev is not null and r.ev > 0 and r.actual > r.ev * cfg.deviation_ratio_trigger)
       or (r.emx is not null and r.emx > 0 and r.actual_max > r.emx * cfg.deviation_ratio_trigger) then
      insert into crm.txn_monitor_event(counterparty_id, event_type, window_start, window_end, aggregate_amount_mxn, uma_multiple, detail, severity, dedupe_key)
        values (r.counterparty_id,'profile_deviation', current_date-30, current_date, r.actual, round(r.actual/uma),
          'Actividad 30d ('||round(r.actual)||') excede el perfil declarado x'||cfg.deviation_ratio_trigger, 3,
          'dev:'||r.counterparty_id||':'||to_char(current_date,'YYYYMM'))
        on conflict (dedupe_key) do nothing;
      if found then n_dev := n_dev + 1; end if;
    end if;
  end loop;
  for r in select id, counterparty_id, event_type, detail, severity from crm.txn_monitor_event where status='open' loop
    perform crm._notify_approvers('txn_alert', 'Alerta de monitoreo - '||r.event_type,
      coalesce(r.detail,''), 'counterparty', r.counterparty_id, null, 'txn_alert', '/monitoreo', null, r.severity, 'txnev:'||r.id);
  end loop;
  return jsonb_build_object('ok',true,'operaciones_relevantes',n_or,'fraccionamiento',n_fr,'profile_deviation',n_dev);
end $$;


--
-- Name: ubo_gate(uuid); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.ubo_gate(p_cp uuid) RETURNS jsonb
    LANGUAGE plpgsql STABLE
    SET search_path TO 'crm', 'public'
    AS $$
declare v_type text; v_ubos int; v_screen text; v_undisposed int; v_acta int; v_estr int; reasons text[] := '{}';
begin
  select entity_type into v_type from crm.counterparty where id=p_cp;
  if coalesce(v_type,'') <> 'persona_moral' then return jsonb_build_object('ok',true,'reasons',reasons); end if;
  select count(*) into v_ubos from crm.dd_ubo where counterparty_id=p_cp and is_ubo;
  if v_ubos = 0 then reasons := array_append(reasons, 'Sin beneficiarios controladores identificados'); end if;
  select status into v_screen from crm.dd_check where counterparty_id=p_cp and check_type='sanctions_pep';
  if coalesce(v_screen,'') <> 'pass' then reasons := array_append(reasons, 'Screening de sanciones/PEP no aprobado sobre los UBOs'); end if;
  select count(*) into v_undisposed from crm.dd_screening_hit where counterparty_id=p_cp and subject='ubo' and disposition='pending';
  if v_undisposed > 0 then reasons := array_append(reasons, (v_undisposed||' coincidencia(s) de UBO sin dictaminar')); end if;
  select count(*) into v_acta from crm.dd_ubo_document where counterparty_id=p_cp and doc_type='acta_constitutiva' and verified_by is not null;
  select count(*) into v_estr from crm.dd_ubo_document where counterparty_id=p_cp and doc_type='estructura_accionaria' and verified_by is not null;
  if v_acta = 0 then reasons := array_append(reasons, 'Falta acta constitutiva verificada'); end if;
  if v_estr = 0 then reasons := array_append(reasons, 'Falta estructura accionaria verificada'); end if;
  return jsonb_build_object('ok', array_length(reasons,1) is null, 'reasons', reasons);
end $$;


--
-- Name: uma_diaria(); Type: FUNCTION; Schema: crm; Owner: -
--

CREATE FUNCTION crm.uma_diaria() RETURNS numeric
    LANGUAGE sql IMMUTABLE
    AS $$ select 113.14::numeric $$;


--
-- Name: deal_summary; Type: VIEW; Schema: crm; Owner: -
--

CREATE VIEW crm.deal_summary AS
SELECT
    NULL::uuid AS id,
    NULL::text AS name,
    NULL::crm.deal_stage AS stage,
    NULL::text AS rpu,
    NULL::uuid AS owner_id,
    NULL::uuid AS account_id,
    NULL::date AS expected_close_date,
    NULL::timestamp with time zone AS updated_at,
    NULL::bigint AS monday_item_id,
    NULL::numeric AS total_kwp,
    NULL::numeric AS total_epc_value,
    NULL::numeric AS total_vpn;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: account; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.account (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    rfc text,
    industry text,
    notes text,
    monday_item_id bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: activity; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.activity (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid,
    contact_id uuid,
    type text DEFAULT 'note'::text NOT NULL,
    direction text DEFAULT 'internal'::text NOT NULL,
    subject text,
    body text,
    channel_meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    occurred_at timestamp with time zone DEFAULT now() NOT NULL,
    logged_by text DEFAULT 'web'::text NOT NULL,
    external_id text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    source text DEFAULT 'web'::text NOT NULL,
    ingest_status text DEFAULT 'linked'::text NOT NULL,
    CONSTRAINT activity_dir CHECK ((direction = ANY (ARRAY['inbound'::text, 'outbound'::text, 'internal'::text]))),
    CONSTRAINT activity_scope CHECK (((deal_id IS NOT NULL) OR (contact_id IS NOT NULL) OR (ingest_status = 'unlinked'::text))),
    CONSTRAINT activity_type CHECK ((type = ANY (ARRAY['email'::text, 'whatsapp'::text, 'call'::text, 'meeting'::text, 'note'::text])))
);


--
-- Name: ai_draft; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.ai_draft (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid,
    action text DEFAULT 'draft'::text NOT NULL,
    channel text,
    title text,
    body text NOT NULL,
    status text DEFAULT 'draft'::text NOT NULL,
    model text,
    grounding_hash text,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    decided_by text,
    decided_at timestamp with time zone,
    CONSTRAINT ai_draft_status_check CHECK ((status = ANY (ARRAY['draft'::text, 'approved'::text, 'discarded'::text])))
);


--
-- Name: ai_prompt_log; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.ai_prompt_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    actor text,
    action text NOT NULL,
    deal_id uuid,
    model text,
    channel text,
    grounding_hash text,
    prompt_chars integer,
    output_chars integer,
    latency_ms integer,
    est_cost_usd numeric,
    ok boolean DEFAULT true NOT NULL,
    error text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: aml_alert; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.aml_alert (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    counterparty_id uuid NOT NULL,
    deal_id uuid,
    triggered_at timestamp with time zone DEFAULT now() NOT NULL,
    rule_codes text[] DEFAULT '{}'::text[] NOT NULL,
    score numeric DEFAULT 0 NOT NULL,
    signals jsonb DEFAULT '{}'::jsonb NOT NULL,
    status text DEFAULT 'open'::text NOT NULL,
    dedup_key text NOT NULL,
    CONSTRAINT aml_alert_status_check CHECK ((status = ANY (ARRAY['open'::text, 'in_review'::text, 'dictamen_report'::text, 'dictamen_dismiss'::text])))
);


--
-- Name: aml_audit; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.aml_audit (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    period text NOT NULL,
    scope text DEFAULT 'clearances'::text NOT NULL,
    sample_size integer,
    drawn_by text,
    drawn_at timestamp with time zone DEFAULT now() NOT NULL,
    status text DEFAULT 'open'::text NOT NULL,
    independent boolean DEFAULT true NOT NULL,
    CONSTRAINT aml_audit_status_check CHECK ((status = ANY (ARRAY['open'::text, 'in_review'::text, 'closed'::text])))
);


--
-- Name: aml_audit_item; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.aml_audit_item (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    audit_id uuid NOT NULL,
    subject_kind text,
    subject_id uuid,
    subject_label text,
    result text,
    finding text,
    remediation text,
    remediated boolean DEFAULT false NOT NULL,
    reviewed_by text,
    reviewed_at timestamp with time zone,
    CONSTRAINT aml_audit_item_result_check CHECK ((result = ANY (ARRAY['conforme'::text, 'no_conforme'::text, 'observacion'::text])))
);


--
-- Name: aml_case; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.aml_case (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    alert_id uuid NOT NULL,
    assigned_officer text,
    opened_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: aml_control; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.aml_control (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    code text NOT NULL,
    name text NOT NULL,
    line_of_defense integer NOT NULL,
    owner_role text,
    frequency text,
    automated boolean DEFAULT false NOT NULL,
    system_ref text,
    active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT aml_control_line_of_defense_check CHECK ((line_of_defense = ANY (ARRAY[1, 2, 3])))
);


--
-- Name: aml_control_clause; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.aml_control_clause (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    control_id uuid NOT NULL,
    manual_version text NOT NULL,
    clause_ref text NOT NULL,
    note text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: aml_designation; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.aml_designation (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    role_type text NOT NULL,
    app_user_id uuid,
    person_name text,
    cargo text,
    designated_at date,
    revoked_at date,
    designated_by text,
    approved_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT aml_designation_role_type_check CHECK ((role_type = ANY (ARRAY['representante'::text, 'oficial_cumplimiento'::text, 'ccc_miembro'::text, 'ccc_presidente'::text, 'auditor_independiente'::text]))),
    CONSTRAINT desig_four_eyes CHECK (((approved_by IS NULL) OR (approved_by <> designated_by)))
);


--
-- Name: aml_dictamen; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.aml_dictamen (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    case_id uuid NOT NULL,
    decision text NOT NULL,
    rationale text NOT NULL,
    decided_by text,
    reviewed_by text,
    decided_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT aml_dictamen_decision_check CHECK ((decision = ANY (ARRAY['report'::text, 'dismiss'::text]))),
    CONSTRAINT dic_four_eyes CHECK (((reviewed_by IS NULL) OR (reviewed_by <> decided_by)))
);


--
-- Name: aml_manual; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.aml_manual (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    version text NOT NULL,
    title text DEFAULT 'Manual de Cumplimiento LFPIORPI'::text NOT NULL,
    body text,
    effective_date date,
    status text DEFAULT 'draft'::text NOT NULL,
    authored_by text,
    approved_by text,
    approved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT aml_manual_status_check CHECK ((status = ANY (ARRAY['draft'::text, 'approved'::text, 'superseded'::text]))),
    CONSTRAINT manual_four_eyes CHECK (((approved_by IS NULL) OR (approved_by <> authored_by)))
);


--
-- Name: aml_rule; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.aml_rule (
    code text NOT NULL,
    category text NOT NULL,
    description text,
    weight numeric DEFAULT 0.3 NOT NULL,
    params jsonb DEFAULT '{}'::jsonb NOT NULL,
    active boolean DEFAULT true NOT NULL,
    methodology_version integer DEFAULT 1 NOT NULL
);


--
-- Name: app_user; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.app_user (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    auth_uid uuid,
    monday_user_id bigint,
    name text NOT NULL,
    email text,
    role crm.user_role DEFAULT 'member'::crm.user_role NOT NULL,
    active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    phone text
);


--
-- Name: automation_action; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.automation_action (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    recipe_id uuid NOT NULL,
    seq integer DEFAULT 1 NOT NULL,
    action_type text NOT NULL,
    action_config jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: automation_event; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.automation_event (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    event_type text NOT NULL,
    entity_type text DEFAULT 'deal'::text NOT NULL,
    entity_id uuid,
    payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    processed_at timestamp with time zone
);


--
-- Name: automation_recipe; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.automation_recipe (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    description text,
    enabled boolean DEFAULT false NOT NULL,
    trigger_type text NOT NULL,
    trigger_config jsonb DEFAULT '{}'::jsonb NOT NULL,
    conditions jsonb DEFAULT '[]'::jsonb NOT NULL,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: automation_run; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.automation_run (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    recipe_id uuid,
    event_id uuid,
    entity_id uuid,
    status text NOT NULL,
    actions_fired jsonb,
    error text,
    ran_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: aviso_batch; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.aviso_batch (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    periodo_anio integer NOT NULL,
    periodo_mes integer NOT NULL,
    tipo text DEFAULT 'mensual_17_frIV'::text NOT NULL,
    estatus text DEFAULT 'abierto'::text NOT NULL,
    due_date date,
    operation_count integer DEFAULT 0 NOT NULL,
    monto_total_uma numeric,
    xml_content text,
    xml_sha text,
    acuse_folio text,
    acuse_note text,
    generated_by text,
    generated_at timestamp with time zone,
    presented_by text,
    presented_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT aviso_batch_estatus_check CHECK ((estatus = ANY (ARRAY['abierto'::text, 'generado'::text, 'presentado'::text, 'vencido'::text, 'sin_operaciones'::text])))
);


--
-- Name: aviso_operation; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.aviso_operation (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    batch_id uuid NOT NULL,
    dd_operation_id uuid,
    deal_id uuid,
    counterparty_id uuid,
    tipo text,
    monto numeric,
    monto_uma numeric,
    fecha_operacion date,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: budget_line; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.budget_line (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid,
    concept text,
    amount_mxn numeric,
    monday_item_id bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: bulk_action_log; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.bulk_action_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    actor text,
    action_type text NOT NULL,
    target_ids uuid[] NOT NULL,
    field text,
    old_values jsonb,
    new_value jsonb,
    affected_count integer DEFAULT 0 NOT NULL,
    skipped jsonb DEFAULT '[]'::jsonb NOT NULL,
    undo_token uuid DEFAULT gen_random_uuid() NOT NULL,
    undone_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: capital_config; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.capital_config (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    version text NOT NULL,
    raroc_hurdle numeric DEFAULT 0.15 NOT NULL,
    cost_of_funds_rate numeric DEFAULT 0.10 NOT NULL,
    opex_rate numeric DEFAULT 0.010 NOT NULL,
    tax_rate numeric DEFAULT 0.30 NOT NULL,
    econ_capital_ratio numeric DEFAULT 0.12 NOT NULL,
    effective_date date DEFAULT CURRENT_DATE NOT NULL,
    approved_by text,
    active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: change_order; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.change_order (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    description text NOT NULL,
    delta_bac numeric DEFAULT 0 NOT NULL,
    delta_contract numeric DEFAULT 0 NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    created_by text,
    approved_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    approved_at timestamp with time zone,
    time_extension_days integer DEFAULT 0 NOT NULL
);


--
-- Name: collateral; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.collateral (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid NOT NULL,
    facility_id uuid,
    instrument_type crm.collateral_type NOT NULL,
    description text,
    gross_value_mxn numeric DEFAULT 0 NOT NULL,
    haircut_pct numeric DEFAULT 0.30 NOT NULL,
    perfection_status crm.perfection_status DEFAULT 'unperfected'::crm.perfection_status NOT NULL,
    perfection_evidence jsonb DEFAULT '{}'::jsonb NOT NULL,
    perfection_date date,
    revalue_method text DEFAULT 'none'::text NOT NULL,
    status crm.collateral_status DEFAULT 'pending_approval'::crm.collateral_status NOT NULL,
    created_by text,
    approved_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT collateral_four_eyes CHECK (((approved_by IS NULL) OR (approved_by <> created_by)))
);


--
-- Name: collateral_haircut; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.collateral_haircut (
    instrument_type crm.collateral_type NOT NULL,
    default_haircut_pct numeric NOT NULL
);


--
-- Name: comms_identity; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.comms_identity (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    kind text NOT NULL,
    value_norm text NOT NULL,
    contact_id uuid,
    deal_id uuid,
    confidence numeric DEFAULT 1 NOT NULL,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT comms_identity_kind_check CHECK ((kind = ANY (ARRAY['email'::text, 'phone'::text])))
);


--
-- Name: comms_outbox; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.comms_outbox (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid,
    contact_id uuid,
    channel text NOT NULL,
    to_address text NOT NULL,
    subject text,
    body text NOT NULL,
    status text DEFAULT 'queued'::text NOT NULL,
    external_id text,
    error text,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    sent_at timestamp with time zone,
    provider text,
    provider_message_id text,
    attempts integer DEFAULT 0 NOT NULL,
    last_error text,
    next_retry_at timestamp with time zone,
    body_html text,
    subject_line text,
    in_reply_to text,
    tracking_id uuid,
    CONSTRAINT comms_outbox_channel_check CHECK ((channel = ANY (ARRAY['email'::text, 'whatsapp'::text]))),
    CONSTRAINT comms_outbox_status_check CHECK ((status = ANY (ARRAY['queued'::text, 'sending'::text, 'sent'::text, 'failed'::text])))
);


--
-- Name: company; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.company (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    razon_social text NOT NULL,
    rfc text,
    nombre_comercial text,
    tipo_persona text,
    sector text,
    estado text,
    canonical boolean DEFAULT true NOT NULL,
    merged_into_id uuid,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: company_merge_log; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.company_merge_log (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    survivor_id uuid,
    merged_id uuid,
    matched_on jsonb,
    requested_by text,
    requested_at timestamp with time zone DEFAULT now() NOT NULL,
    approved_by text,
    approved_at timestamp with time zone,
    status text DEFAULT 'pending'::text NOT NULL,
    reason text,
    CONSTRAINT company_merge_log_status_check CHECK ((status = ANY (ARRAY['pending'::text, 'approved'::text, 'rejected'::text]))),
    CONSTRAINT merge_four_eyes CHECK (((approved_by IS NULL) OR (approved_by <> requested_by)))
);


--
-- Name: company_relationship; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.company_relationship (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    parent_company_id uuid NOT NULL,
    child_company_id uuid NOT NULL,
    rel_type crm.rel_type DEFAULT 'subsidiary'::crm.rel_type NOT NULL,
    pct numeric,
    note text,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT company_relationship_check CHECK ((parent_company_id <> child_company_id))
);


--
-- Name: concentration_cap; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.concentration_cap (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    dimension text NOT NULL,
    bucket_key text,
    basis text DEFAULT 'pct_of_portfolio_ead'::text NOT NULL,
    limit_value numeric NOT NULL,
    warning_pct numeric DEFAULT 0.80 NOT NULL,
    hard boolean DEFAULT true NOT NULL,
    active boolean DEFAULT true NOT NULL,
    note text,
    CONSTRAINT concentration_cap_basis_check CHECK ((basis = ANY (ARRAY['pct_of_portfolio_ead'::text, 'abs_mxn'::text]))),
    CONSTRAINT concentration_cap_dimension_check CHECK ((dimension = ANY (ARRAY['single_obligor'::text, 'connected_group'::text, 'offtaker'::text, 'technology'::text, 'geography'::text])))
);


--
-- Name: concentration_limit; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.concentration_limit (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    dimension text NOT NULL,
    key text,
    limit_pct numeric NOT NULL,
    note text
);


--
-- Name: contact; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.contact (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    account_id uuid,
    name text NOT NULL,
    email text,
    phone text,
    title text,
    status text,
    monday_item_id bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    company text,
    department text,
    mobile text,
    address text,
    city text,
    state text,
    country text,
    website text,
    birthday date,
    notes text,
    labels text[],
    source text,
    google_resource_name text,
    custom jsonb DEFAULT '{}'::jsonb NOT NULL,
    description text,
    company_id uuid,
    owner_id uuid,
    enrich_pending boolean DEFAULT false NOT NULL,
    enrich_asked_at timestamp with time zone
);


--
-- Name: contact_enrich; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.contact_enrich (
    id uuid NOT NULL,
    raw jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: contact_field; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.contact_field (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    key text NOT NULL,
    label text NOT NULL,
    type text DEFAULT 'text'::text NOT NULL,
    options jsonb DEFAULT '[]'::jsonb NOT NULL,
    "position" integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT contact_field_type_check CHECK ((type = ANY (ARRAY['text'::text, 'number'::text, 'date'::text, 'url'::text, 'email'::text, 'phone'::text, 'select'::text, 'boolean'::text])))
);


--
-- Name: counterparty; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.counterparty (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    rfc text,
    entity_type text,
    roles text[] DEFAULT '{}'::text[] NOT NULL,
    dd_status crm.dd_status DEFAULT 'not_started'::crm.dd_status NOT NULL,
    risk_score integer,
    risk_tier text,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    clearance_status text DEFAULT 'none'::text NOT NULL,
    clearance_requested_by text,
    cleared_by text,
    cleared_at timestamp with time zone,
    ebr_grade text,
    dd_level text,
    company_id uuid
);


--
-- Name: covenant_test; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.covenant_test (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    facility_id uuid NOT NULL,
    period date DEFAULT CURRENT_DATE NOT NULL,
    projected_dscr numeric,
    covenant_dscr numeric,
    source text,
    breach boolean DEFAULT false NOT NULL,
    sicr_fired boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: coverage_covenant; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.coverage_covenant (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    facility_id uuid,
    ratio_type text NOT NULL,
    threshold numeric NOT NULL,
    action text NOT NULL,
    active boolean DEFAULT true NOT NULL
);


--
-- Name: coverage_ratio; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.coverage_ratio (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    facility_id uuid NOT NULL,
    as_of date DEFAULT CURRENT_DATE NOT NULL,
    llcr numeric,
    plcr numeric,
    dscr numeric,
    npv_remaining_cfads numeric,
    debt_outstanding numeric,
    dsra_balance numeric,
    status text,
    computed_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: cp_item; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.cp_item (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid NOT NULL,
    sanction_id uuid,
    cp_type text NOT NULL,
    label text NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    auto_source text,
    evidence_path text,
    satisfied_by text,
    satisfied_at timestamp with time zone,
    verified_by text,
    waived_by text,
    waived_reason text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT cp_item_status_check CHECK ((status = ANY (ARRAY['pending'::text, 'satisfied'::text, 'waived'::text])))
);


--
-- Name: credit_memo; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.credit_memo (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid NOT NULL,
    facility_id uuid,
    version integer DEFAULT 1 NOT NULL,
    status text DEFAULT 'draft'::text NOT NULL,
    authority_tier text,
    auto_refer boolean DEFAULT false NOT NULL,
    snapshot jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT credit_memo_status_check CHECK ((status = ANY (ARRAY['draft'::text, 'submitted'::text, 'approved'::text, 'approved_with_conditions'::text, 'declined'::text, 'returned'::text])))
);


--
-- Name: credit_sanction; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.credit_sanction (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    memo_id uuid NOT NULL,
    deal_id uuid NOT NULL,
    decision text NOT NULL,
    tier_matched text,
    locked_terms jsonb DEFAULT '{}'::jsonb NOT NULL,
    sanctioned_by text,
    sanctioned_role text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT credit_sanction_decision_check CHECK ((decision = ANY (ARRAY['approve'::text, 'approve_with_conditions'::text, 'decline'::text])))
);


--
-- Name: dashboard; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.dashboard (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    owner_email text NOT NULL,
    name text NOT NULL,
    shared boolean DEFAULT false NOT NULL,
    widgets jsonb DEFAULT '[]'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: dd_aviso; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.dd_aviso (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    counterparty_id uuid NOT NULL,
    tipo text NOT NULL,
    actividad_vulnerable text,
    folio text,
    status text DEFAULT 'pending'::text NOT NULL,
    reason text,
    evidence_path text,
    due_at timestamp with time zone,
    presented_by text,
    presented_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: dd_check; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.dd_check (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    counterparty_id uuid NOT NULL,
    check_type text NOT NULL,
    status text NOT NULL,
    detail text,
    source text,
    performed_by text,
    performed_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: dd_consent; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.dd_consent (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    counterparty_id uuid NOT NULL,
    kind text NOT NULL,
    subject text,
    scope text,
    evidence_path text,
    granted_by text,
    granted_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone
);


--
-- Name: dd_decision; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.dd_decision (
    id bigint NOT NULL,
    counterparty_id uuid NOT NULL,
    kind text NOT NULL,
    target_ref text,
    decision text,
    reason text,
    actor text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: dd_decision_id_seq; Type: SEQUENCE; Schema: crm; Owner: -
--

ALTER TABLE crm.dd_decision ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME crm.dd_decision_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dd_lpb; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.dd_lpb (
    id bigint NOT NULL,
    rfc text,
    curp text,
    nombre text NOT NULL,
    norm_name text NOT NULL,
    tipo text,
    folio text,
    loaded_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: dd_lpb_id_seq; Type: SEQUENCE; Schema: crm; Owner: -
--

ALTER TABLE crm.dd_lpb ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME crm.dd_lpb_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dd_operation; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.dd_operation (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid,
    counterparty_id uuid,
    facility_id uuid,
    tipo text DEFAULT 'drawdown'::text NOT NULL,
    monto_mxn numeric NOT NULL,
    moneda text DEFAULT 'MXN'::text NOT NULL,
    fecha date NOT NULL,
    instrumento_monetario text,
    uma_multiplo numeric,
    aggregated_6m numeric,
    threshold_flag text DEFAULT 'none'::text NOT NULL,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: dd_ownership_edge; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.dd_ownership_edge (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    counterparty_id uuid NOT NULL,
    owner_node_id uuid NOT NULL,
    owned_node_id uuid NOT NULL,
    pct numeric NOT NULL,
    CONSTRAINT dd_ownership_edge_pct_check CHECK (((pct > (0)::numeric) AND (pct <= (100)::numeric)))
);


--
-- Name: dd_ownership_node; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.dd_ownership_node (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    counterparty_id uuid NOT NULL,
    node_type text NOT NULL,
    name text NOT NULL,
    rfc text,
    is_root boolean DEFAULT false NOT NULL,
    is_pep boolean DEFAULT false NOT NULL,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT dd_ownership_node_node_type_check CHECK ((node_type = ANY (ARRAY['person'::text, 'entity'::text])))
);


--
-- Name: dd_screening_hit; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.dd_screening_hit (
    id bigint NOT NULL,
    counterparty_id uuid NOT NULL,
    subject text NOT NULL,
    subject_name text NOT NULL,
    list_source text,
    matched_name text,
    match_score numeric,
    dataset text,
    disposition text DEFAULT 'pending'::text NOT NULL,
    reviewed_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: dd_screening_hit_id_seq; Type: SEQUENCE; Schema: crm; Owner: -
--

ALTER TABLE crm.dd_screening_hit ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME crm.dd_screening_hit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: dd_ubo; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.dd_ubo (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    counterparty_id uuid NOT NULL,
    name text NOT NULL,
    pct_ownership numeric,
    is_pep boolean DEFAULT false NOT NULL,
    control_type text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    effective_pct numeric,
    is_ubo boolean DEFAULT true NOT NULL,
    node_id uuid,
    rfc text
);


--
-- Name: dd_ubo_document; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.dd_ubo_document (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    counterparty_id uuid NOT NULL,
    ubo_node_id uuid,
    doc_type text NOT NULL,
    storage_path text,
    uploaded_by text,
    verified_by text,
    verified_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT dd_ubo_document_doc_type_check CHECK ((doc_type = ANY (ARRAY['acta_constitutiva'::text, 'estructura_accionaria'::text, 'poder_representante'::text, 'ine_pasaporte'::text, 'comprobante_domicilio'::text])))
);


--
-- Name: deal; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.deal (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    stage crm.deal_stage DEFAULT 'lead'::crm.deal_stage NOT NULL,
    account_id uuid,
    primary_contact_id uuid,
    owner_id uuid,
    rpu text,
    status_note text,
    source text,
    expected_close_date date,
    won_date date,
    close_date date,
    stage_changed_at timestamp with time zone,
    monday_item_id bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    intake_meta jsonb,
    client_summary text,
    client_research jsonb,
    researched_at timestamp with time zone,
    counterparty_id uuid,
    min_dscr numeric,
    project_irr numeric,
    lcoe_mxn_kwh numeric,
    pd numeric,
    lgd numeric,
    ead_mxn numeric,
    el_mxn numeric,
    ecl_stage integer,
    ecl_provision numeric,
    sector text,
    estado text,
    currency text DEFAULT 'MXN'::text,
    lost_reason text,
    archived_at timestamp with time zone,
    company_id uuid
);


--
-- Name: deal_attachment; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.deal_attachment (
    id bigint NOT NULL,
    deal_id uuid NOT NULL,
    storage_path text NOT NULL,
    filename text NOT NULL,
    content_type text,
    size_bytes bigint,
    uploaded_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: deal_attachment_id_seq; Type: SEQUENCE; Schema: crm; Owner: -
--

ALTER TABLE crm.deal_attachment ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME crm.deal_attachment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: deal_comment; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.deal_comment (
    id bigint NOT NULL,
    deal_id uuid NOT NULL,
    author text,
    body text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: deal_comment_id_seq; Type: SEQUENCE; Schema: crm; Owner: -
--

ALTER TABLE crm.deal_comment ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME crm.deal_comment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: deal_event; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.deal_event (
    id bigint NOT NULL,
    deal_id uuid NOT NULL,
    from_stage crm.deal_stage,
    to_stage crm.deal_stage,
    actor text,
    detail text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: deal_event_id_seq; Type: SEQUENCE; Schema: crm; Owner: -
--

ALTER TABLE crm.deal_event ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME crm.deal_event_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: deal_financials; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.deal_financials (
    deal_id uuid NOT NULL,
    assumptions jsonb DEFAULT '{}'::jsonb NOT NULL,
    results jsonb,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: deal_line_item; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.deal_line_item (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid NOT NULL,
    name text,
    item_type crm.line_type DEFAULT 'epc'::crm.line_type NOT NULL,
    kwp numeric,
    usc numeric,
    mxn_kwh numeric,
    periodo integer,
    kwh_annum numeric,
    location text,
    monday_item_id bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: deal_line_item_calc; Type: VIEW; Schema: crm; Owner: -
--

CREATE VIEW crm.deal_line_item_calc WITH (security_invoker='on') AS
 SELECT id,
    deal_id,
    name,
    item_type,
    kwp,
    usc,
    mxn_kwh,
    periodo,
    kwh_annum,
    location,
    monday_item_id,
    created_at,
    ((kwp * usc) * (1000)::numeric) AS epc_value,
        CASE
            WHEN ((kwp IS NOT NULL) AND (kwp <> (0)::numeric)) THEN (kwh_annum / kwp)
            ELSE NULL::numeric
        END AS yield_kwh_per_kwp,
    ((mxn_kwh * kwh_annum) + ((((mxn_kwh * kwh_annum) * ((1)::numeric - 0.01)) * ((1)::numeric + 0.05)) * (((1)::numeric - power((((1)::numeric + 0.05) * ((1)::numeric - 0.004)), ((periodo - 1))::numeric)) / ((1)::numeric - (((1)::numeric + 0.05) * ((1)::numeric - 0.004)))))) AS flujos_contratos,
        CASE
            WHEN (item_type = 'ppa'::crm.line_type) THEN (((mxn_kwh * kwh_annum) / ((1)::numeric + 0.1)) + (((((mxn_kwh * kwh_annum) * ((1)::numeric - 0.01)) * ((1)::numeric + 0.05)) / power(((1)::numeric + 0.12), (2)::numeric)) *
            CASE
                WHEN (abs((((((1)::numeric + 0.05) * ((1)::numeric - 0.004)) / ((1)::numeric + 0.12)) - (1)::numeric)) < 0.000000000001) THEN ((periodo - 1))::numeric
                ELSE (((1)::numeric - power(((((1)::numeric + 0.05) * ((1)::numeric - 0.004)) / ((1)::numeric + 0.12)), ((periodo - 1))::numeric)) / ((1)::numeric - ((((1)::numeric + 0.05) * ((1)::numeric - 0.004)) / ((1)::numeric + 0.12))))
            END))
            WHEN (item_type = 'bess'::crm.line_type) THEN (0)::numeric
            ELSE NULL::numeric
        END AS vpn_contrato
   FROM crm.deal_line_item li;


--
-- Name: deal_rpu; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.deal_rpu (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid NOT NULL,
    rpu text NOT NULL,
    razon_social text,
    validated boolean DEFAULT false NOT NULL,
    validated_at timestamp with time zone,
    collection_request_id bigint,
    coverage jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: deal_stage_history; Type: VIEW; Schema: crm; Owner: -
--

CREATE VIEW crm.deal_stage_history WITH (security_invoker='on') AS
 WITH ev AS (
         SELECT deal_event.deal_id,
            deal_event.to_stage AS stage,
            deal_event.created_at AS entered_at,
            lead(deal_event.created_at) OVER (PARTITION BY deal_event.deal_id ORDER BY deal_event.created_at) AS exited_at
           FROM crm.deal_event
          WHERE (deal_event.to_stage IS NOT NULL)
        ), opening AS (
         SELECT d.id AS deal_id,
            COALESCE(( SELECT e.from_stage
                   FROM crm.deal_event e
                  WHERE (e.deal_id = d.id)
                  ORDER BY e.created_at
                 LIMIT 1), d.stage) AS stage,
            d.created_at AS entered_at,
            ( SELECT min(e.created_at) AS min
                   FROM crm.deal_event e
                  WHERE (e.deal_id = d.id)) AS exited_at
           FROM crm.deal d
        )
 SELECT deal_id,
    stage,
    entered_at,
    exited_at,
    round((EXTRACT(epoch FROM (COALESCE(exited_at, now()) - entered_at)) / 86400.0), 1) AS days_in_stage
   FROM ( SELECT ev.deal_id,
            ev.stage,
            ev.entered_at,
            ev.exited_at
           FROM ev
        UNION ALL
         SELECT opening.deal_id,
            opening.stage,
            opening.entered_at,
            opening.exited_at
           FROM opening) x;


--
-- Name: delegated_authority; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.delegated_authority (
    tier text NOT NULL,
    seq integer NOT NULL,
    min_amount numeric NOT NULL,
    max_amount numeric,
    label text NOT NULL,
    requires_approver boolean DEFAULT true NOT NULL,
    requires_quorum integer DEFAULT 1 NOT NULL
);


--
-- Name: dlp_clock; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.dlp_clock (
    project_id uuid NOT NULL,
    cod_date date,
    dlp_months integer DEFAULT 24 NOT NULL,
    expires_at date,
    final_retention_released boolean DEFAULT false NOT NULL,
    released_by text,
    released_at timestamp with time zone
);


--
-- Name: dlp_defect; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.dlp_defect (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    description text,
    severity text,
    status text DEFAULT 'open'::text NOT NULL,
    raised_at timestamp with time zone DEFAULT now() NOT NULL,
    closed_by text,
    closed_at timestamp with time zone,
    CONSTRAINT dlp_defect_status_check CHECK ((status = ANY (ARRAY['open'::text, 'remediating'::text, 'closed'::text])))
);


--
-- Name: ebr_factor; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.ebr_factor (
    code text NOT NULL,
    label text NOT NULL,
    weight numeric NOT NULL,
    seq integer NOT NULL
);


--
-- Name: ebr_rating; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.ebr_rating (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    counterparty_id uuid NOT NULL,
    score numeric NOT NULL,
    grade text NOT NULL,
    dd_level text NOT NULL,
    factor_scores jsonb DEFAULT '{}'::jsonb NOT NULL,
    methodology_ver integer DEFAULT 1 NOT NULL,
    computed_by text,
    computed_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: ecl_run; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.ecl_run (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    run_date date DEFAULT CURRENT_DATE NOT NULL,
    set_id uuid,
    portfolio_weighted_ecl numeric,
    portfolio_base_ecl numeric,
    correlated_downside_ecl numeric,
    diversified_sum_ecl numeric,
    tail_add_on numeric,
    n_facilities integer,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: edd_item; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.edd_item (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    counterparty_id uuid NOT NULL,
    item_type text NOT NULL,
    label text NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    evidence_path text,
    satisfied_by text,
    verified_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT edd_item_status_check CHECK ((status = ANY (ARRAY['pending'::text, 'satisfied'::text, 'waived'::text])))
);


--
-- Name: efos_69b; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.efos_69b (
    rfc text NOT NULL,
    nombre text,
    situacion text,
    loaded_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: email_account; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.email_account (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    owner_email text NOT NULL,
    imap_host text,
    imap_port integer DEFAULT 993,
    smtp_host text,
    smtp_port integer DEFAULT 465,
    username text,
    secret_ref text,
    from_address text,
    display_name text,
    last_uid_seen bigint DEFAULT 0,
    sync_state text,
    active boolean DEFAULT true NOT NULL,
    last_synced_at timestamp with time zone,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: email_template; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.email_template (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    owner_email text,
    name text NOT NULL,
    subject text,
    body_html text,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: email_tracking; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.email_tracking (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    outbox_id uuid,
    open_token uuid DEFAULT gen_random_uuid() NOT NULL,
    opened_at timestamp with time zone,
    clicks jsonb DEFAULT '[]'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: expense; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.expense (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid,
    concept text,
    amount_mxn numeric,
    incurred_date date,
    category text,
    monday_item_id bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: facility; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.facility (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid NOT NULL,
    counterparty_id uuid,
    currency text DEFAULT 'MXN'::text NOT NULL,
    principal_mxn numeric DEFAULT 0 NOT NULL,
    annual_rate numeric DEFAULT 0 NOT NULL,
    tenor_months integer DEFAULT 60 NOT NULL,
    grace_months integer DEFAULT 0 NOT NULL,
    dscr_target numeric,
    disburse_date date,
    status text DEFAULT 'active'::text NOT NULL,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: facility_base_case; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.facility_base_case (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    facility_id uuid NOT NULL,
    version integer DEFAULT 1 NOT NULL,
    base_model jsonb NOT NULL,
    integrity_hash text,
    frozen_by text,
    approved_by text,
    frozen_at timestamp with time zone DEFAULT now() NOT NULL,
    active boolean DEFAULT true NOT NULL
);


--
-- Name: facility_scenario_ecl; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.facility_scenario_ecl (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    run_id uuid NOT NULL,
    facility_id uuid,
    scenario_id uuid,
    scenario_name text,
    pd_scenario numeric,
    lgd_scenario numeric,
    ead numeric,
    stage_scenario integer,
    ecl_scenario numeric
);


--
-- Name: facility_schedule; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.facility_schedule (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    facility_id uuid NOT NULL,
    period_no integer NOT NULL,
    due_date date NOT NULL,
    opening_balance numeric NOT NULL,
    principal_due numeric NOT NULL,
    interest_due numeric NOT NULL,
    total_due numeric NOT NULL,
    closing_balance numeric NOT NULL
);


--
-- Name: field_capture; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.field_capture (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    client_uuid uuid NOT NULL,
    rep_email text,
    deal_id uuid,
    kind text NOT NULL,
    payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    photo_path text,
    captured_at timestamp with time zone,
    status text DEFAULT 'synced'::text NOT NULL,
    synced_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT field_capture_kind_check CHECK ((kind = ANY (ARRAY['visit'::text, 'cfe_bill'::text, 'stage_update'::text, 'note'::text])))
);


--
-- Name: forbearance_event; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.forbearance_event (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    facility_id uuid NOT NULL,
    kind text DEFAULT 'restructure'::text NOT NULL,
    classification text DEFAULT 'non_performing'::text NOT NULL,
    substantial boolean DEFAULT false NOT NULL,
    gross_before numeric,
    gross_after numeric,
    mod_gain_loss numeric,
    original_eir numeric,
    probation_until date,
    granted_by text,
    approved_by text,
    granted_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT fb_four_eyes CHECK (((approved_by IS NULL) OR (approved_by <> granted_by))),
    CONSTRAINT forbearance_event_classification_check CHECK ((classification = ANY (ARRAY['performing'::text, 'non_performing'::text])))
);


--
-- Name: generation_actual; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.generation_actual (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    period_start date NOT NULL,
    period_end date NOT NULL,
    year_no integer,
    kwh_actual numeric NOT NULL,
    source text DEFAULT 'cfe_bill'::text NOT NULL,
    evidence_url text,
    captured_by text,
    verified_by text,
    verified_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: generation_baseline; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.generation_baseline (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    year_no integer NOT NULL,
    expected_kwh numeric NOT NULL,
    degradation_pct numeric DEFAULT 0.005 NOT NULL,
    source text DEFAULT 'p50_frozen'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: goods_receipt; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.goods_receipt (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    po_id uuid NOT NULL,
    received_pct numeric DEFAULT 0 NOT NULL,
    gr_date date DEFAULT CURRENT_DATE NOT NULL,
    note text,
    received_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: huddle_run; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.huddle_run (
    id bigint NOT NULL,
    doc_id text NOT NULL,
    doc_title text,
    doc_modified_at timestamp with time zone,
    meeting_date date,
    model text,
    items_extracted integer DEFAULT 0 NOT NULL,
    todos_created integer DEFAULT 0 NOT NULL,
    deals_created integer DEFAULT 0 NOT NULL,
    comments_created integer DEFAULT 0 NOT NULL,
    raw_extract jsonb,
    status text DEFAULT 'ok'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: huddle_run_id_seq; Type: SEQUENCE; Schema: crm; Owner: -
--

ALTER TABLE crm.huddle_run ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME crm.huddle_run_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: inspection; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.inspection (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    itp_item_id uuid NOT NULL,
    result text NOT NULL,
    punch_items jsonb DEFAULT '[]'::jsonb NOT NULL,
    inspector text,
    evidence_url text,
    created_by text,
    approved_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT inspection_result_check CHECK ((result = ANY (ARRAY['pass'::text, 'fail'::text, 'conditional'::text])))
);


--
-- Name: invoice; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.invoice (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    quote_id uuid,
    deal_id uuid,
    number text,
    amount_mxn numeric,
    status text,
    issued_date date,
    paid_date date,
    monday_item_id bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: itp_item; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.itp_item (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    milestone_id uuid,
    discipline text,
    description text NOT NULL,
    weight_pct numeric DEFAULT 0 NOT NULL,
    hold_point boolean DEFAULT false NOT NULL,
    self_pct numeric DEFAULT 0 NOT NULL,
    verified_pct numeric DEFAULT 0 NOT NULL,
    status crm.itp_status DEFAULT 'pending'::crm.itp_status NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    reported_by text
);


--
-- Name: ld_accrual; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.ld_accrual (
    project_id uuid NOT NULL,
    cod_target date,
    cod_actual date,
    days_late integer DEFAULT 0 NOT NULL,
    ld_rate_per_day numeric DEFAULT 0 NOT NULL,
    ld_cap_pct numeric DEFAULT 0.10 NOT NULL,
    accrued_amount numeric DEFAULT 0 NOT NULL,
    capped boolean DEFAULT false NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: lgd_realization; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.lgd_realization (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    facility_id uuid NOT NULL,
    defaulted_ead numeric,
    recovered numeric,
    realized_lgd numeric,
    sector text,
    closed_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: limit_breach; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.limit_breach (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid,
    dimension text,
    bucket_key text,
    current_util numeric,
    post_deal_util numeric,
    limit_value numeric,
    state text,
    hard boolean,
    computed_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT limit_breach_state_check CHECK ((state = ANY (ARRAY['ok'::text, 'warning'::text, 'breach'::text])))
);


--
-- Name: macro_scenario; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.macro_scenario (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    set_id uuid NOT NULL,
    name text NOT NULL,
    probability numeric NOT NULL,
    fx_mxn_usd numeric DEFAULT 18 NOT NULL,
    cfe_tariff_delta_pct numeric DEFAULT 0 NOT NULL,
    domestic_rate_delta_bps numeric DEFAULT 0 NOT NULL,
    generation_factor numeric DEFAULT 1.0 NOT NULL,
    is_downside boolean DEFAULT false NOT NULL,
    sort integer DEFAULT 0 NOT NULL,
    CONSTRAINT macro_scenario_probability_check CHECK (((probability >= (0)::numeric) AND (probability <= (1)::numeric)))
);


--
-- Name: macro_scenario_set; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.macro_scenario_set (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    version integer DEFAULT 1 NOT NULL,
    label text NOT NULL,
    status text DEFAULT 'draft'::text NOT NULL,
    created_by text,
    approved_by text,
    approved_at timestamp with time zone,
    effective_date date,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT macro_scenario_set_status_check CHECK ((status = ANY (ARRAY['draft'::text, 'approved'::text, 'archived'::text]))),
    CONSTRAINT mss_four_eyes CHECK (((approved_by IS NULL) OR (approved_by <> created_by)))
);


--
-- Name: notification; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.notification (
    id bigint NOT NULL,
    recipient_email text NOT NULL,
    kind text NOT NULL,
    title text NOT NULL,
    body text,
    entity_type text,
    entity_id uuid,
    deal_id uuid,
    read boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    pushed_at timestamp with time zone,
    url text,
    action_type text,
    action_state text DEFAULT 'none'::text NOT NULL,
    route text,
    due_at timestamp with time zone,
    priority integer DEFAULT 0 NOT NULL,
    acted_by text,
    acted_at timestamp with time zone,
    dedupe_key text,
    CONSTRAINT notification_action_state_check CHECK ((action_state = ANY (ARRAY['none'::text, 'pending'::text, 'acted'::text, 'dismissed'::text])))
);


--
-- Name: notification_id_seq; Type: SEQUENCE; Schema: crm; Owner: -
--

ALTER TABLE crm.notification ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME crm.notification_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: operacion_relevante; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.operacion_relevante (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    counterparty_id uuid,
    period text,
    instrument text,
    amount_mxn numeric,
    uma_multiple numeric,
    trigger_event_id uuid,
    due_at date,
    status text DEFAULT 'staged'::text NOT NULL,
    xml_artifact text,
    filed_by text,
    dedupe_key text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT operacion_relevante_status_check CHECK ((status = ANY (ARRAY['staged'::text, 'prepared'::text, 'filed'::text])))
);


--
-- Name: ops_report; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.ops_report (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid,
    title text NOT NULL,
    status text,
    notes text,
    monday_item_id bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: pd_rating; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.pd_rating (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid NOT NULL,
    facility_id uuid,
    grade text NOT NULL,
    pit_pd numeric NOT NULL,
    composite numeric,
    factor_scores jsonb DEFAULT '{}'::jsonb NOT NULL,
    methodology_ver integer DEFAULT 1 NOT NULL,
    computed_by text,
    computed_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: pd_scorecard_factor; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.pd_scorecard_factor (
    code text NOT NULL,
    label text NOT NULL,
    weight numeric NOT NULL,
    seq integer DEFAULT 0 NOT NULL
);


--
-- Name: pd_term_structure; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.pd_term_structure (
    rating_id uuid NOT NULL,
    year integer NOT NULL,
    marginal_pd numeric NOT NULL,
    cumulative_pd numeric NOT NULL
);


--
-- Name: performance_backcharge; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.performance_backcharge (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    cumulative_shortfall_kwh numeric,
    shortfall_value_mxn numeric,
    tariff_basis numeric,
    status text DEFAULT 'draft'::text NOT NULL,
    created_by text,
    approved_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT pbc_four_eyes CHECK (((approved_by IS NULL) OR (approved_by <> created_by))),
    CONSTRAINT performance_backcharge_status_check CHECK ((status = ANY (ARRAY['draft'::text, 'asserted'::text, 'netted'::text, 'closed'::text])))
);


--
-- Name: po_invoice; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.po_invoice (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    po_id uuid NOT NULL,
    invoice_folio text,
    invoice_amount_fx numeric NOT NULL,
    invoice_date date DEFAULT CURRENT_DATE NOT NULL,
    three_way_matched boolean DEFAULT false NOT NULL,
    approved_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: progress_claim; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.progress_claim (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    period text,
    claimed_pct numeric,
    certified_pct numeric,
    retention_pct numeric DEFAULT 0.10 NOT NULL,
    gross_earned numeric,
    retention_withheld numeric,
    net_certified numeric,
    status text DEFAULT 'draft'::text NOT NULL,
    approved_by text,
    certified_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT progress_claim_status_check CHECK ((status = ANY (ARRAY['draft'::text, 'inspection_gate'::text, 'certified'::text, 'rejected'::text])))
);


--
-- Name: project; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.project (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid,
    counterparty_id uuid,
    name text,
    status text DEFAULT 'in_delivery'::text NOT NULL,
    contract_value_mxn numeric,
    kwp numeric,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: project_cost; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.project_cost (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    cost_code text NOT NULL,
    bac numeric DEFAULT 0 NOT NULL,
    committed numeric DEFAULT 0 NOT NULL,
    actual numeric DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: project_milestone; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.project_milestone (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    seq integer NOT NULL,
    name text NOT NULL,
    pct_value numeric DEFAULT 0 NOT NULL,
    planned_date date,
    actual_date date,
    status text DEFAULT 'pending'::text NOT NULL,
    updated_by text,
    certified_by text,
    certified_at timestamp with time zone,
    certificate_path text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: proposal; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.proposal (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid NOT NULL,
    version integer DEFAULT 1 NOT NULL,
    title text,
    currency text DEFAULT 'MXN'::text NOT NULL,
    status crm.proposal_status DEFAULT 'draft'::crm.proposal_status NOT NULL,
    public_token text DEFAULT encode(extensions.gen_random_bytes(18), 'hex'::text) NOT NULL,
    snapshot jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    sent_at timestamp with time zone,
    viewed_at timestamp with time zone,
    signed_at timestamp with time zone,
    expires_at timestamp with time zone
);


--
-- Name: proposal_event; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.proposal_event (
    id bigint NOT NULL,
    proposal_id uuid NOT NULL,
    type text NOT NULL,
    at timestamp with time zone DEFAULT now() NOT NULL,
    meta jsonb
);


--
-- Name: proposal_event_id_seq; Type: SEQUENCE; Schema: crm; Owner: -
--

ALTER TABLE crm.proposal_event ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME crm.proposal_event_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: proposal_line; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.proposal_line (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    proposal_id uuid NOT NULL,
    section text NOT NULL,
    label text NOT NULL,
    value_numeric numeric,
    unit text,
    value_text text,
    sort integer DEFAULT 0 NOT NULL
);


--
-- Name: proposal_signature; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.proposal_signature (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    proposal_id uuid NOT NULL,
    signer_name text,
    signer_email text,
    signed_at timestamp with time zone DEFAULT now() NOT NULL,
    ip text,
    user_agent text,
    signature_image text,
    consent_text text,
    audit_hash text
);


--
-- Name: purchase_order; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.purchase_order (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    cost_id uuid,
    category text NOT NULL,
    supplier_name text NOT NULL,
    supplier_rfc text,
    currency text DEFAULT 'USD'::text NOT NULL,
    contract_value_fx numeric NOT NULL,
    fx_rate_underwritten numeric DEFAULT 1 NOT NULL,
    fx_rate_po numeric DEFAULT 1 NOT NULL,
    hedged boolean DEFAULT false NOT NULL,
    mxn_committed numeric GENERATED ALWAYS AS ((contract_value_fx * fx_rate_po)) STORED,
    need_by_date date,
    expected_delivery_date date,
    retainage_pct numeric DEFAULT 0 NOT NULL,
    status crm.po_status DEFAULT 'pending_approval'::crm.po_status NOT NULL,
    created_by text,
    approved_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT po_four_eyes CHECK (((approved_by IS NULL) OR (approved_by <> created_by)))
);


--
-- Name: push_subscription; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.push_subscription (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    owner_email text NOT NULL,
    endpoint text NOT NULL,
    p256dh text,
    auth_key text,
    user_agent text,
    active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    last_seen_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: quote; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.quote (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid,
    number text,
    amount_mxn numeric,
    status text,
    issued_date date,
    monday_item_id bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: raroc_assessment; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.raroc_assessment (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid NOT NULL,
    ead numeric,
    pd numeric,
    lgd numeric,
    expected_loss numeric,
    el_rate numeric,
    capital_charge_rate numeric,
    cost_of_funds_rate numeric,
    opex_rate numeric,
    required_all_in_rate numeric,
    offered_rate numeric,
    required_spread_bps numeric,
    offered_spread_bps numeric,
    raroc_pct numeric,
    hurdle_pct numeric,
    verdict text,
    config_version text,
    inputs jsonb,
    computed_by text,
    computed_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT raroc_assessment_verdict_check CHECK ((verdict = ANY (ARRAY['pass'::text, 'fail'::text])))
);


--
-- Name: recovery_posting; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.recovery_posting (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    facility_id uuid NOT NULL,
    amount numeric NOT NULL,
    source text,
    posted_by text,
    posted_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: reforecast; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.reforecast (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    facility_id uuid NOT NULL,
    as_of date DEFAULT CURRENT_DATE NOT NULL,
    revised_cfads jsonb NOT NULL,
    note text,
    created_by text,
    approved_by text,
    approved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: repayment; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.repayment (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    facility_id uuid NOT NULL,
    received_at date NOT NULL,
    amount_mxn numeric NOT NULL,
    method text,
    allocated_interest numeric DEFAULT 0 NOT NULL,
    allocated_principal numeric DEFAULT 0 NOT NULL,
    note text,
    posted_by text,
    posted_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: retention_ledger; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.retention_ledger (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    progress_claim_id uuid,
    withheld numeric DEFAULT 0 NOT NULL,
    released numeric DEFAULT 0 NOT NULL,
    release_reason text,
    released_by text,
    released_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: roi_artifact; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.roi_artifact (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    case_id uuid NOT NULL,
    roi_xml text,
    integrity_hash text,
    generated_by text,
    generated_at timestamp with time zone,
    presenter text,
    acuse_folio text,
    presented_at timestamp with time zone,
    status text DEFAULT 'draft'::text NOT NULL,
    CONSTRAINT roi_artifact_status_check CHECK ((status = ANY (ARRAY['draft'::text, 'presentado'::text])))
);


--
-- Name: sales_target; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.sales_target (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    scope text DEFAULT 'rep'::text NOT NULL,
    owner_id uuid,
    team_key text,
    period_type text DEFAULT 'quarter'::text NOT NULL,
    period_start date NOT NULL,
    period_end date NOT NULL,
    target_vpn_weighted numeric DEFAULT 0 NOT NULL,
    target_count integer,
    version integer DEFAULT 1 NOT NULL,
    status text DEFAULT 'draft'::text NOT NULL,
    created_by text,
    approved_by text,
    approved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT sales_target_period_type_check CHECK ((period_type = ANY (ARRAY['month'::text, 'quarter'::text, 'year'::text]))),
    CONSTRAINT sales_target_scope_check CHECK ((scope = ANY (ARRAY['rep'::text, 'team'::text]))),
    CONSTRAINT sales_target_status_check CHECK ((status = ANY (ARRAY['draft'::text, 'approved'::text]))),
    CONSTRAINT st_four_eyes CHECK (((approved_by IS NULL) OR (approved_by <> created_by)))
);


--
-- Name: sanction_override; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.sanction_override (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid NOT NULL,
    kind text NOT NULL,
    reason text NOT NULL,
    overridden_by text,
    approver_role text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT sanction_override_kind_check CHECK ((kind = ANY (ARRAY['raroc'::text, 'concentration'::text, 'both'::text])))
);


--
-- Name: sanctions_entry; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.sanctions_entry (
    id bigint NOT NULL,
    source text NOT NULL,
    dataset text,
    schema text,
    target_name text NOT NULL,
    alt_name text NOT NULL,
    norm_name text NOT NULL,
    countries text
);


--
-- Name: sanctions_entry_id_seq; Type: SEQUENCE; Schema: crm; Owner: -
--

ALTER TABLE crm.sanctions_entry ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME crm.sanctions_entry_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: saved_view; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.saved_view (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    owner_id uuid,
    owner_email text,
    name text NOT NULL,
    object text DEFAULT 'pipeline'::text NOT NULL,
    config jsonb DEFAULT '{}'::jsonb NOT NULL,
    is_shared boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: schedule_activity; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.schedule_activity (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    code text,
    name text NOT NULL,
    activity_type text DEFAULT 'construction'::text NOT NULL,
    baseline_duration_days numeric DEFAULT 30 NOT NULL,
    pct_complete numeric DEFAULT 0 NOT NULL,
    is_terminal boolean DEFAULT false NOT NULL,
    linked_itp_item_id uuid,
    linked_po_id uuid,
    seq integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: schedule_baseline; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.schedule_baseline (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    version integer DEFAULT 1 NOT NULL,
    baseline_cod date,
    status text DEFAULT 'draft'::text NOT NULL,
    created_by text,
    approved_by text,
    approved_at timestamp with time zone,
    CONSTRAINT sb_four_eyes CHECK (((approved_by IS NULL) OR (approved_by <> created_by)))
);


--
-- Name: schedule_dependency; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.schedule_dependency (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    predecessor_id uuid NOT NULL,
    successor_id uuid NOT NULL,
    dep_type text DEFAULT 'FS'::text NOT NULL,
    lag_days integer DEFAULT 0 NOT NULL
);


--
-- Name: schedule_forecast; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.schedule_forecast (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    run_at timestamp with time zone DEFAULT now() NOT NULL,
    predicted_cod date,
    baseline_cod date,
    target_cod date,
    slip_days integer,
    critical_path jsonb,
    spi_t numeric,
    forecast_ld_mxn numeric,
    approved_eot_days integer,
    net_forecast_ld_mxn numeric
);


--
-- Name: screening_list_version; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.screening_list_version (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    list_name text NOT NULL,
    version_tag text NOT NULL,
    source_published_date date,
    imported_at timestamp with time zone DEFAULT now() NOT NULL,
    row_count integer,
    sha text,
    notes text,
    CONSTRAINT screening_list_version_list_name_check CHECK ((list_name = ANY (ARRAY['opensanctions'::text, 'sat_69b_efos'::text, 'uif_lpb'::text, 'rfc'::text])))
);


--
-- Name: screening_provenance; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.screening_provenance (
    id bigint NOT NULL,
    counterparty_id uuid,
    entity_ref text,
    list_version_id uuid,
    screened_at timestamp with time zone DEFAULT now() NOT NULL,
    result text,
    disposition_ref text
);


--
-- Name: screening_provenance_id_seq; Type: SEQUENCE; Schema: crm; Owner: -
--

ALTER TABLE crm.screening_provenance ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME crm.screening_provenance_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: sequence; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.sequence (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    enabled boolean DEFAULT true NOT NULL,
    exit_on_reply boolean DEFAULT true NOT NULL,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: sequence_enrollment; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.sequence_enrollment (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    sequence_id uuid NOT NULL,
    deal_id uuid,
    contact_id uuid,
    current_step integer DEFAULT 0 NOT NULL,
    status text DEFAULT 'active'::text NOT NULL,
    next_action_at timestamp with time zone,
    enrolled_at timestamp with time zone DEFAULT now() NOT NULL,
    exit_reason text
);


--
-- Name: sequence_step; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.sequence_step (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    sequence_id uuid NOT NULL,
    step_no integer NOT NULL,
    delay_hours integer DEFAULT 24 NOT NULL,
    channel text DEFAULT 'whatsapp'::text NOT NULL,
    template text NOT NULL
);


--
-- Name: stage_probability; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.stage_probability (
    stage crm.deal_stage NOT NULL,
    win_prob numeric NOT NULL,
    is_commit boolean DEFAULT false NOT NULL,
    is_won boolean DEFAULT false NOT NULL,
    is_lost boolean DEFAULT false NOT NULL,
    max_days_in_stage integer,
    sort_order integer DEFAULT 0 NOT NULL,
    updated_by text,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT stage_probability_win_prob_check CHECK (((win_prob >= (0)::numeric) AND (win_prob <= (1)::numeric)))
);


--
-- Name: sub_back_charge; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.sub_back_charge (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    subcontract_id uuid NOT NULL,
    description text,
    amount numeric DEFAULT 0 NOT NULL,
    kind text DEFAULT 'back_charge'::text NOT NULL,
    status text DEFAULT 'pending'::text NOT NULL,
    created_by text,
    approved_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: sub_payment_claim; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.sub_payment_claim (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    subcontract_id uuid NOT NULL,
    claim_no integer DEFAULT 1 NOT NULL,
    period text,
    verified_pct numeric,
    gross_certified numeric,
    retention_withheld numeric,
    back_charges numeric,
    net_certified numeric,
    status text DEFAULT 'certified'::text NOT NULL,
    submitted_by text,
    certified_by text,
    certified_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: sub_retention_ledger; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.sub_retention_ledger (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    subcontract_id uuid NOT NULL,
    claim_id uuid,
    withheld numeric DEFAULT 0 NOT NULL,
    released numeric DEFAULT 0 NOT NULL,
    release_reason text,
    released_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: subcontract; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.subcontract (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    project_id uuid NOT NULL,
    cost_id uuid,
    itp_item_id uuid,
    vendor text NOT NULL,
    scope text,
    contract_value_mxn numeric DEFAULT 0 NOT NULL,
    retention_pct numeric DEFAULT 0.07 NOT NULL,
    status text DEFAULT 'pending_approval'::text NOT NULL,
    created_by text,
    approved_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT sub_four_eyes CHECK (((approved_by IS NULL) OR (approved_by <> created_by))),
    CONSTRAINT subcontract_status_check CHECK ((status = ANY (ARRAY['draft'::text, 'pending_approval'::text, 'issued'::text, 'active'::text, 'closed'::text, 'cancelled'::text])))
);


--
-- Name: sync_state; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.sync_state (
    source text NOT NULL,
    watermark text,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: task; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.task (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    deal_id uuid,
    contact_id uuid,
    assignee text NOT NULL,
    title text NOT NULL,
    detail text,
    due_at timestamp with time zone NOT NULL,
    priority smallint DEFAULT 2 NOT NULL,
    is_next_step boolean DEFAULT false NOT NULL,
    status text DEFAULT 'open'::text NOT NULL,
    completed_at timestamp with time zone,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT task_status CHECK ((status = ANY (ARRAY['open'::text, 'done'::text, 'cancelled'::text])))
);


--
-- Name: todo; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.todo (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    title text NOT NULL,
    detail text,
    status crm.todo_status DEFAULT 'pipeline'::crm.todo_status NOT NULL,
    owner_id uuid,
    deal_id uuid,
    source text DEFAULT 'huddle'::text NOT NULL,
    source_doc_id text,
    source_line text,
    is_blocked boolean DEFAULT false NOT NULL,
    blocked_reason text,
    due_date date,
    "position" integer DEFAULT 0 NOT NULL,
    created_by text DEFAULT 'huddle-agent'::text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: todo_board; Type: VIEW; Schema: crm; Owner: -
--

CREATE VIEW crm.todo_board AS
 SELECT t.id,
    t.title,
    t.detail,
    t.status,
    t."position",
    t.owner_id,
    u.name AS owner_name,
    u.email AS owner_email,
    t.deal_id,
    d.name AS deal_name,
    d.stage AS deal_stage,
    t.is_blocked,
    t.blocked_reason,
    t.due_date,
    t.source,
    t.source_doc_id,
    t.source_line,
    t.created_by,
    t.created_at,
    t.updated_at
   FROM ((crm.todo t
     LEFT JOIN crm.app_user u ON ((u.id = t.owner_id)))
     LEFT JOIN crm.deal d ON ((d.id = t.deal_id)));


--
-- Name: todo_subtask; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.todo_subtask (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    todo_id uuid NOT NULL,
    title text NOT NULL,
    done boolean DEFAULT false NOT NULL,
    "position" integer DEFAULT 0 NOT NULL,
    created_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: training_completion; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.training_completion (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    app_user_id uuid NOT NULL,
    topic text NOT NULL,
    completed_on date NOT NULL,
    expires_on date,
    score numeric,
    evidence_ref text,
    recorded_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: training_course; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.training_course (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    topic text NOT NULL,
    name text NOT NULL,
    valid_months integer DEFAULT 12 NOT NULL,
    mandatory_for text[] DEFAULT '{}'::text[]
);


--
-- Name: transaction_profile; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.transaction_profile (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    counterparty_id uuid NOT NULL,
    version integer DEFAULT 1 NOT NULL,
    effective_from date DEFAULT CURRENT_DATE NOT NULL,
    expected_op_types text[] DEFAULT '{}'::text[] NOT NULL,
    expected_freq_6mo integer,
    expected_amount_uma_max numeric,
    declared_source_of_funds text,
    declared_source_of_wealth text,
    ebr_grade_snapshot text,
    created_by text,
    verified_by text,
    verified_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT tp_four_eyes CHECK (((verified_by IS NULL) OR (verified_by <> created_by)))
);


--
-- Name: txn_monitor_event; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.txn_monitor_event (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    counterparty_id uuid,
    event_type text NOT NULL,
    window_start date,
    window_end date,
    aggregate_amount_mxn numeric,
    uma_multiple numeric,
    detail text,
    severity integer DEFAULT 1 NOT NULL,
    status text DEFAULT 'open'::text NOT NULL,
    linked_str_case_id uuid,
    dedupe_key text,
    reviewed_by text,
    reviewed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT txn_monitor_event_event_type_check CHECK ((event_type = ANY (ARRAY['operacion_relevante'::text, 'fraccionamiento'::text, 'profile_deviation'::text]))),
    CONSTRAINT txn_monitor_event_status_check CHECK ((status = ANY (ARRAY['open'::text, 'reviewed'::text, 'dismissed'::text, 'escalated'::text])))
);


--
-- Name: txn_profile; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.txn_profile (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    counterparty_id uuid NOT NULL,
    expected_monthly_volume_mxn numeric,
    expected_txn_count integer,
    expected_max_single_mxn numeric,
    currency text DEFAULT 'MXN'::text,
    source_of_funds text,
    business_rationale text,
    status text DEFAULT 'draft'::text NOT NULL,
    version integer DEFAULT 1 NOT NULL,
    captured_by text,
    approved_by text,
    approved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT txn_profile_status_check CHECK ((status = ANY (ARRAY['draft'::text, 'approved'::text, 'superseded'::text]))),
    CONSTRAINT txnp_four_eyes CHECK (((approved_by IS NULL) OR (approved_by <> captured_by)))
);


--
-- Name: uma_config; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.uma_config (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    version text NOT NULL,
    or_threshold_uma numeric DEFAULT 1605 NOT NULL,
    structuring_window_days integer DEFAULT 30 NOT NULL,
    structuring_uma_floor numeric DEFAULT 500 NOT NULL,
    deviation_ratio_trigger numeric DEFAULT 3.0 NOT NULL,
    active boolean DEFAULT true NOT NULL,
    approved_by text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: workout_case; Type: TABLE; Schema: crm; Owner: -
--

CREATE TABLE crm.workout_case (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    facility_id uuid NOT NULL,
    deal_id uuid,
    status text DEFAULT 'watchlist'::text NOT NULL,
    opened_by text,
    opened_at timestamp with time zone DEFAULT now() NOT NULL,
    note text,
    CONSTRAINT workout_case_status_check CHECK ((status = ANY (ARRAY['watchlist'::text, 'forbearance'::text, 'restructured'::text, 'recovery'::text, 'cured'::text, 'written_off'::text])))
);


--
-- Name: account account_monday_item_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.account
    ADD CONSTRAINT account_monday_item_id_key UNIQUE (monday_item_id);


--
-- Name: account account_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.account
    ADD CONSTRAINT account_pkey PRIMARY KEY (id);


--
-- Name: activity activity_external_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.activity
    ADD CONSTRAINT activity_external_id_key UNIQUE (external_id);


--
-- Name: activity activity_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.activity
    ADD CONSTRAINT activity_pkey PRIMARY KEY (id);


--
-- Name: ai_draft ai_draft_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.ai_draft
    ADD CONSTRAINT ai_draft_pkey PRIMARY KEY (id);


--
-- Name: ai_prompt_log ai_prompt_log_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.ai_prompt_log
    ADD CONSTRAINT ai_prompt_log_pkey PRIMARY KEY (id);


--
-- Name: aml_alert aml_alert_counterparty_id_dedup_key_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_alert
    ADD CONSTRAINT aml_alert_counterparty_id_dedup_key_key UNIQUE (counterparty_id, dedup_key);


--
-- Name: aml_alert aml_alert_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_alert
    ADD CONSTRAINT aml_alert_pkey PRIMARY KEY (id);


--
-- Name: aml_audit_item aml_audit_item_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_audit_item
    ADD CONSTRAINT aml_audit_item_pkey PRIMARY KEY (id);


--
-- Name: aml_audit aml_audit_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_audit
    ADD CONSTRAINT aml_audit_pkey PRIMARY KEY (id);


--
-- Name: aml_case aml_case_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_case
    ADD CONSTRAINT aml_case_pkey PRIMARY KEY (id);


--
-- Name: aml_control_clause aml_control_clause_control_id_manual_version_clause_ref_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_control_clause
    ADD CONSTRAINT aml_control_clause_control_id_manual_version_clause_ref_key UNIQUE (control_id, manual_version, clause_ref);


--
-- Name: aml_control_clause aml_control_clause_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_control_clause
    ADD CONSTRAINT aml_control_clause_pkey PRIMARY KEY (id);


--
-- Name: aml_control aml_control_code_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_control
    ADD CONSTRAINT aml_control_code_key UNIQUE (code);


--
-- Name: aml_control aml_control_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_control
    ADD CONSTRAINT aml_control_pkey PRIMARY KEY (id);


--
-- Name: aml_designation aml_designation_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_designation
    ADD CONSTRAINT aml_designation_pkey PRIMARY KEY (id);


--
-- Name: aml_dictamen aml_dictamen_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_dictamen
    ADD CONSTRAINT aml_dictamen_pkey PRIMARY KEY (id);


--
-- Name: aml_manual aml_manual_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_manual
    ADD CONSTRAINT aml_manual_pkey PRIMARY KEY (id);


--
-- Name: aml_rule aml_rule_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_rule
    ADD CONSTRAINT aml_rule_pkey PRIMARY KEY (code);


--
-- Name: app_user app_user_auth_uid_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.app_user
    ADD CONSTRAINT app_user_auth_uid_key UNIQUE (auth_uid);


--
-- Name: app_user app_user_email_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.app_user
    ADD CONSTRAINT app_user_email_key UNIQUE (email);


--
-- Name: app_user app_user_monday_user_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.app_user
    ADD CONSTRAINT app_user_monday_user_id_key UNIQUE (monday_user_id);


--
-- Name: app_user app_user_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.app_user
    ADD CONSTRAINT app_user_pkey PRIMARY KEY (id);


--
-- Name: automation_action automation_action_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.automation_action
    ADD CONSTRAINT automation_action_pkey PRIMARY KEY (id);


--
-- Name: automation_event automation_event_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.automation_event
    ADD CONSTRAINT automation_event_pkey PRIMARY KEY (id);


--
-- Name: automation_recipe automation_recipe_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.automation_recipe
    ADD CONSTRAINT automation_recipe_pkey PRIMARY KEY (id);


--
-- Name: automation_run automation_run_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.automation_run
    ADD CONSTRAINT automation_run_pkey PRIMARY KEY (id);


--
-- Name: automation_run automation_run_recipe_id_event_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.automation_run
    ADD CONSTRAINT automation_run_recipe_id_event_id_key UNIQUE (recipe_id, event_id);


--
-- Name: aviso_batch aviso_batch_periodo_anio_periodo_mes_tipo_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aviso_batch
    ADD CONSTRAINT aviso_batch_periodo_anio_periodo_mes_tipo_key UNIQUE (periodo_anio, periodo_mes, tipo);


--
-- Name: aviso_batch aviso_batch_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aviso_batch
    ADD CONSTRAINT aviso_batch_pkey PRIMARY KEY (id);


--
-- Name: aviso_operation aviso_operation_dd_operation_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aviso_operation
    ADD CONSTRAINT aviso_operation_dd_operation_id_key UNIQUE (dd_operation_id);


--
-- Name: aviso_operation aviso_operation_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aviso_operation
    ADD CONSTRAINT aviso_operation_pkey PRIMARY KEY (id);


--
-- Name: budget_line budget_line_monday_item_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.budget_line
    ADD CONSTRAINT budget_line_monday_item_id_key UNIQUE (monday_item_id);


--
-- Name: budget_line budget_line_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.budget_line
    ADD CONSTRAINT budget_line_pkey PRIMARY KEY (id);


--
-- Name: bulk_action_log bulk_action_log_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.bulk_action_log
    ADD CONSTRAINT bulk_action_log_pkey PRIMARY KEY (id);


--
-- Name: bulk_action_log bulk_action_log_undo_token_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.bulk_action_log
    ADD CONSTRAINT bulk_action_log_undo_token_key UNIQUE (undo_token);


--
-- Name: capital_config capital_config_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.capital_config
    ADD CONSTRAINT capital_config_pkey PRIMARY KEY (id);


--
-- Name: capital_config capital_config_version_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.capital_config
    ADD CONSTRAINT capital_config_version_key UNIQUE (version);


--
-- Name: change_order change_order_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.change_order
    ADD CONSTRAINT change_order_pkey PRIMARY KEY (id);


--
-- Name: collateral_haircut collateral_haircut_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.collateral_haircut
    ADD CONSTRAINT collateral_haircut_pkey PRIMARY KEY (instrument_type);


--
-- Name: collateral collateral_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.collateral
    ADD CONSTRAINT collateral_pkey PRIMARY KEY (id);


--
-- Name: comms_identity comms_identity_kind_value_norm_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.comms_identity
    ADD CONSTRAINT comms_identity_kind_value_norm_key UNIQUE (kind, value_norm);


--
-- Name: comms_identity comms_identity_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.comms_identity
    ADD CONSTRAINT comms_identity_pkey PRIMARY KEY (id);


--
-- Name: comms_outbox comms_outbox_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.comms_outbox
    ADD CONSTRAINT comms_outbox_pkey PRIMARY KEY (id);


--
-- Name: company_merge_log company_merge_log_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.company_merge_log
    ADD CONSTRAINT company_merge_log_pkey PRIMARY KEY (id);


--
-- Name: company company_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.company
    ADD CONSTRAINT company_pkey PRIMARY KEY (id);


--
-- Name: company_relationship company_relationship_parent_company_id_child_company_id_rel_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.company_relationship
    ADD CONSTRAINT company_relationship_parent_company_id_child_company_id_rel_key UNIQUE (parent_company_id, child_company_id, rel_type);


--
-- Name: company_relationship company_relationship_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.company_relationship
    ADD CONSTRAINT company_relationship_pkey PRIMARY KEY (id);


--
-- Name: concentration_cap concentration_cap_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.concentration_cap
    ADD CONSTRAINT concentration_cap_pkey PRIMARY KEY (id);


--
-- Name: concentration_limit concentration_limit_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.concentration_limit
    ADD CONSTRAINT concentration_limit_pkey PRIMARY KEY (id);


--
-- Name: contact_enrich contact_enrich_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.contact_enrich
    ADD CONSTRAINT contact_enrich_pkey PRIMARY KEY (id);


--
-- Name: contact_field contact_field_key_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.contact_field
    ADD CONSTRAINT contact_field_key_key UNIQUE (key);


--
-- Name: contact_field contact_field_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.contact_field
    ADD CONSTRAINT contact_field_pkey PRIMARY KEY (id);


--
-- Name: contact contact_monday_item_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.contact
    ADD CONSTRAINT contact_monday_item_id_key UNIQUE (monday_item_id);


--
-- Name: contact contact_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.contact
    ADD CONSTRAINT contact_pkey PRIMARY KEY (id);


--
-- Name: counterparty counterparty_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.counterparty
    ADD CONSTRAINT counterparty_pkey PRIMARY KEY (id);


--
-- Name: covenant_test covenant_test_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.covenant_test
    ADD CONSTRAINT covenant_test_pkey PRIMARY KEY (id);


--
-- Name: coverage_covenant coverage_covenant_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.coverage_covenant
    ADD CONSTRAINT coverage_covenant_pkey PRIMARY KEY (id);


--
-- Name: coverage_ratio coverage_ratio_facility_id_as_of_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.coverage_ratio
    ADD CONSTRAINT coverage_ratio_facility_id_as_of_key UNIQUE (facility_id, as_of);


--
-- Name: coverage_ratio coverage_ratio_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.coverage_ratio
    ADD CONSTRAINT coverage_ratio_pkey PRIMARY KEY (id);


--
-- Name: cp_item cp_item_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.cp_item
    ADD CONSTRAINT cp_item_pkey PRIMARY KEY (id);


--
-- Name: credit_memo credit_memo_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.credit_memo
    ADD CONSTRAINT credit_memo_pkey PRIMARY KEY (id);


--
-- Name: credit_sanction credit_sanction_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.credit_sanction
    ADD CONSTRAINT credit_sanction_pkey PRIMARY KEY (id);


--
-- Name: dashboard dashboard_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dashboard
    ADD CONSTRAINT dashboard_pkey PRIMARY KEY (id);


--
-- Name: dd_aviso dd_aviso_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_aviso
    ADD CONSTRAINT dd_aviso_pkey PRIMARY KEY (id);


--
-- Name: dd_check dd_check_counterparty_id_check_type_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_check
    ADD CONSTRAINT dd_check_counterparty_id_check_type_key UNIQUE (counterparty_id, check_type);


--
-- Name: dd_check dd_check_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_check
    ADD CONSTRAINT dd_check_pkey PRIMARY KEY (id);


--
-- Name: dd_consent dd_consent_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_consent
    ADD CONSTRAINT dd_consent_pkey PRIMARY KEY (id);


--
-- Name: dd_decision dd_decision_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_decision
    ADD CONSTRAINT dd_decision_pkey PRIMARY KEY (id);


--
-- Name: dd_lpb dd_lpb_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_lpb
    ADD CONSTRAINT dd_lpb_pkey PRIMARY KEY (id);


--
-- Name: dd_operation dd_operation_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_operation
    ADD CONSTRAINT dd_operation_pkey PRIMARY KEY (id);


--
-- Name: dd_ownership_edge dd_ownership_edge_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_ownership_edge
    ADD CONSTRAINT dd_ownership_edge_pkey PRIMARY KEY (id);


--
-- Name: dd_ownership_node dd_ownership_node_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_ownership_node
    ADD CONSTRAINT dd_ownership_node_pkey PRIMARY KEY (id);


--
-- Name: dd_screening_hit dd_screening_hit_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_screening_hit
    ADD CONSTRAINT dd_screening_hit_pkey PRIMARY KEY (id);


--
-- Name: dd_ubo_document dd_ubo_document_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_ubo_document
    ADD CONSTRAINT dd_ubo_document_pkey PRIMARY KEY (id);


--
-- Name: dd_ubo dd_ubo_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_ubo
    ADD CONSTRAINT dd_ubo_pkey PRIMARY KEY (id);


--
-- Name: deal_attachment deal_attachment_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal_attachment
    ADD CONSTRAINT deal_attachment_pkey PRIMARY KEY (id);


--
-- Name: deal_comment deal_comment_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal_comment
    ADD CONSTRAINT deal_comment_pkey PRIMARY KEY (id);


--
-- Name: deal_event deal_event_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal_event
    ADD CONSTRAINT deal_event_pkey PRIMARY KEY (id);


--
-- Name: deal_financials deal_financials_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal_financials
    ADD CONSTRAINT deal_financials_pkey PRIMARY KEY (deal_id);


--
-- Name: deal_line_item deal_line_item_monday_item_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal_line_item
    ADD CONSTRAINT deal_line_item_monday_item_id_key UNIQUE (monday_item_id);


--
-- Name: deal_line_item deal_line_item_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal_line_item
    ADD CONSTRAINT deal_line_item_pkey PRIMARY KEY (id);


--
-- Name: deal deal_monday_item_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal
    ADD CONSTRAINT deal_monday_item_id_key UNIQUE (monday_item_id);


--
-- Name: deal deal_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal
    ADD CONSTRAINT deal_pkey PRIMARY KEY (id);


--
-- Name: deal_rpu deal_rpu_deal_id_rpu_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal_rpu
    ADD CONSTRAINT deal_rpu_deal_id_rpu_key UNIQUE (deal_id, rpu);


--
-- Name: deal_rpu deal_rpu_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal_rpu
    ADD CONSTRAINT deal_rpu_pkey PRIMARY KEY (id);


--
-- Name: delegated_authority delegated_authority_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.delegated_authority
    ADD CONSTRAINT delegated_authority_pkey PRIMARY KEY (tier);


--
-- Name: dlp_clock dlp_clock_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dlp_clock
    ADD CONSTRAINT dlp_clock_pkey PRIMARY KEY (project_id);


--
-- Name: dlp_defect dlp_defect_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dlp_defect
    ADD CONSTRAINT dlp_defect_pkey PRIMARY KEY (id);


--
-- Name: ebr_factor ebr_factor_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.ebr_factor
    ADD CONSTRAINT ebr_factor_pkey PRIMARY KEY (code);


--
-- Name: ebr_rating ebr_rating_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.ebr_rating
    ADD CONSTRAINT ebr_rating_pkey PRIMARY KEY (id);


--
-- Name: ecl_run ecl_run_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.ecl_run
    ADD CONSTRAINT ecl_run_pkey PRIMARY KEY (id);


--
-- Name: edd_item edd_item_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.edd_item
    ADD CONSTRAINT edd_item_pkey PRIMARY KEY (id);


--
-- Name: efos_69b efos_69b_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.efos_69b
    ADD CONSTRAINT efos_69b_pkey PRIMARY KEY (rfc);


--
-- Name: email_account email_account_owner_email_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.email_account
    ADD CONSTRAINT email_account_owner_email_key UNIQUE (owner_email);


--
-- Name: email_account email_account_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.email_account
    ADD CONSTRAINT email_account_pkey PRIMARY KEY (id);


--
-- Name: email_template email_template_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.email_template
    ADD CONSTRAINT email_template_pkey PRIMARY KEY (id);


--
-- Name: email_tracking email_tracking_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.email_tracking
    ADD CONSTRAINT email_tracking_pkey PRIMARY KEY (id);


--
-- Name: expense expense_monday_item_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.expense
    ADD CONSTRAINT expense_monday_item_id_key UNIQUE (monday_item_id);


--
-- Name: expense expense_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.expense
    ADD CONSTRAINT expense_pkey PRIMARY KEY (id);


--
-- Name: facility_base_case facility_base_case_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.facility_base_case
    ADD CONSTRAINT facility_base_case_pkey PRIMARY KEY (id);


--
-- Name: facility facility_deal_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.facility
    ADD CONSTRAINT facility_deal_id_key UNIQUE (deal_id);


--
-- Name: facility facility_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.facility
    ADD CONSTRAINT facility_pkey PRIMARY KEY (id);


--
-- Name: facility_scenario_ecl facility_scenario_ecl_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.facility_scenario_ecl
    ADD CONSTRAINT facility_scenario_ecl_pkey PRIMARY KEY (id);


--
-- Name: facility_schedule facility_schedule_facility_id_period_no_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.facility_schedule
    ADD CONSTRAINT facility_schedule_facility_id_period_no_key UNIQUE (facility_id, period_no);


--
-- Name: facility_schedule facility_schedule_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.facility_schedule
    ADD CONSTRAINT facility_schedule_pkey PRIMARY KEY (id);


--
-- Name: field_capture field_capture_client_uuid_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.field_capture
    ADD CONSTRAINT field_capture_client_uuid_key UNIQUE (client_uuid);


--
-- Name: field_capture field_capture_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.field_capture
    ADD CONSTRAINT field_capture_pkey PRIMARY KEY (id);


--
-- Name: forbearance_event forbearance_event_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.forbearance_event
    ADD CONSTRAINT forbearance_event_pkey PRIMARY KEY (id);


--
-- Name: generation_actual generation_actual_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.generation_actual
    ADD CONSTRAINT generation_actual_pkey PRIMARY KEY (id);


--
-- Name: generation_actual generation_actual_project_id_period_start_period_end_source_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.generation_actual
    ADD CONSTRAINT generation_actual_project_id_period_start_period_end_source_key UNIQUE (project_id, period_start, period_end, source);


--
-- Name: generation_baseline generation_baseline_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.generation_baseline
    ADD CONSTRAINT generation_baseline_pkey PRIMARY KEY (id);


--
-- Name: generation_baseline generation_baseline_project_id_year_no_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.generation_baseline
    ADD CONSTRAINT generation_baseline_project_id_year_no_key UNIQUE (project_id, year_no);


--
-- Name: goods_receipt goods_receipt_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.goods_receipt
    ADD CONSTRAINT goods_receipt_pkey PRIMARY KEY (id);


--
-- Name: huddle_run huddle_run_doc_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.huddle_run
    ADD CONSTRAINT huddle_run_doc_id_key UNIQUE (doc_id);


--
-- Name: huddle_run huddle_run_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.huddle_run
    ADD CONSTRAINT huddle_run_pkey PRIMARY KEY (id);


--
-- Name: inspection inspection_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.inspection
    ADD CONSTRAINT inspection_pkey PRIMARY KEY (id);


--
-- Name: invoice invoice_monday_item_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.invoice
    ADD CONSTRAINT invoice_monday_item_id_key UNIQUE (monday_item_id);


--
-- Name: invoice invoice_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.invoice
    ADD CONSTRAINT invoice_pkey PRIMARY KEY (id);


--
-- Name: itp_item itp_item_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.itp_item
    ADD CONSTRAINT itp_item_pkey PRIMARY KEY (id);


--
-- Name: ld_accrual ld_accrual_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.ld_accrual
    ADD CONSTRAINT ld_accrual_pkey PRIMARY KEY (project_id);


--
-- Name: lgd_realization lgd_realization_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.lgd_realization
    ADD CONSTRAINT lgd_realization_pkey PRIMARY KEY (id);


--
-- Name: limit_breach limit_breach_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.limit_breach
    ADD CONSTRAINT limit_breach_pkey PRIMARY KEY (id);


--
-- Name: macro_scenario macro_scenario_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.macro_scenario
    ADD CONSTRAINT macro_scenario_pkey PRIMARY KEY (id);


--
-- Name: macro_scenario_set macro_scenario_set_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.macro_scenario_set
    ADD CONSTRAINT macro_scenario_set_pkey PRIMARY KEY (id);


--
-- Name: notification notification_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.notification
    ADD CONSTRAINT notification_pkey PRIMARY KEY (id);


--
-- Name: operacion_relevante operacion_relevante_dedupe_key_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.operacion_relevante
    ADD CONSTRAINT operacion_relevante_dedupe_key_key UNIQUE (dedupe_key);


--
-- Name: operacion_relevante operacion_relevante_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.operacion_relevante
    ADD CONSTRAINT operacion_relevante_pkey PRIMARY KEY (id);


--
-- Name: ops_report ops_report_monday_item_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.ops_report
    ADD CONSTRAINT ops_report_monday_item_id_key UNIQUE (monday_item_id);


--
-- Name: ops_report ops_report_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.ops_report
    ADD CONSTRAINT ops_report_pkey PRIMARY KEY (id);


--
-- Name: pd_rating pd_rating_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.pd_rating
    ADD CONSTRAINT pd_rating_pkey PRIMARY KEY (id);


--
-- Name: pd_scorecard_factor pd_scorecard_factor_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.pd_scorecard_factor
    ADD CONSTRAINT pd_scorecard_factor_pkey PRIMARY KEY (code);


--
-- Name: pd_term_structure pd_term_structure_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.pd_term_structure
    ADD CONSTRAINT pd_term_structure_pkey PRIMARY KEY (rating_id, year);


--
-- Name: performance_backcharge performance_backcharge_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.performance_backcharge
    ADD CONSTRAINT performance_backcharge_pkey PRIMARY KEY (id);


--
-- Name: po_invoice po_invoice_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.po_invoice
    ADD CONSTRAINT po_invoice_pkey PRIMARY KEY (id);


--
-- Name: progress_claim progress_claim_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.progress_claim
    ADD CONSTRAINT progress_claim_pkey PRIMARY KEY (id);


--
-- Name: project_cost project_cost_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.project_cost
    ADD CONSTRAINT project_cost_pkey PRIMARY KEY (id);


--
-- Name: project project_deal_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.project
    ADD CONSTRAINT project_deal_id_key UNIQUE (deal_id);


--
-- Name: project_milestone project_milestone_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.project_milestone
    ADD CONSTRAINT project_milestone_pkey PRIMARY KEY (id);


--
-- Name: project_milestone project_milestone_project_id_seq_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.project_milestone
    ADD CONSTRAINT project_milestone_project_id_seq_key UNIQUE (project_id, seq);


--
-- Name: project project_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.project
    ADD CONSTRAINT project_pkey PRIMARY KEY (id);


--
-- Name: proposal_event proposal_event_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.proposal_event
    ADD CONSTRAINT proposal_event_pkey PRIMARY KEY (id);


--
-- Name: proposal_line proposal_line_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.proposal_line
    ADD CONSTRAINT proposal_line_pkey PRIMARY KEY (id);


--
-- Name: proposal proposal_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.proposal
    ADD CONSTRAINT proposal_pkey PRIMARY KEY (id);


--
-- Name: proposal proposal_public_token_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.proposal
    ADD CONSTRAINT proposal_public_token_key UNIQUE (public_token);


--
-- Name: proposal_signature proposal_signature_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.proposal_signature
    ADD CONSTRAINT proposal_signature_pkey PRIMARY KEY (id);


--
-- Name: purchase_order purchase_order_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.purchase_order
    ADD CONSTRAINT purchase_order_pkey PRIMARY KEY (id);


--
-- Name: push_subscription push_subscription_endpoint_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.push_subscription
    ADD CONSTRAINT push_subscription_endpoint_key UNIQUE (endpoint);


--
-- Name: push_subscription push_subscription_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.push_subscription
    ADD CONSTRAINT push_subscription_pkey PRIMARY KEY (id);


--
-- Name: quote quote_monday_item_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.quote
    ADD CONSTRAINT quote_monday_item_id_key UNIQUE (monday_item_id);


--
-- Name: quote quote_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.quote
    ADD CONSTRAINT quote_pkey PRIMARY KEY (id);


--
-- Name: raroc_assessment raroc_assessment_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.raroc_assessment
    ADD CONSTRAINT raroc_assessment_pkey PRIMARY KEY (id);


--
-- Name: recovery_posting recovery_posting_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.recovery_posting
    ADD CONSTRAINT recovery_posting_pkey PRIMARY KEY (id);


--
-- Name: reforecast reforecast_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.reforecast
    ADD CONSTRAINT reforecast_pkey PRIMARY KEY (id);


--
-- Name: repayment repayment_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.repayment
    ADD CONSTRAINT repayment_pkey PRIMARY KEY (id);


--
-- Name: retention_ledger retention_ledger_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.retention_ledger
    ADD CONSTRAINT retention_ledger_pkey PRIMARY KEY (id);


--
-- Name: roi_artifact roi_artifact_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.roi_artifact
    ADD CONSTRAINT roi_artifact_pkey PRIMARY KEY (id);


--
-- Name: sales_target sales_target_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sales_target
    ADD CONSTRAINT sales_target_pkey PRIMARY KEY (id);


--
-- Name: sanction_override sanction_override_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sanction_override
    ADD CONSTRAINT sanction_override_pkey PRIMARY KEY (id);


--
-- Name: sanctions_entry sanctions_entry_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sanctions_entry
    ADD CONSTRAINT sanctions_entry_pkey PRIMARY KEY (id);


--
-- Name: saved_view saved_view_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.saved_view
    ADD CONSTRAINT saved_view_pkey PRIMARY KEY (id);


--
-- Name: schedule_activity schedule_activity_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.schedule_activity
    ADD CONSTRAINT schedule_activity_pkey PRIMARY KEY (id);


--
-- Name: schedule_baseline schedule_baseline_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.schedule_baseline
    ADD CONSTRAINT schedule_baseline_pkey PRIMARY KEY (id);


--
-- Name: schedule_dependency schedule_dependency_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.schedule_dependency
    ADD CONSTRAINT schedule_dependency_pkey PRIMARY KEY (id);


--
-- Name: schedule_forecast schedule_forecast_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.schedule_forecast
    ADD CONSTRAINT schedule_forecast_pkey PRIMARY KEY (id);


--
-- Name: screening_list_version screening_list_version_list_name_version_tag_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.screening_list_version
    ADD CONSTRAINT screening_list_version_list_name_version_tag_key UNIQUE (list_name, version_tag);


--
-- Name: screening_list_version screening_list_version_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.screening_list_version
    ADD CONSTRAINT screening_list_version_pkey PRIMARY KEY (id);


--
-- Name: screening_provenance screening_provenance_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.screening_provenance
    ADD CONSTRAINT screening_provenance_pkey PRIMARY KEY (id);


--
-- Name: sequence_enrollment sequence_enrollment_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sequence_enrollment
    ADD CONSTRAINT sequence_enrollment_pkey PRIMARY KEY (id);


--
-- Name: sequence_enrollment sequence_enrollment_sequence_id_deal_id_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sequence_enrollment
    ADD CONSTRAINT sequence_enrollment_sequence_id_deal_id_key UNIQUE (sequence_id, deal_id);


--
-- Name: sequence sequence_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sequence
    ADD CONSTRAINT sequence_pkey PRIMARY KEY (id);


--
-- Name: sequence_step sequence_step_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sequence_step
    ADD CONSTRAINT sequence_step_pkey PRIMARY KEY (id);


--
-- Name: sequence_step sequence_step_sequence_id_step_no_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sequence_step
    ADD CONSTRAINT sequence_step_sequence_id_step_no_key UNIQUE (sequence_id, step_no);


--
-- Name: stage_probability stage_probability_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.stage_probability
    ADD CONSTRAINT stage_probability_pkey PRIMARY KEY (stage);


--
-- Name: sub_back_charge sub_back_charge_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sub_back_charge
    ADD CONSTRAINT sub_back_charge_pkey PRIMARY KEY (id);


--
-- Name: sub_payment_claim sub_payment_claim_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sub_payment_claim
    ADD CONSTRAINT sub_payment_claim_pkey PRIMARY KEY (id);


--
-- Name: sub_retention_ledger sub_retention_ledger_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sub_retention_ledger
    ADD CONSTRAINT sub_retention_ledger_pkey PRIMARY KEY (id);


--
-- Name: subcontract subcontract_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.subcontract
    ADD CONSTRAINT subcontract_pkey PRIMARY KEY (id);


--
-- Name: sync_state sync_state_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sync_state
    ADD CONSTRAINT sync_state_pkey PRIMARY KEY (source);


--
-- Name: task task_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.task
    ADD CONSTRAINT task_pkey PRIMARY KEY (id);


--
-- Name: todo todo_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.todo
    ADD CONSTRAINT todo_pkey PRIMARY KEY (id);


--
-- Name: todo_subtask todo_subtask_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.todo_subtask
    ADD CONSTRAINT todo_subtask_pkey PRIMARY KEY (id);


--
-- Name: training_completion training_completion_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.training_completion
    ADD CONSTRAINT training_completion_pkey PRIMARY KEY (id);


--
-- Name: training_course training_course_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.training_course
    ADD CONSTRAINT training_course_pkey PRIMARY KEY (id);


--
-- Name: training_course training_course_topic_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.training_course
    ADD CONSTRAINT training_course_topic_key UNIQUE (topic);


--
-- Name: transaction_profile transaction_profile_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.transaction_profile
    ADD CONSTRAINT transaction_profile_pkey PRIMARY KEY (id);


--
-- Name: txn_monitor_event txn_monitor_event_dedupe_key_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.txn_monitor_event
    ADD CONSTRAINT txn_monitor_event_dedupe_key_key UNIQUE (dedupe_key);


--
-- Name: txn_monitor_event txn_monitor_event_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.txn_monitor_event
    ADD CONSTRAINT txn_monitor_event_pkey PRIMARY KEY (id);


--
-- Name: txn_profile txn_profile_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.txn_profile
    ADD CONSTRAINT txn_profile_pkey PRIMARY KEY (id);


--
-- Name: uma_config uma_config_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.uma_config
    ADD CONSTRAINT uma_config_pkey PRIMARY KEY (id);


--
-- Name: uma_config uma_config_version_key; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.uma_config
    ADD CONSTRAINT uma_config_version_key UNIQUE (version);


--
-- Name: workout_case workout_case_pkey; Type: CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.workout_case
    ADD CONSTRAINT workout_case_pkey PRIMARY KEY (id);


--
-- Name: account_name_lower_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX account_name_lower_idx ON crm.account USING btree (lower(name));


--
-- Name: activity_contact; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX activity_contact ON crm.activity USING btree (contact_id, occurred_at DESC);


--
-- Name: activity_deal; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX activity_deal ON crm.activity USING btree (deal_id, occurred_at DESC);


--
-- Name: ai_draft_deal_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX ai_draft_deal_idx ON crm.ai_draft USING btree (deal_id, created_at DESC);


--
-- Name: ai_log_deal_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX ai_log_deal_idx ON crm.ai_prompt_log USING btree (deal_id, created_at DESC);


--
-- Name: aml_manual_ver_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE UNIQUE INDEX aml_manual_ver_idx ON crm.aml_manual USING btree (version);


--
-- Name: automation_event_unproc; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX automation_event_unproc ON crm.automation_event USING btree (created_at) WHERE (processed_at IS NULL);


--
-- Name: collateral_deal; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX collateral_deal ON crm.collateral USING btree (deal_id);


--
-- Name: comms_outbox_dispatch; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX comms_outbox_dispatch ON crm.comms_outbox USING btree (status, next_retry_at) WHERE (status = ANY (ARRAY['queued'::text, 'failed'::text]));


--
-- Name: comms_outbox_queued; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX comms_outbox_queued ON crm.comms_outbox USING btree (status) WHERE (status = 'queued'::text);


--
-- Name: company_rfc_ux; Type: INDEX; Schema: crm; Owner: -
--

CREATE UNIQUE INDEX company_rfc_ux ON crm.company USING btree (upper(rfc)) WHERE (canonical AND (rfc IS NOT NULL) AND (rfc <> ''::text));


--
-- Name: contact_email_lower_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX contact_email_lower_idx ON crm.contact USING btree (lower(email));


--
-- Name: contact_google_resource_uidx; Type: INDEX; Schema: crm; Owner: -
--

CREATE UNIQUE INDEX contact_google_resource_uidx ON crm.contact USING btree (google_resource_name) WHERE (google_resource_name IS NOT NULL);


--
-- Name: contact_owner_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX contact_owner_idx ON crm.contact USING btree (owner_id);


--
-- Name: contact_phone_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX contact_phone_idx ON crm.contact USING btree (phone);


--
-- Name: counterparty_rfc_uidx; Type: INDEX; Schema: crm; Owner: -
--

CREATE UNIQUE INDEX counterparty_rfc_uidx ON crm.counterparty USING btree (upper(rfc)) WHERE (rfc IS NOT NULL);


--
-- Name: cp_item_deal; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX cp_item_deal ON crm.cp_item USING btree (deal_id);


--
-- Name: credit_memo_deal; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX credit_memo_deal ON crm.credit_memo USING btree (deal_id, version DESC);


--
-- Name: dd_decision_cp_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX dd_decision_cp_idx ON crm.dd_decision USING btree (counterparty_id, created_at DESC);


--
-- Name: dd_lpb_norm_trgm; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX dd_lpb_norm_trgm ON crm.dd_lpb USING gin (norm_name public.gin_trgm_ops);


--
-- Name: dd_lpb_rfc; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX dd_lpb_rfc ON crm.dd_lpb USING btree (upper(rfc));


--
-- Name: dd_operation_cp; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX dd_operation_cp ON crm.dd_operation USING btree (counterparty_id, fecha);


--
-- Name: dd_screening_hit_cp_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX dd_screening_hit_cp_idx ON crm.dd_screening_hit USING btree (counterparty_id, created_at DESC);


--
-- Name: deal_archived; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX deal_archived ON crm.deal USING btree (archived_at) WHERE (archived_at IS NULL);


--
-- Name: deal_attachment_deal_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX deal_attachment_deal_idx ON crm.deal_attachment USING btree (deal_id, created_at DESC);


--
-- Name: deal_comment_deal_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX deal_comment_deal_idx ON crm.deal_comment USING btree (deal_id, created_at DESC);


--
-- Name: deal_event_deal_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX deal_event_deal_idx ON crm.deal_event USING btree (deal_id, created_at DESC);


--
-- Name: deal_owner_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX deal_owner_idx ON crm.deal USING btree (owner_id);


--
-- Name: deal_rpu_deal_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX deal_rpu_deal_idx ON crm.deal_rpu USING btree (deal_id);


--
-- Name: deal_rpu_rpu_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX deal_rpu_rpu_idx ON crm.deal_rpu USING btree (rpu);


--
-- Name: deal_stage_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX deal_stage_idx ON crm.deal USING btree (stage);


--
-- Name: deal_updated_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX deal_updated_idx ON crm.deal USING btree (updated_at DESC);


--
-- Name: ebr_rating_cp; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX ebr_rating_cp ON crm.ebr_rating USING btree (counterparty_id, computed_at DESC);


--
-- Name: edd_item_cp; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX edd_item_cp ON crm.edd_item USING btree (counterparty_id);


--
-- Name: facility_schedule_fid; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX facility_schedule_fid ON crm.facility_schedule USING btree (facility_id, due_date);


--
-- Name: facility_status; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX facility_status ON crm.facility USING btree (status);


--
-- Name: fbc_active; Type: INDEX; Schema: crm; Owner: -
--

CREATE UNIQUE INDEX fbc_active ON crm.facility_base_case USING btree (facility_id) WHERE active;


--
-- Name: itp_item_pid; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX itp_item_pid ON crm.itp_item USING btree (project_id);


--
-- Name: limit_breach_deal_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX limit_breach_deal_idx ON crm.limit_breach USING btree (deal_id, computed_at DESC);


--
-- Name: line_item_deal_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX line_item_deal_idx ON crm.deal_line_item USING btree (deal_id);


--
-- Name: notification_dedupe_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE UNIQUE INDEX notification_dedupe_idx ON crm.notification USING btree (dedupe_key) WHERE (dedupe_key IS NOT NULL);


--
-- Name: notification_pending_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX notification_pending_idx ON crm.notification USING btree (recipient_email, action_state, due_at) WHERE (action_state = 'pending'::text);


--
-- Name: notification_recipient_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX notification_recipient_idx ON crm.notification USING btree (recipient_email, read, created_at DESC);


--
-- Name: notification_unpushed; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX notification_unpushed ON crm.notification USING btree (created_at) WHERE (pushed_at IS NULL);


--
-- Name: or_cp_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX or_cp_idx ON crm.operacion_relevante USING btree (counterparty_id, period);


--
-- Name: own_node_cp; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX own_node_cp ON crm.dd_ownership_node USING btree (counterparty_id);


--
-- Name: pd_rating_deal; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX pd_rating_deal ON crm.pd_rating USING btree (deal_id, computed_at DESC);


--
-- Name: project_cost_pid; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX project_cost_pid ON crm.project_cost USING btree (project_id);


--
-- Name: project_milestone_pid; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX project_milestone_pid ON crm.project_milestone USING btree (project_id, seq);


--
-- Name: proposal_deal; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX proposal_deal ON crm.proposal USING btree (deal_id, version DESC);


--
-- Name: purchase_order_pid; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX purchase_order_pid ON crm.purchase_order USING btree (project_id);


--
-- Name: push_sub_owner; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX push_sub_owner ON crm.push_subscription USING btree (owner_email) WHERE active;


--
-- Name: raroc_deal_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX raroc_deal_idx ON crm.raroc_assessment USING btree (deal_id, computed_at DESC);


--
-- Name: repayment_fid; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX repayment_fid ON crm.repayment USING btree (facility_id, received_at);


--
-- Name: sales_target_live; Type: INDEX; Schema: crm; Owner: -
--

CREATE UNIQUE INDEX sales_target_live ON crm.sales_target USING btree (scope, COALESCE(owner_id, '00000000-0000-0000-0000-000000000000'::uuid), COALESCE(team_key, ''::text), period_type, period_start) WHERE (status = 'approved'::text);


--
-- Name: sanction_override_deal_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX sanction_override_deal_idx ON crm.sanction_override USING btree (deal_id, created_at DESC);


--
-- Name: sanctions_norm_trgm; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX sanctions_norm_trgm ON crm.sanctions_entry USING gin (norm_name public.gin_trgm_ops);


--
-- Name: sch_act_pid; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX sch_act_pid ON crm.schedule_activity USING btree (project_id);


--
-- Name: subcontract_pid; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX subcontract_pid ON crm.subcontract USING btree (project_id);


--
-- Name: task_assignee; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX task_assignee ON crm.task USING btree (assignee, status, due_at);


--
-- Name: task_deal; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX task_deal ON crm.task USING btree (deal_id, status);


--
-- Name: todo_deal_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX todo_deal_idx ON crm.todo USING btree (deal_id);


--
-- Name: todo_dedupe_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE UNIQUE INDEX todo_dedupe_idx ON crm.todo USING btree (source_doc_id, md5(COALESCE(source_line, title))) WHERE ((source = 'huddle'::text) AND (source_doc_id IS NOT NULL));


--
-- Name: todo_owner_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX todo_owner_idx ON crm.todo USING btree (owner_id);


--
-- Name: todo_source_doc_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX todo_source_doc_idx ON crm.todo USING btree (source_doc_id);


--
-- Name: todo_status_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX todo_status_idx ON crm.todo USING btree (status);


--
-- Name: todo_subtask_todo_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX todo_subtask_todo_idx ON crm.todo_subtask USING btree (todo_id, "position");


--
-- Name: training_user_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX training_user_idx ON crm.training_completion USING btree (app_user_id, topic);


--
-- Name: txn_event_cp_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX txn_event_cp_idx ON crm.txn_monitor_event USING btree (counterparty_id, status, created_at DESC);


--
-- Name: txn_profile_cp_idx; Type: INDEX; Schema: crm; Owner: -
--

CREATE INDEX txn_profile_cp_idx ON crm.txn_profile USING btree (counterparty_id, version DESC);


--
-- Name: deal_summary _RETURN; Type: RULE; Schema: crm; Owner: -
--

CREATE OR REPLACE VIEW crm.deal_summary WITH (security_invoker='on') AS
 SELECT d.id,
    d.name,
    d.stage,
    d.rpu,
    d.owner_id,
    d.account_id,
    d.expected_close_date,
    d.updated_at,
    d.monday_item_id,
    COALESCE(sum(c.kwp), (0)::numeric) AS total_kwp,
    COALESCE(sum(c.epc_value), (0)::numeric) AS total_epc_value,
    COALESCE(sum(c.vpn_contrato), (0)::numeric) AS total_vpn
   FROM (crm.deal d
     LEFT JOIN crm.deal_line_item_calc c ON ((c.deal_id = d.id)))
  GROUP BY d.id;


--
-- Name: activity activity_automation_emit; Type: TRIGGER; Schema: crm; Owner: -
--

CREATE TRIGGER activity_automation_emit AFTER INSERT ON crm.activity FOR EACH ROW EXECUTE FUNCTION crm._emit_activity_event();


--
-- Name: deal deal_automation_emit; Type: TRIGGER; Schema: crm; Owner: -
--

CREATE TRIGGER deal_automation_emit AFTER UPDATE ON crm.deal FOR EACH ROW EXECUTE FUNCTION crm._emit_deal_event();


--
-- Name: todo todo_set_updated_at; Type: TRIGGER; Schema: crm; Owner: -
--

CREATE TRIGGER todo_set_updated_at BEFORE UPDATE ON crm.todo FOR EACH ROW EXECUTE FUNCTION crm.set_updated_at();


--
-- Name: todo_subtask todo_subtask_set_updated_at; Type: TRIGGER; Schema: crm; Owner: -
--

CREATE TRIGGER todo_subtask_set_updated_at BEFORE UPDATE ON crm.todo_subtask FOR EACH ROW EXECUTE FUNCTION crm.set_updated_at();


--
-- Name: activity activity_contact_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.activity
    ADD CONSTRAINT activity_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES crm.contact(id) ON DELETE SET NULL;


--
-- Name: activity activity_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.activity
    ADD CONSTRAINT activity_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: ai_draft ai_draft_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.ai_draft
    ADD CONSTRAINT ai_draft_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: aml_alert aml_alert_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_alert
    ADD CONSTRAINT aml_alert_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: aml_audit_item aml_audit_item_audit_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_audit_item
    ADD CONSTRAINT aml_audit_item_audit_id_fkey FOREIGN KEY (audit_id) REFERENCES crm.aml_audit(id) ON DELETE CASCADE;


--
-- Name: aml_case aml_case_alert_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_case
    ADD CONSTRAINT aml_case_alert_id_fkey FOREIGN KEY (alert_id) REFERENCES crm.aml_alert(id) ON DELETE CASCADE;


--
-- Name: aml_control_clause aml_control_clause_control_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_control_clause
    ADD CONSTRAINT aml_control_clause_control_id_fkey FOREIGN KEY (control_id) REFERENCES crm.aml_control(id) ON DELETE CASCADE;


--
-- Name: aml_designation aml_designation_app_user_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_designation
    ADD CONSTRAINT aml_designation_app_user_id_fkey FOREIGN KEY (app_user_id) REFERENCES crm.app_user(id);


--
-- Name: aml_dictamen aml_dictamen_case_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aml_dictamen
    ADD CONSTRAINT aml_dictamen_case_id_fkey FOREIGN KEY (case_id) REFERENCES crm.aml_case(id) ON DELETE CASCADE;


--
-- Name: automation_action automation_action_recipe_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.automation_action
    ADD CONSTRAINT automation_action_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES crm.automation_recipe(id) ON DELETE CASCADE;


--
-- Name: automation_run automation_run_event_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.automation_run
    ADD CONSTRAINT automation_run_event_id_fkey FOREIGN KEY (event_id) REFERENCES crm.automation_event(id) ON DELETE CASCADE;


--
-- Name: automation_run automation_run_recipe_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.automation_run
    ADD CONSTRAINT automation_run_recipe_id_fkey FOREIGN KEY (recipe_id) REFERENCES crm.automation_recipe(id) ON DELETE CASCADE;


--
-- Name: aviso_operation aviso_operation_batch_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aviso_operation
    ADD CONSTRAINT aviso_operation_batch_id_fkey FOREIGN KEY (batch_id) REFERENCES crm.aviso_batch(id) ON DELETE CASCADE;


--
-- Name: aviso_operation aviso_operation_dd_operation_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.aviso_operation
    ADD CONSTRAINT aviso_operation_dd_operation_id_fkey FOREIGN KEY (dd_operation_id) REFERENCES crm.dd_operation(id) ON DELETE CASCADE;


--
-- Name: budget_line budget_line_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.budget_line
    ADD CONSTRAINT budget_line_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE SET NULL;


--
-- Name: change_order change_order_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.change_order
    ADD CONSTRAINT change_order_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: collateral collateral_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.collateral
    ADD CONSTRAINT collateral_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: collateral collateral_facility_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.collateral
    ADD CONSTRAINT collateral_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES crm.facility(id) ON DELETE SET NULL;


--
-- Name: comms_identity comms_identity_contact_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.comms_identity
    ADD CONSTRAINT comms_identity_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES crm.contact(id) ON DELETE CASCADE;


--
-- Name: comms_identity comms_identity_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.comms_identity
    ADD CONSTRAINT comms_identity_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE SET NULL;


--
-- Name: comms_outbox comms_outbox_contact_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.comms_outbox
    ADD CONSTRAINT comms_outbox_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES crm.contact(id) ON DELETE SET NULL;


--
-- Name: comms_outbox comms_outbox_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.comms_outbox
    ADD CONSTRAINT comms_outbox_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: company_merge_log company_merge_log_merged_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.company_merge_log
    ADD CONSTRAINT company_merge_log_merged_id_fkey FOREIGN KEY (merged_id) REFERENCES crm.company(id) ON DELETE SET NULL;


--
-- Name: company_merge_log company_merge_log_survivor_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.company_merge_log
    ADD CONSTRAINT company_merge_log_survivor_id_fkey FOREIGN KEY (survivor_id) REFERENCES crm.company(id) ON DELETE SET NULL;


--
-- Name: company company_merged_into_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.company
    ADD CONSTRAINT company_merged_into_id_fkey FOREIGN KEY (merged_into_id) REFERENCES crm.company(id) ON DELETE SET NULL;


--
-- Name: company_relationship company_relationship_child_company_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.company_relationship
    ADD CONSTRAINT company_relationship_child_company_id_fkey FOREIGN KEY (child_company_id) REFERENCES crm.company(id) ON DELETE CASCADE;


--
-- Name: company_relationship company_relationship_parent_company_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.company_relationship
    ADD CONSTRAINT company_relationship_parent_company_id_fkey FOREIGN KEY (parent_company_id) REFERENCES crm.company(id) ON DELETE CASCADE;


--
-- Name: contact contact_account_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.contact
    ADD CONSTRAINT contact_account_id_fkey FOREIGN KEY (account_id) REFERENCES crm.account(id) ON DELETE SET NULL;


--
-- Name: contact contact_company_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.contact
    ADD CONSTRAINT contact_company_id_fkey FOREIGN KEY (company_id) REFERENCES crm.company(id) ON DELETE SET NULL;


--
-- Name: contact contact_owner_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.contact
    ADD CONSTRAINT contact_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES crm.app_user(id) ON DELETE SET NULL;


--
-- Name: counterparty counterparty_company_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.counterparty
    ADD CONSTRAINT counterparty_company_id_fkey FOREIGN KEY (company_id) REFERENCES crm.company(id) ON DELETE SET NULL;


--
-- Name: covenant_test covenant_test_facility_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.covenant_test
    ADD CONSTRAINT covenant_test_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES crm.facility(id) ON DELETE CASCADE;


--
-- Name: coverage_ratio coverage_ratio_facility_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.coverage_ratio
    ADD CONSTRAINT coverage_ratio_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES crm.facility(id) ON DELETE CASCADE;


--
-- Name: cp_item cp_item_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.cp_item
    ADD CONSTRAINT cp_item_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: cp_item cp_item_sanction_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.cp_item
    ADD CONSTRAINT cp_item_sanction_id_fkey FOREIGN KEY (sanction_id) REFERENCES crm.credit_sanction(id) ON DELETE CASCADE;


--
-- Name: credit_memo credit_memo_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.credit_memo
    ADD CONSTRAINT credit_memo_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: credit_memo credit_memo_facility_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.credit_memo
    ADD CONSTRAINT credit_memo_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES crm.facility(id) ON DELETE SET NULL;


--
-- Name: credit_sanction credit_sanction_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.credit_sanction
    ADD CONSTRAINT credit_sanction_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: credit_sanction credit_sanction_memo_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.credit_sanction
    ADD CONSTRAINT credit_sanction_memo_id_fkey FOREIGN KEY (memo_id) REFERENCES crm.credit_memo(id) ON DELETE CASCADE;


--
-- Name: dd_aviso dd_aviso_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_aviso
    ADD CONSTRAINT dd_aviso_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: dd_check dd_check_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_check
    ADD CONSTRAINT dd_check_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: dd_consent dd_consent_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_consent
    ADD CONSTRAINT dd_consent_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: dd_decision dd_decision_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_decision
    ADD CONSTRAINT dd_decision_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: dd_operation dd_operation_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_operation
    ADD CONSTRAINT dd_operation_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE SET NULL;


--
-- Name: dd_operation dd_operation_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_operation
    ADD CONSTRAINT dd_operation_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE SET NULL;


--
-- Name: dd_operation dd_operation_facility_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_operation
    ADD CONSTRAINT dd_operation_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES crm.facility(id) ON DELETE SET NULL;


--
-- Name: dd_ownership_edge dd_ownership_edge_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_ownership_edge
    ADD CONSTRAINT dd_ownership_edge_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: dd_ownership_edge dd_ownership_edge_owned_node_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_ownership_edge
    ADD CONSTRAINT dd_ownership_edge_owned_node_id_fkey FOREIGN KEY (owned_node_id) REFERENCES crm.dd_ownership_node(id) ON DELETE CASCADE;


--
-- Name: dd_ownership_edge dd_ownership_edge_owner_node_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_ownership_edge
    ADD CONSTRAINT dd_ownership_edge_owner_node_id_fkey FOREIGN KEY (owner_node_id) REFERENCES crm.dd_ownership_node(id) ON DELETE CASCADE;


--
-- Name: dd_ownership_node dd_ownership_node_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_ownership_node
    ADD CONSTRAINT dd_ownership_node_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: dd_screening_hit dd_screening_hit_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_screening_hit
    ADD CONSTRAINT dd_screening_hit_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: dd_ubo dd_ubo_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_ubo
    ADD CONSTRAINT dd_ubo_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: dd_ubo_document dd_ubo_document_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_ubo_document
    ADD CONSTRAINT dd_ubo_document_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: dd_ubo_document dd_ubo_document_ubo_node_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_ubo_document
    ADD CONSTRAINT dd_ubo_document_ubo_node_id_fkey FOREIGN KEY (ubo_node_id) REFERENCES crm.dd_ownership_node(id) ON DELETE SET NULL;


--
-- Name: dd_ubo dd_ubo_node_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dd_ubo
    ADD CONSTRAINT dd_ubo_node_id_fkey FOREIGN KEY (node_id) REFERENCES crm.dd_ownership_node(id) ON DELETE SET NULL;


--
-- Name: deal deal_account_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal
    ADD CONSTRAINT deal_account_id_fkey FOREIGN KEY (account_id) REFERENCES crm.account(id) ON DELETE SET NULL;


--
-- Name: deal_attachment deal_attachment_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal_attachment
    ADD CONSTRAINT deal_attachment_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: deal_comment deal_comment_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal_comment
    ADD CONSTRAINT deal_comment_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: deal deal_company_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal
    ADD CONSTRAINT deal_company_id_fkey FOREIGN KEY (company_id) REFERENCES crm.company(id) ON DELETE SET NULL;


--
-- Name: deal deal_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal
    ADD CONSTRAINT deal_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE SET NULL;


--
-- Name: deal_event deal_event_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal_event
    ADD CONSTRAINT deal_event_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: deal_financials deal_financials_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal_financials
    ADD CONSTRAINT deal_financials_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: deal_line_item deal_line_item_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal_line_item
    ADD CONSTRAINT deal_line_item_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: deal deal_owner_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal
    ADD CONSTRAINT deal_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES crm.app_user(id) ON DELETE SET NULL;


--
-- Name: deal deal_primary_contact_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal
    ADD CONSTRAINT deal_primary_contact_id_fkey FOREIGN KEY (primary_contact_id) REFERENCES crm.contact(id) ON DELETE SET NULL;


--
-- Name: deal_rpu deal_rpu_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.deal_rpu
    ADD CONSTRAINT deal_rpu_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: dlp_clock dlp_clock_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dlp_clock
    ADD CONSTRAINT dlp_clock_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: dlp_defect dlp_defect_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.dlp_defect
    ADD CONSTRAINT dlp_defect_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: ebr_rating ebr_rating_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.ebr_rating
    ADD CONSTRAINT ebr_rating_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: ecl_run ecl_run_set_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.ecl_run
    ADD CONSTRAINT ecl_run_set_id_fkey FOREIGN KEY (set_id) REFERENCES crm.macro_scenario_set(id);


--
-- Name: edd_item edd_item_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.edd_item
    ADD CONSTRAINT edd_item_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: email_tracking email_tracking_outbox_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.email_tracking
    ADD CONSTRAINT email_tracking_outbox_id_fkey FOREIGN KEY (outbox_id) REFERENCES crm.comms_outbox(id) ON DELETE CASCADE;


--
-- Name: expense expense_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.expense
    ADD CONSTRAINT expense_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE SET NULL;


--
-- Name: facility_base_case facility_base_case_facility_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.facility_base_case
    ADD CONSTRAINT facility_base_case_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES crm.facility(id) ON DELETE CASCADE;


--
-- Name: facility facility_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.facility
    ADD CONSTRAINT facility_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id);


--
-- Name: facility facility_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.facility
    ADD CONSTRAINT facility_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: facility_scenario_ecl facility_scenario_ecl_facility_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.facility_scenario_ecl
    ADD CONSTRAINT facility_scenario_ecl_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES crm.facility(id) ON DELETE SET NULL;


--
-- Name: facility_scenario_ecl facility_scenario_ecl_run_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.facility_scenario_ecl
    ADD CONSTRAINT facility_scenario_ecl_run_id_fkey FOREIGN KEY (run_id) REFERENCES crm.ecl_run(id) ON DELETE CASCADE;


--
-- Name: facility_schedule facility_schedule_facility_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.facility_schedule
    ADD CONSTRAINT facility_schedule_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES crm.facility(id) ON DELETE CASCADE;


--
-- Name: field_capture field_capture_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.field_capture
    ADD CONSTRAINT field_capture_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE SET NULL;


--
-- Name: forbearance_event forbearance_event_facility_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.forbearance_event
    ADD CONSTRAINT forbearance_event_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES crm.facility(id) ON DELETE CASCADE;


--
-- Name: generation_actual generation_actual_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.generation_actual
    ADD CONSTRAINT generation_actual_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: generation_baseline generation_baseline_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.generation_baseline
    ADD CONSTRAINT generation_baseline_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: goods_receipt goods_receipt_po_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.goods_receipt
    ADD CONSTRAINT goods_receipt_po_id_fkey FOREIGN KEY (po_id) REFERENCES crm.purchase_order(id) ON DELETE CASCADE;


--
-- Name: inspection inspection_itp_item_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.inspection
    ADD CONSTRAINT inspection_itp_item_id_fkey FOREIGN KEY (itp_item_id) REFERENCES crm.itp_item(id) ON DELETE CASCADE;


--
-- Name: invoice invoice_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.invoice
    ADD CONSTRAINT invoice_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE SET NULL;


--
-- Name: invoice invoice_quote_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.invoice
    ADD CONSTRAINT invoice_quote_id_fkey FOREIGN KEY (quote_id) REFERENCES crm.quote(id) ON DELETE SET NULL;


--
-- Name: itp_item itp_item_milestone_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.itp_item
    ADD CONSTRAINT itp_item_milestone_id_fkey FOREIGN KEY (milestone_id) REFERENCES crm.project_milestone(id) ON DELETE SET NULL;


--
-- Name: itp_item itp_item_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.itp_item
    ADD CONSTRAINT itp_item_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: ld_accrual ld_accrual_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.ld_accrual
    ADD CONSTRAINT ld_accrual_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: lgd_realization lgd_realization_facility_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.lgd_realization
    ADD CONSTRAINT lgd_realization_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES crm.facility(id) ON DELETE CASCADE;


--
-- Name: limit_breach limit_breach_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.limit_breach
    ADD CONSTRAINT limit_breach_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: macro_scenario macro_scenario_set_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.macro_scenario
    ADD CONSTRAINT macro_scenario_set_id_fkey FOREIGN KEY (set_id) REFERENCES crm.macro_scenario_set(id) ON DELETE CASCADE;


--
-- Name: operacion_relevante operacion_relevante_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.operacion_relevante
    ADD CONSTRAINT operacion_relevante_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: operacion_relevante operacion_relevante_trigger_event_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.operacion_relevante
    ADD CONSTRAINT operacion_relevante_trigger_event_id_fkey FOREIGN KEY (trigger_event_id) REFERENCES crm.txn_monitor_event(id) ON DELETE SET NULL;


--
-- Name: ops_report ops_report_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.ops_report
    ADD CONSTRAINT ops_report_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE SET NULL;


--
-- Name: pd_rating pd_rating_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.pd_rating
    ADD CONSTRAINT pd_rating_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: pd_rating pd_rating_facility_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.pd_rating
    ADD CONSTRAINT pd_rating_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES crm.facility(id) ON DELETE SET NULL;


--
-- Name: pd_term_structure pd_term_structure_rating_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.pd_term_structure
    ADD CONSTRAINT pd_term_structure_rating_id_fkey FOREIGN KEY (rating_id) REFERENCES crm.pd_rating(id) ON DELETE CASCADE;


--
-- Name: performance_backcharge performance_backcharge_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.performance_backcharge
    ADD CONSTRAINT performance_backcharge_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: po_invoice po_invoice_po_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.po_invoice
    ADD CONSTRAINT po_invoice_po_id_fkey FOREIGN KEY (po_id) REFERENCES crm.purchase_order(id) ON DELETE CASCADE;


--
-- Name: progress_claim progress_claim_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.progress_claim
    ADD CONSTRAINT progress_claim_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: project_cost project_cost_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.project_cost
    ADD CONSTRAINT project_cost_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: project project_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.project
    ADD CONSTRAINT project_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE SET NULL;


--
-- Name: project project_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.project
    ADD CONSTRAINT project_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: project_milestone project_milestone_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.project_milestone
    ADD CONSTRAINT project_milestone_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: proposal proposal_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.proposal
    ADD CONSTRAINT proposal_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: proposal_event proposal_event_proposal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.proposal_event
    ADD CONSTRAINT proposal_event_proposal_id_fkey FOREIGN KEY (proposal_id) REFERENCES crm.proposal(id) ON DELETE CASCADE;


--
-- Name: proposal_line proposal_line_proposal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.proposal_line
    ADD CONSTRAINT proposal_line_proposal_id_fkey FOREIGN KEY (proposal_id) REFERENCES crm.proposal(id) ON DELETE CASCADE;


--
-- Name: proposal_signature proposal_signature_proposal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.proposal_signature
    ADD CONSTRAINT proposal_signature_proposal_id_fkey FOREIGN KEY (proposal_id) REFERENCES crm.proposal(id) ON DELETE CASCADE;


--
-- Name: purchase_order purchase_order_cost_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.purchase_order
    ADD CONSTRAINT purchase_order_cost_id_fkey FOREIGN KEY (cost_id) REFERENCES crm.project_cost(id) ON DELETE SET NULL;


--
-- Name: purchase_order purchase_order_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.purchase_order
    ADD CONSTRAINT purchase_order_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: quote quote_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.quote
    ADD CONSTRAINT quote_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE SET NULL;


--
-- Name: raroc_assessment raroc_assessment_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.raroc_assessment
    ADD CONSTRAINT raroc_assessment_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: recovery_posting recovery_posting_facility_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.recovery_posting
    ADD CONSTRAINT recovery_posting_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES crm.facility(id) ON DELETE CASCADE;


--
-- Name: reforecast reforecast_facility_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.reforecast
    ADD CONSTRAINT reforecast_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES crm.facility(id) ON DELETE CASCADE;


--
-- Name: repayment repayment_facility_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.repayment
    ADD CONSTRAINT repayment_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES crm.facility(id) ON DELETE CASCADE;


--
-- Name: retention_ledger retention_ledger_progress_claim_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.retention_ledger
    ADD CONSTRAINT retention_ledger_progress_claim_id_fkey FOREIGN KEY (progress_claim_id) REFERENCES crm.progress_claim(id) ON DELETE SET NULL;


--
-- Name: retention_ledger retention_ledger_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.retention_ledger
    ADD CONSTRAINT retention_ledger_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: roi_artifact roi_artifact_case_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.roi_artifact
    ADD CONSTRAINT roi_artifact_case_id_fkey FOREIGN KEY (case_id) REFERENCES crm.aml_case(id) ON DELETE CASCADE;


--
-- Name: sales_target sales_target_owner_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sales_target
    ADD CONSTRAINT sales_target_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES crm.app_user(id) ON DELETE CASCADE;


--
-- Name: sanction_override sanction_override_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sanction_override
    ADD CONSTRAINT sanction_override_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: saved_view saved_view_owner_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.saved_view
    ADD CONSTRAINT saved_view_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES crm.app_user(id) ON DELETE SET NULL;


--
-- Name: schedule_activity schedule_activity_linked_itp_item_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.schedule_activity
    ADD CONSTRAINT schedule_activity_linked_itp_item_id_fkey FOREIGN KEY (linked_itp_item_id) REFERENCES crm.itp_item(id) ON DELETE SET NULL;


--
-- Name: schedule_activity schedule_activity_linked_po_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.schedule_activity
    ADD CONSTRAINT schedule_activity_linked_po_id_fkey FOREIGN KEY (linked_po_id) REFERENCES crm.purchase_order(id) ON DELETE SET NULL;


--
-- Name: schedule_activity schedule_activity_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.schedule_activity
    ADD CONSTRAINT schedule_activity_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: schedule_baseline schedule_baseline_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.schedule_baseline
    ADD CONSTRAINT schedule_baseline_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: schedule_dependency schedule_dependency_predecessor_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.schedule_dependency
    ADD CONSTRAINT schedule_dependency_predecessor_id_fkey FOREIGN KEY (predecessor_id) REFERENCES crm.schedule_activity(id) ON DELETE CASCADE;


--
-- Name: schedule_dependency schedule_dependency_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.schedule_dependency
    ADD CONSTRAINT schedule_dependency_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: schedule_dependency schedule_dependency_successor_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.schedule_dependency
    ADD CONSTRAINT schedule_dependency_successor_id_fkey FOREIGN KEY (successor_id) REFERENCES crm.schedule_activity(id) ON DELETE CASCADE;


--
-- Name: schedule_forecast schedule_forecast_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.schedule_forecast
    ADD CONSTRAINT schedule_forecast_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: screening_provenance screening_provenance_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.screening_provenance
    ADD CONSTRAINT screening_provenance_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: screening_provenance screening_provenance_list_version_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.screening_provenance
    ADD CONSTRAINT screening_provenance_list_version_id_fkey FOREIGN KEY (list_version_id) REFERENCES crm.screening_list_version(id);


--
-- Name: sequence_enrollment sequence_enrollment_contact_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sequence_enrollment
    ADD CONSTRAINT sequence_enrollment_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES crm.contact(id) ON DELETE SET NULL;


--
-- Name: sequence_enrollment sequence_enrollment_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sequence_enrollment
    ADD CONSTRAINT sequence_enrollment_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: sequence_enrollment sequence_enrollment_sequence_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sequence_enrollment
    ADD CONSTRAINT sequence_enrollment_sequence_id_fkey FOREIGN KEY (sequence_id) REFERENCES crm.sequence(id) ON DELETE CASCADE;


--
-- Name: sequence_step sequence_step_sequence_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sequence_step
    ADD CONSTRAINT sequence_step_sequence_id_fkey FOREIGN KEY (sequence_id) REFERENCES crm.sequence(id) ON DELETE CASCADE;


--
-- Name: sub_back_charge sub_back_charge_subcontract_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sub_back_charge
    ADD CONSTRAINT sub_back_charge_subcontract_id_fkey FOREIGN KEY (subcontract_id) REFERENCES crm.subcontract(id) ON DELETE CASCADE;


--
-- Name: sub_payment_claim sub_payment_claim_subcontract_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sub_payment_claim
    ADD CONSTRAINT sub_payment_claim_subcontract_id_fkey FOREIGN KEY (subcontract_id) REFERENCES crm.subcontract(id) ON DELETE CASCADE;


--
-- Name: sub_retention_ledger sub_retention_ledger_claim_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sub_retention_ledger
    ADD CONSTRAINT sub_retention_ledger_claim_id_fkey FOREIGN KEY (claim_id) REFERENCES crm.sub_payment_claim(id) ON DELETE SET NULL;


--
-- Name: sub_retention_ledger sub_retention_ledger_subcontract_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.sub_retention_ledger
    ADD CONSTRAINT sub_retention_ledger_subcontract_id_fkey FOREIGN KEY (subcontract_id) REFERENCES crm.subcontract(id) ON DELETE CASCADE;


--
-- Name: subcontract subcontract_cost_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.subcontract
    ADD CONSTRAINT subcontract_cost_id_fkey FOREIGN KEY (cost_id) REFERENCES crm.project_cost(id) ON DELETE SET NULL;


--
-- Name: subcontract subcontract_itp_item_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.subcontract
    ADD CONSTRAINT subcontract_itp_item_id_fkey FOREIGN KEY (itp_item_id) REFERENCES crm.itp_item(id) ON DELETE SET NULL;


--
-- Name: subcontract subcontract_project_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.subcontract
    ADD CONSTRAINT subcontract_project_id_fkey FOREIGN KEY (project_id) REFERENCES crm.project(id) ON DELETE CASCADE;


--
-- Name: task task_contact_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.task
    ADD CONSTRAINT task_contact_id_fkey FOREIGN KEY (contact_id) REFERENCES crm.contact(id) ON DELETE SET NULL;


--
-- Name: task task_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.task
    ADD CONSTRAINT task_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE CASCADE;


--
-- Name: todo todo_deal_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.todo
    ADD CONSTRAINT todo_deal_id_fkey FOREIGN KEY (deal_id) REFERENCES crm.deal(id) ON DELETE SET NULL;


--
-- Name: todo todo_owner_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.todo
    ADD CONSTRAINT todo_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES crm.app_user(id) ON DELETE SET NULL;


--
-- Name: todo_subtask todo_subtask_todo_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.todo_subtask
    ADD CONSTRAINT todo_subtask_todo_id_fkey FOREIGN KEY (todo_id) REFERENCES crm.todo(id) ON DELETE CASCADE;


--
-- Name: training_completion training_completion_app_user_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.training_completion
    ADD CONSTRAINT training_completion_app_user_id_fkey FOREIGN KEY (app_user_id) REFERENCES crm.app_user(id) ON DELETE CASCADE;


--
-- Name: transaction_profile transaction_profile_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.transaction_profile
    ADD CONSTRAINT transaction_profile_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: txn_monitor_event txn_monitor_event_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.txn_monitor_event
    ADD CONSTRAINT txn_monitor_event_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: txn_profile txn_profile_counterparty_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.txn_profile
    ADD CONSTRAINT txn_profile_counterparty_id_fkey FOREIGN KEY (counterparty_id) REFERENCES crm.counterparty(id) ON DELETE CASCADE;


--
-- Name: workout_case workout_case_facility_id_fkey; Type: FK CONSTRAINT; Schema: crm; Owner: -
--

ALTER TABLE ONLY crm.workout_case
    ADD CONSTRAINT workout_case_facility_id_fkey FOREIGN KEY (facility_id) REFERENCES crm.facility(id) ON DELETE CASCADE;


--
-- Name: automation_action aa_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY aa_staff ON crm.automation_action TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: aviso_batch ab_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ab_staff ON crm.aviso_batch TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: account; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.account ENABLE ROW LEVEL SECURITY;

--
-- Name: activity; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.activity ENABLE ROW LEVEL SECURITY;

--
-- Name: activity activity_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY activity_staff ON crm.activity TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: ai_draft; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.ai_draft ENABLE ROW LEVEL SECURITY;

--
-- Name: ai_prompt_log; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.ai_prompt_log ENABLE ROW LEVEL SECURITY;

--
-- Name: ai_draft aid_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY aid_staff ON crm.ai_draft TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: ai_prompt_log ail_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ail_staff ON crm.ai_prompt_log TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: aml_alert ala_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ala_staff ON crm.aml_alert TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: aml_case alc_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY alc_staff ON crm.aml_case TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: aml_dictamen ald_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ald_staff ON crm.aml_dictamen TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: roi_artifact alr_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY alr_staff ON crm.roi_artifact TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: aml_alert; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.aml_alert ENABLE ROW LEVEL SECURITY;

--
-- Name: aml_audit; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.aml_audit ENABLE ROW LEVEL SECURITY;

--
-- Name: aml_audit_item; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.aml_audit_item ENABLE ROW LEVEL SECURITY;

--
-- Name: aml_case; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.aml_case ENABLE ROW LEVEL SECURITY;

--
-- Name: aml_control; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.aml_control ENABLE ROW LEVEL SECURITY;

--
-- Name: aml_control_clause; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.aml_control_clause ENABLE ROW LEVEL SECURITY;

--
-- Name: aml_designation; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.aml_designation ENABLE ROW LEVEL SECURITY;

--
-- Name: aml_dictamen; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.aml_dictamen ENABLE ROW LEVEL SECURITY;

--
-- Name: aml_manual; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.aml_manual ENABLE ROW LEVEL SECURITY;

--
-- Name: aml_rule; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.aml_rule ENABLE ROW LEVEL SECURITY;

--
-- Name: aml_rule aml_rule_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY aml_rule_staff ON crm.aml_rule TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: aml_audit amlaud; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY amlaud ON crm.aml_audit TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: aml_audit_item amlaudi; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY amlaudi ON crm.aml_audit_item TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: aml_control_clause amlcc; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY amlcc ON crm.aml_control_clause TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: aml_control amlctl; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY amlctl ON crm.aml_control TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: aml_designation amldes; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY amldes ON crm.aml_designation TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: aml_manual amlman; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY amlman ON crm.aml_manual TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: training_course amltc; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY amltc ON crm.training_course TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: training_completion amltcomp; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY amltcomp ON crm.training_completion TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: aviso_operation ao_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ao_staff ON crm.aviso_operation TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: app_user; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.app_user ENABLE ROW LEVEL SECURITY;

--
-- Name: automation_recipe ar_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ar_staff ON crm.automation_recipe TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: automation_action; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.automation_action ENABLE ROW LEVEL SECURITY;

--
-- Name: automation_event; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.automation_event ENABLE ROW LEVEL SECURITY;

--
-- Name: automation_event automation_event_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY automation_event_staff ON crm.automation_event TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: automation_recipe; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.automation_recipe ENABLE ROW LEVEL SECURITY;

--
-- Name: automation_run; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.automation_run ENABLE ROW LEVEL SECURITY;

--
-- Name: automation_run automation_run_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY automation_run_staff ON crm.automation_run TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: aviso_batch; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.aviso_batch ENABLE ROW LEVEL SECURITY;

--
-- Name: aviso_operation; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.aviso_operation ENABLE ROW LEVEL SECURITY;

--
-- Name: bulk_action_log bal_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY bal_staff ON crm.bulk_action_log TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: budget_line; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.budget_line ENABLE ROW LEVEL SECURITY;

--
-- Name: bulk_action_log; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.bulk_action_log ENABLE ROW LEVEL SECURITY;

--
-- Name: capital_config; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.capital_config ENABLE ROW LEVEL SECURITY;

--
-- Name: capital_config cc_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY cc_staff ON crm.capital_config TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: change_order; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.change_order ENABLE ROW LEVEL SECURITY;

--
-- Name: change_order change_order_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY change_order_staff ON crm.change_order TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: concentration_cap cl_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY cl_staff ON crm.concentration_cap TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: credit_memo cm_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY cm_staff ON crm.credit_memo TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: company co_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY co_staff ON crm.company TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: collateral; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.collateral ENABLE ROW LEVEL SECURITY;

--
-- Name: collateral_haircut; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.collateral_haircut ENABLE ROW LEVEL SECURITY;

--
-- Name: collateral_haircut collateral_haircut_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY collateral_haircut_staff ON crm.collateral_haircut TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: collateral collateral_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY collateral_staff ON crm.collateral TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: company_merge_log com_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY com_staff ON crm.company_merge_log TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: comms_identity; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.comms_identity ENABLE ROW LEVEL SECURITY;

--
-- Name: comms_identity comms_identity_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY comms_identity_staff ON crm.comms_identity TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: comms_outbox; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.comms_outbox ENABLE ROW LEVEL SECURITY;

--
-- Name: comms_outbox comms_outbox_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY comms_outbox_staff ON crm.comms_outbox TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: company; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.company ENABLE ROW LEVEL SECURITY;

--
-- Name: company_merge_log; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.company_merge_log ENABLE ROW LEVEL SECURITY;

--
-- Name: company_relationship; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.company_relationship ENABLE ROW LEVEL SECURITY;

--
-- Name: concentration_limit conc_limit_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY conc_limit_staff ON crm.concentration_limit TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: concentration_cap; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.concentration_cap ENABLE ROW LEVEL SECURITY;

--
-- Name: concentration_limit; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.concentration_limit ENABLE ROW LEVEL SECURITY;

--
-- Name: contact; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.contact ENABLE ROW LEVEL SECURITY;

--
-- Name: contact_enrich; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.contact_enrich ENABLE ROW LEVEL SECURITY;

--
-- Name: contact_enrich contact_enrich_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY contact_enrich_staff ON crm.contact_enrich TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: contact_field; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.contact_field ENABLE ROW LEVEL SECURITY;

--
-- Name: contact contact_owner_rls; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY contact_owner_rls ON crm.contact TO authenticated USING ((crm.is_admin() OR (owner_id = crm.my_app_user_id()))) WITH CHECK ((crm.is_admin() OR (owner_id = crm.my_app_user_id()) OR (owner_id IS NULL)));


--
-- Name: company_relationship cor_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY cor_staff ON crm.company_relationship TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: counterparty; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.counterparty ENABLE ROW LEVEL SECURITY;

--
-- Name: covenant_test cov_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY cov_staff ON crm.covenant_test TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: covenant_test; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.covenant_test ENABLE ROW LEVEL SECURITY;

--
-- Name: coverage_covenant; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.coverage_covenant ENABLE ROW LEVEL SECURITY;

--
-- Name: coverage_ratio; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.coverage_ratio ENABLE ROW LEVEL SECURITY;

--
-- Name: cp_item; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.cp_item ENABLE ROW LEVEL SECURITY;

--
-- Name: cp_item cp_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY cp_staff ON crm.cp_item TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: credit_memo; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.credit_memo ENABLE ROW LEVEL SECURITY;

--
-- Name: credit_sanction; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.credit_sanction ENABLE ROW LEVEL SECURITY;

--
-- Name: account crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.account TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: app_user crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.app_user TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: budget_line crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.budget_line TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: contact_field crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.contact_field TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: counterparty crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.counterparty TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: dd_check crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.dd_check TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: dd_decision crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.dd_decision TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: dd_screening_hit crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.dd_screening_hit TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: dd_ubo crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.dd_ubo TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: deal_attachment crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.deal_attachment TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: deal_comment crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.deal_comment TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: deal_event crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.deal_event TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: deal_financials crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.deal_financials TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: deal_line_item crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.deal_line_item TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: deal_rpu crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.deal_rpu TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: expense crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.expense TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: huddle_run crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.huddle_run TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: invoice crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.invoice TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: ops_report crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.ops_report TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: quote crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.quote TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: todo crm_staff_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY crm_staff_all ON crm.todo TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: credit_sanction cs_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY cs_staff ON crm.credit_sanction TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: coverage_covenant cvc_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY cvc_staff ON crm.coverage_covenant TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: coverage_ratio cvr_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY cvr_staff ON crm.coverage_ratio TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: dashboard dash_rw; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY dash_rw ON crm.dashboard TO authenticated USING (((owner_email = (auth.jwt() ->> 'email'::text)) OR shared)) WITH CHECK ((owner_email = (auth.jwt() ->> 'email'::text)));


--
-- Name: dashboard; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.dashboard ENABLE ROW LEVEL SECURITY;

--
-- Name: dlp_clock dc_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY dc_staff ON crm.dlp_clock TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: dd_aviso; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.dd_aviso ENABLE ROW LEVEL SECURITY;

--
-- Name: dd_aviso dd_aviso_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY dd_aviso_staff ON crm.dd_aviso TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: dd_check; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.dd_check ENABLE ROW LEVEL SECURITY;

--
-- Name: dd_consent; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.dd_consent ENABLE ROW LEVEL SECURITY;

--
-- Name: dd_consent dd_consent_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY dd_consent_staff ON crm.dd_consent TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: dd_decision; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.dd_decision ENABLE ROW LEVEL SECURITY;

--
-- Name: dd_lpb; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.dd_lpb ENABLE ROW LEVEL SECURITY;

--
-- Name: dd_lpb dd_lpb_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY dd_lpb_staff ON crm.dd_lpb TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: dd_operation; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.dd_operation ENABLE ROW LEVEL SECURITY;

--
-- Name: dd_operation dd_operation_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY dd_operation_staff ON crm.dd_operation TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: dd_ownership_edge; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.dd_ownership_edge ENABLE ROW LEVEL SECURITY;

--
-- Name: dd_ownership_node; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.dd_ownership_node ENABLE ROW LEVEL SECURITY;

--
-- Name: dd_screening_hit; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.dd_screening_hit ENABLE ROW LEVEL SECURITY;

--
-- Name: dlp_defect dd_staff2; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY dd_staff2 ON crm.dlp_defect TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: dd_ubo; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.dd_ubo ENABLE ROW LEVEL SECURITY;

--
-- Name: dd_ubo_document; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.dd_ubo_document ENABLE ROW LEVEL SECURITY;

--
-- Name: deal; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.deal ENABLE ROW LEVEL SECURITY;

--
-- Name: deal_attachment; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.deal_attachment ENABLE ROW LEVEL SECURITY;

--
-- Name: deal_comment; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.deal_comment ENABLE ROW LEVEL SECURITY;

--
-- Name: deal_event; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.deal_event ENABLE ROW LEVEL SECURITY;

--
-- Name: deal_financials; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.deal_financials ENABLE ROW LEVEL SECURITY;

--
-- Name: deal_line_item; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.deal_line_item ENABLE ROW LEVEL SECURITY;

--
-- Name: deal deal_owner_rls; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY deal_owner_rls ON crm.deal TO authenticated USING ((crm.is_admin() OR (owner_id = crm.my_app_user_id()))) WITH CHECK ((crm.is_admin() OR (owner_id = crm.my_app_user_id()) OR (owner_id IS NULL)));


--
-- Name: deal_rpu; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.deal_rpu ENABLE ROW LEVEL SECURITY;

--
-- Name: delegated_authority; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.delegated_authority ENABLE ROW LEVEL SECURITY;

--
-- Name: delegated_authority delegated_authority_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY delegated_authority_staff ON crm.delegated_authority TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: dlp_clock; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.dlp_clock ENABLE ROW LEVEL SECURITY;

--
-- Name: dlp_defect; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.dlp_defect ENABLE ROW LEVEL SECURITY;

--
-- Name: email_account ea_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ea_staff ON crm.email_account TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: ebr_factor; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.ebr_factor ENABLE ROW LEVEL SECURITY;

--
-- Name: ebr_factor ebr_factor_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ebr_factor_staff ON crm.ebr_factor TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: ebr_rating; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.ebr_rating ENABLE ROW LEVEL SECURITY;

--
-- Name: ebr_rating ebr_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ebr_staff ON crm.ebr_rating TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: ecl_run; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.ecl_run ENABLE ROW LEVEL SECURITY;

--
-- Name: edd_item; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.edd_item ENABLE ROW LEVEL SECURITY;

--
-- Name: edd_item edd_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY edd_staff ON crm.edd_item TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: efos_69b; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.efos_69b ENABLE ROW LEVEL SECURITY;

--
-- Name: efos_69b efos_69b_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY efos_69b_staff ON crm.efos_69b TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: email_account; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.email_account ENABLE ROW LEVEL SECURITY;

--
-- Name: email_template; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.email_template ENABLE ROW LEVEL SECURITY;

--
-- Name: email_tracking; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.email_tracking ENABLE ROW LEVEL SECURITY;

--
-- Name: ecl_run er_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY er_staff ON crm.ecl_run TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: email_template et_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY et_staff ON crm.email_template TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: email_tracking etr_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY etr_staff ON crm.email_tracking TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: expense; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.expense ENABLE ROW LEVEL SECURITY;

--
-- Name: facility; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.facility ENABLE ROW LEVEL SECURITY;

--
-- Name: facility_base_case; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.facility_base_case ENABLE ROW LEVEL SECURITY;

--
-- Name: facility_scenario_ecl; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.facility_scenario_ecl ENABLE ROW LEVEL SECURITY;

--
-- Name: facility_schedule; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.facility_schedule ENABLE ROW LEVEL SECURITY;

--
-- Name: facility_schedule facility_schedule_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY facility_schedule_staff ON crm.facility_schedule TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: facility facility_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY facility_staff ON crm.facility TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: facility_base_case fbc_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY fbc_staff ON crm.facility_base_case TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: field_capture fc_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY fc_staff ON crm.field_capture TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: forbearance_event fe_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY fe_staff ON crm.forbearance_event TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: field_capture; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.field_capture ENABLE ROW LEVEL SECURITY;

--
-- Name: forbearance_event; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.forbearance_event ENABLE ROW LEVEL SECURITY;

--
-- Name: facility_scenario_ecl fse_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY fse_staff ON crm.facility_scenario_ecl TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: generation_actual ga_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ga_staff ON crm.generation_actual TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: generation_baseline gb_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY gb_staff ON crm.generation_baseline TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: generation_actual; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.generation_actual ENABLE ROW LEVEL SECURITY;

--
-- Name: generation_baseline; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.generation_baseline ENABLE ROW LEVEL SECURITY;

--
-- Name: goods_receipt; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.goods_receipt ENABLE ROW LEVEL SECURITY;

--
-- Name: goods_receipt goods_receipt_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY goods_receipt_staff ON crm.goods_receipt TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: huddle_run; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.huddle_run ENABLE ROW LEVEL SECURITY;

--
-- Name: huddle_run huddle_run_newman_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY huddle_run_newman_all ON crm.huddle_run TO authenticated USING (crm.is_newman()) WITH CHECK (crm.is_newman());


--
-- Name: inspection insp_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY insp_staff ON crm.inspection TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: inspection; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.inspection ENABLE ROW LEVEL SECURITY;

--
-- Name: invoice; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.invoice ENABLE ROW LEVEL SECURITY;

--
-- Name: itp_item; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.itp_item ENABLE ROW LEVEL SECURITY;

--
-- Name: itp_item itp_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY itp_staff ON crm.itp_item TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: limit_breach lb_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY lb_staff ON crm.limit_breach TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: ld_accrual; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.ld_accrual ENABLE ROW LEVEL SECURITY;

--
-- Name: ld_accrual ld_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ld_staff ON crm.ld_accrual TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: lgd_realization; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.lgd_realization ENABLE ROW LEVEL SECURITY;

--
-- Name: limit_breach; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.limit_breach ENABLE ROW LEVEL SECURITY;

--
-- Name: lgd_realization lr_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY lr_staff ON crm.lgd_realization TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: macro_scenario; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.macro_scenario ENABLE ROW LEVEL SECURITY;

--
-- Name: macro_scenario_set; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.macro_scenario_set ENABLE ROW LEVEL SECURITY;

--
-- Name: macro_scenario ms_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ms_staff ON crm.macro_scenario TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: macro_scenario_set mss_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY mss_staff ON crm.macro_scenario_set TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: notification; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.notification ENABLE ROW LEVEL SECURITY;

--
-- Name: notification notification_own; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY notification_own ON crm.notification TO authenticated USING ((recipient_email = (auth.jwt() ->> 'email'::text))) WITH CHECK ((recipient_email = (auth.jwt() ->> 'email'::text)));


--
-- Name: operacion_relevante; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.operacion_relevante ENABLE ROW LEVEL SECURITY;

--
-- Name: ops_report; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.ops_report ENABLE ROW LEVEL SECURITY;

--
-- Name: operacion_relevante or_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY or_staff ON crm.operacion_relevante TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: dd_ownership_edge own_edge_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY own_edge_staff ON crm.dd_ownership_edge TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: dd_ownership_node own_node_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY own_node_staff ON crm.dd_ownership_node TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: performance_backcharge pbc_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY pbc_staff ON crm.performance_backcharge TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: progress_claim pc_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY pc_staff ON crm.progress_claim TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: pd_rating; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.pd_rating ENABLE ROW LEVEL SECURITY;

--
-- Name: pd_scorecard_factor; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.pd_scorecard_factor ENABLE ROW LEVEL SECURITY;

--
-- Name: pd_scorecard_factor pd_scorecard_factor_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY pd_scorecard_factor_staff ON crm.pd_scorecard_factor TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: pd_term_structure; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.pd_term_structure ENABLE ROW LEVEL SECURITY;

--
-- Name: pd_rating pdr_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY pdr_staff ON crm.pd_rating TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: pd_term_structure pdt_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY pdt_staff ON crm.pd_term_structure TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: performance_backcharge; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.performance_backcharge ENABLE ROW LEVEL SECURITY;

--
-- Name: po_invoice; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.po_invoice ENABLE ROW LEVEL SECURITY;

--
-- Name: po_invoice po_invoice_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY po_invoice_staff ON crm.po_invoice TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: proposal pr_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY pr_staff ON crm.proposal TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: proposal_event pre_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY pre_staff ON crm.proposal_event TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: proposal_line prl_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY prl_staff ON crm.proposal_line TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: progress_claim; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.progress_claim ENABLE ROW LEVEL SECURITY;

--
-- Name: project; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.project ENABLE ROW LEVEL SECURITY;

--
-- Name: project_cost; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.project_cost ENABLE ROW LEVEL SECURITY;

--
-- Name: project_cost project_cost_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY project_cost_staff ON crm.project_cost TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: project_milestone; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.project_milestone ENABLE ROW LEVEL SECURITY;

--
-- Name: project_milestone project_ms_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY project_ms_staff ON crm.project_milestone TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: project project_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY project_staff ON crm.project TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: proposal; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.proposal ENABLE ROW LEVEL SECURITY;

--
-- Name: proposal_event; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.proposal_event ENABLE ROW LEVEL SECURITY;

--
-- Name: proposal_line; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.proposal_line ENABLE ROW LEVEL SECURITY;

--
-- Name: proposal_signature; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.proposal_signature ENABLE ROW LEVEL SECURITY;

--
-- Name: proposal_signature prs_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY prs_staff ON crm.proposal_signature TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: push_subscription ps_own; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ps_own ON crm.push_subscription TO authenticated USING ((owner_email = (auth.jwt() ->> 'email'::text))) WITH CHECK ((owner_email = (auth.jwt() ->> 'email'::text)));


--
-- Name: purchase_order; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.purchase_order ENABLE ROW LEVEL SECURITY;

--
-- Name: purchase_order purchase_order_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY purchase_order_staff ON crm.purchase_order TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: push_subscription; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.push_subscription ENABLE ROW LEVEL SECURITY;

--
-- Name: quote; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.quote ENABLE ROW LEVEL SECURITY;

--
-- Name: raroc_assessment ra_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ra_staff ON crm.raroc_assessment TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: raroc_assessment; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.raroc_assessment ENABLE ROW LEVEL SECURITY;

--
-- Name: recovery_posting; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.recovery_posting ENABLE ROW LEVEL SECURITY;

--
-- Name: reforecast; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.reforecast ENABLE ROW LEVEL SECURITY;

--
-- Name: repayment; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.repayment ENABLE ROW LEVEL SECURITY;

--
-- Name: repayment repayment_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY repayment_staff ON crm.repayment TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: retention_ledger ret_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ret_staff ON crm.retention_ledger TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: retention_ledger; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.retention_ledger ENABLE ROW LEVEL SECURITY;

--
-- Name: reforecast rf_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY rf_staff ON crm.reforecast TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: roi_artifact; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.roi_artifact ENABLE ROW LEVEL SECURITY;

--
-- Name: recovery_posting rp_staff2; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY rp_staff2 ON crm.recovery_posting TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: schedule_activity sa_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY sa_staff ON crm.schedule_activity TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: sales_target; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.sales_target ENABLE ROW LEVEL SECURITY;

--
-- Name: sanction_override; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.sanction_override ENABLE ROW LEVEL SECURITY;

--
-- Name: sanctions_entry; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.sanctions_entry ENABLE ROW LEVEL SECURITY;

--
-- Name: sanctions_entry sanctions_entry_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY sanctions_entry_staff ON crm.sanctions_entry TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: saved_view; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.saved_view ENABLE ROW LEVEL SECURITY;

--
-- Name: saved_view saved_view_read; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY saved_view_read ON crm.saved_view FOR SELECT TO authenticated USING (((crm.my_role() IS NOT NULL) AND (is_shared OR (owner_email = (auth.jwt() ->> 'email'::text)))));


--
-- Name: saved_view saved_view_write; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY saved_view_write ON crm.saved_view TO authenticated USING ((owner_email = (auth.jwt() ->> 'email'::text))) WITH CHECK ((owner_email = (auth.jwt() ->> 'email'::text)));


--
-- Name: sub_back_charge sbc_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY sbc_staff ON crm.sub_back_charge TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: schedule_baseline sbl_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY sbl_staff ON crm.schedule_baseline TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: schedule_activity; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.schedule_activity ENABLE ROW LEVEL SECURITY;

--
-- Name: schedule_baseline; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.schedule_baseline ENABLE ROW LEVEL SECURITY;

--
-- Name: schedule_dependency; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.schedule_dependency ENABLE ROW LEVEL SECURITY;

--
-- Name: schedule_forecast; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.schedule_forecast ENABLE ROW LEVEL SECURITY;

--
-- Name: screening_list_version; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.screening_list_version ENABLE ROW LEVEL SECURITY;

--
-- Name: screening_provenance; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.screening_provenance ENABLE ROW LEVEL SECURITY;

--
-- Name: schedule_dependency sd_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY sd_staff ON crm.schedule_dependency TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: sequence_enrollment se_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY se_staff ON crm.sequence_enrollment TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: sequence; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.sequence ENABLE ROW LEVEL SECURITY;

--
-- Name: sequence_enrollment; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.sequence_enrollment ENABLE ROW LEVEL SECURITY;

--
-- Name: sequence_step; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.sequence_step ENABLE ROW LEVEL SECURITY;

--
-- Name: schedule_forecast sf_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY sf_staff ON crm.schedule_forecast TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: screening_list_version slv_read; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY slv_read ON crm.screening_list_version FOR SELECT TO authenticated USING ((crm.my_role() IS NOT NULL));


--
-- Name: sanction_override so_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY so_staff ON crm.sanction_override TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: screening_provenance sp_read; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY sp_read ON crm.screening_provenance FOR SELECT TO authenticated USING ((crm.my_role() IS NOT NULL));


--
-- Name: sub_payment_claim spc_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY spc_staff ON crm.sub_payment_claim TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: sequence sq_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY sq_staff ON crm.sequence TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: sub_retention_ledger srl_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY srl_staff ON crm.sub_retention_ledger TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: sequence_step ss_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ss_staff ON crm.sequence_step TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: sales_target st_read; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY st_read ON crm.sales_target FOR SELECT TO authenticated USING ((crm.my_role() IS NOT NULL));


--
-- Name: sales_target st_write; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY st_write ON crm.sales_target TO authenticated USING (crm.is_approver()) WITH CHECK (crm.is_approver());


--
-- Name: stage_probability; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.stage_probability ENABLE ROW LEVEL SECURITY;

--
-- Name: stage_probability stageprob_read; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY stageprob_read ON crm.stage_probability FOR SELECT TO authenticated USING ((crm.my_role() IS NOT NULL));


--
-- Name: stage_probability stageprob_write; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY stageprob_write ON crm.stage_probability TO authenticated USING (crm.is_approver()) WITH CHECK (crm.is_approver());


--
-- Name: sub_back_charge; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.sub_back_charge ENABLE ROW LEVEL SECURITY;

--
-- Name: sub_payment_claim; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.sub_payment_claim ENABLE ROW LEVEL SECURITY;

--
-- Name: sub_retention_ledger; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.sub_retention_ledger ENABLE ROW LEVEL SECURITY;

--
-- Name: subcontract sub_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY sub_staff ON crm.subcontract TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: subcontract; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.subcontract ENABLE ROW LEVEL SECURITY;

--
-- Name: sync_state; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.sync_state ENABLE ROW LEVEL SECURITY;

--
-- Name: sync_state sync_state_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY sync_state_staff ON crm.sync_state TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: task; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.task ENABLE ROW LEVEL SECURITY;

--
-- Name: task task_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY task_staff ON crm.task TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: txn_monitor_event tme_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY tme_staff ON crm.txn_monitor_event TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: todo; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.todo ENABLE ROW LEVEL SECURITY;

--
-- Name: todo todo_newman_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY todo_newman_all ON crm.todo TO authenticated USING (crm.is_newman()) WITH CHECK (crm.is_newman());


--
-- Name: todo_subtask; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.todo_subtask ENABLE ROW LEVEL SECURITY;

--
-- Name: todo_subtask todo_subtask_authenticated_all; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY todo_subtask_authenticated_all ON crm.todo_subtask TO authenticated USING (true) WITH CHECK (true);


--
-- Name: transaction_profile tp_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY tp_staff ON crm.transaction_profile TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: txn_profile tp_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY tp_staff ON crm.txn_profile TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: training_completion; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.training_completion ENABLE ROW LEVEL SECURITY;

--
-- Name: training_course; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.training_course ENABLE ROW LEVEL SECURITY;

--
-- Name: transaction_profile; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.transaction_profile ENABLE ROW LEVEL SECURITY;

--
-- Name: txn_monitor_event; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.txn_monitor_event ENABLE ROW LEVEL SECURITY;

--
-- Name: txn_profile; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.txn_profile ENABLE ROW LEVEL SECURITY;

--
-- Name: dd_ubo_document ubo_doc_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY ubo_doc_staff ON crm.dd_ubo_document TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: uma_config uc_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY uc_staff ON crm.uma_config TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: uma_config; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.uma_config ENABLE ROW LEVEL SECURITY;

--
-- Name: workout_case wc_staff; Type: POLICY; Schema: crm; Owner: -
--

CREATE POLICY wc_staff ON crm.workout_case TO authenticated USING ((crm.my_role() IS NOT NULL)) WITH CHECK ((crm.my_role() IS NOT NULL));


--
-- Name: workout_case; Type: ROW SECURITY; Schema: crm; Owner: -
--

ALTER TABLE crm.workout_case ENABLE ROW LEVEL SECURITY;

--
-- PostgreSQL database dump complete
--

\unrestrict bHMvRlOVdsRvAhzdxbyRECFHA7uEGz9i7XVJ9dUtFhgUjeXtWVnSb24jIUNKyY2

