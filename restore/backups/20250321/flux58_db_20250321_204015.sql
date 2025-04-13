--
-- PostgreSQL database dump
--

-- Dumped from database version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.8 (Ubuntu 16.8-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: assets; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.assets (
    id text NOT NULL,
    project_id text NOT NULL,
    name text NOT NULL,
    path text NOT NULL,
    type text NOT NULL,
    created_at timestamp without time zone NOT NULL,
    metadata jsonb
);


ALTER TABLE public.assets OWNER TO flux58_user;

--
-- Name: clips; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.clips (
    id text NOT NULL,
    project_id text NOT NULL,
    asset_id text NOT NULL,
    track_id integer NOT NULL,
    "position" double precision NOT NULL,
    duration double precision NOT NULL,
    created_at timestamp without time zone NOT NULL,
    properties jsonb
);


ALTER TABLE public.clips OWNER TO flux58_user;

--
-- Name: credit_transactions; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.credit_transactions (
    id character varying(36) NOT NULL,
    user_id character varying(36) NOT NULL,
    amount integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    type character varying(50) NOT NULL,
    description text,
    status character varying(50) NOT NULL
);


ALTER TABLE public.credit_transactions OWNER TO flux58_user;

--
-- Name: credits; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.credits (
    user_id character varying(36) NOT NULL,
    total integer NOT NULL,
    used integer NOT NULL
);


ALTER TABLE public.credits OWNER TO flux58_user;

--
-- Name: export_jobs; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.export_jobs (
    id text NOT NULL,
    project_id text NOT NULL,
    user_id text NOT NULL,
    output_path text,
    format text NOT NULL,
    width integer NOT NULL,
    height integer NOT NULL,
    fps double precision NOT NULL,
    video_bitrate text,
    audio_bitrate text,
    start_frame integer,
    end_frame integer,
    started_at timestamp without time zone NOT NULL,
    completed_at timestamp without time zone,
    status text NOT NULL,
    error_message text,
    progress double precision DEFAULT 0.0,
    priority integer DEFAULT 0
);


ALTER TABLE public.export_jobs OWNER TO flux58_user;

--
-- Name: logs; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.logs (
    id integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    level text NOT NULL,
    module text,
    message text NOT NULL,
    user_id text,
    ip_address text,
    details jsonb,
    context jsonb
);


ALTER TABLE public.logs OWNER TO flux58_user;

--
-- Name: logs_id_seq; Type: SEQUENCE; Schema: public; Owner: flux58_user
--

CREATE SEQUENCE public.logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.logs_id_seq OWNER TO flux58_user;

--
-- Name: logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: flux58_user
--

ALTER SEQUENCE public.logs_id_seq OWNED BY public.logs.id;


--
-- Name: project_assets; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.project_assets (
    id character varying(36) NOT NULL,
    project_id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    filename character varying(255) NOT NULL,
    path text NOT NULL,
    type character varying(50) NOT NULL,
    added_at timestamp without time zone NOT NULL
);


ALTER TABLE public.project_assets OWNER TO flux58_user;

--
-- Name: project_timeline; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.project_timeline (
    project_id character varying(36) NOT NULL,
    duration real NOT NULL,
    width integer NOT NULL,
    height integer NOT NULL,
    fps_num integer NOT NULL,
    fps_den integer NOT NULL,
    sample_rate integer NOT NULL,
    channels integer NOT NULL,
    channel_layout integer NOT NULL
);


ALTER TABLE public.project_timeline OWNER TO flux58_user;

--
-- Name: projects; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.projects (
    id text NOT NULL,
    user_id text NOT NULL,
    name text NOT NULL,
    description text,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    settings jsonb
);


ALTER TABLE public.projects OWNER TO flux58_user;

--
-- Name: sessions; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.sessions (
    token text NOT NULL,
    user_id text NOT NULL,
    username text NOT NULL,
    created_at timestamp without time zone NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    ip_address text,
    user_agent text,
    last_activity timestamp without time zone
);


ALTER TABLE public.sessions OWNER TO flux58_user;

--
-- Name: system_logs; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.system_logs (
    id integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    level character varying(20) NOT NULL,
    module character varying(100) NOT NULL,
    message text NOT NULL,
    user_id character varying(36),
    ip_address character varying(50)
);


ALTER TABLE public.system_logs OWNER TO flux58_user;

--
-- Name: system_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: flux58_user
--

CREATE SEQUENCE public.system_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.system_logs_id_seq OWNER TO flux58_user;

--
-- Name: system_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: flux58_user
--

ALTER SEQUENCE public.system_logs_id_seq OWNED BY public.system_logs.id;


--
-- Name: system_settings; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.system_settings (
    key text NOT NULL,
    value text NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.system_settings OWNER TO flux58_user;

--
-- Name: timeline_clips; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.timeline_clips (
    id character varying(36) NOT NULL,
    track_id character varying(36) NOT NULL,
    asset_id character varying(36) NOT NULL,
    "position" real NOT NULL,
    duration real NOT NULL,
    start_point real NOT NULL,
    end_point real NOT NULL,
    properties jsonb NOT NULL
);


ALTER TABLE public.timeline_clips OWNER TO flux58_user;

--
-- Name: timeline_tracks; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.timeline_tracks (
    id character varying(36) NOT NULL,
    project_id character varying(36) NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.timeline_tracks OWNER TO flux58_user;

--
-- Name: user_credits; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.user_credits (
    id text NOT NULL,
    user_id text NOT NULL,
    amount integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    description text,
    type text NOT NULL,
    reference_id text,
    status text NOT NULL
);


ALTER TABLE public.user_credits OWNER TO flux58_user;

--
-- Name: users; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.users (
    id text NOT NULL,
    username text NOT NULL,
    password_hash text NOT NULL,
    email text NOT NULL,
    created_at timestamp without time zone NOT NULL,
    role text NOT NULL
);


ALTER TABLE public.users OWNER TO flux58_user;

--
-- Name: logs id; Type: DEFAULT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.logs ALTER COLUMN id SET DEFAULT nextval('public.logs_id_seq'::regclass);


--
-- Name: system_logs id; Type: DEFAULT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.system_logs ALTER COLUMN id SET DEFAULT nextval('public.system_logs_id_seq'::regclass);


--
-- Data for Name: assets; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.assets (id, project_id, name, path, type, created_at, metadata) FROM stdin;
\.


--
-- Data for Name: clips; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.clips (id, project_id, asset_id, track_id, "position", duration, created_at, properties) FROM stdin;
\.


--
-- Data for Name: credit_transactions; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.credit_transactions (id, user_id, amount, "timestamp", type, description, status) FROM stdin;
\.


--
-- Data for Name: credits; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.credits (user_id, total, used) FROM stdin;
\.


--
-- Data for Name: export_jobs; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.export_jobs (id, project_id, user_id, output_path, format, width, height, fps, video_bitrate, audio_bitrate, start_frame, end_frame, started_at, completed_at, status, error_message, progress, priority) FROM stdin;
\.


--
-- Data for Name: logs; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.logs (id, "timestamp", level, module, message, user_id, ip_address, details, context) FROM stdin;
\.


--
-- Data for Name: project_assets; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.project_assets (id, project_id, name, filename, path, type, added_at) FROM stdin;
\.


--
-- Data for Name: project_timeline; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.project_timeline (project_id, duration, width, height, fps_num, fps_den, sample_rate, channels, channel_layout) FROM stdin;
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.projects (id, user_id, name, description, created_at, updated_at, settings) FROM stdin;
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.sessions (token, user_id, username, created_at, expires_at, ip_address, user_agent, last_activity) FROM stdin;
\.


--
-- Data for Name: system_logs; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.system_logs (id, "timestamp", level, module, message, user_id, ip_address) FROM stdin;
1	2025-03-21 20:33:23.594197	INFO	app	Application starting	\N	\N
2	2025-03-21 20:33:23.923429	INFO	app	Application starting	\N	\N
3	2025-03-21 20:33:26.486379	INFO	app	Application starting	\N	\N
4	2025-03-21 20:33:26.864156	INFO	app	Application starting	\N	\N
\.


--
-- Data for Name: system_settings; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.system_settings (key, value, updated_at) FROM stdin;
navbar_brand_text	FLUX58 AI MEDIA LABS	2025-03-21 20:35:17.647769
navbar_bg_color	#212529	2025-03-21 20:35:17.661745
navbar_text_color	#000000	2025-03-21 20:35:17.664462
\.


--
-- Data for Name: timeline_clips; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.timeline_clips (id, track_id, asset_id, "position", duration, start_point, end_point, properties) FROM stdin;
\.


--
-- Data for Name: timeline_tracks; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.timeline_tracks (id, project_id, name) FROM stdin;
\.


--
-- Data for Name: user_credits; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.user_credits (id, user_id, amount, "timestamp", description, type, reference_id, status) FROM stdin;
21f560cc-07bc-4d56-b8e9-71a1b6a7be01	b3c6bccc-453a-43fd-b16e-1985cb21f22f	9999	2025-03-21 20:33:20.551835	Admin account setup	initial	\N	completed
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.users (id, username, password_hash, email, created_at, role) FROM stdin;
b3c6bccc-453a-43fd-b16e-1985cb21f22f	admin	scrypt:32768:8:1$shAp4gOLNrT7qeps$5ef76356a53758127e55d37757a95ce0a57a2c50728a6b1c29f4e18ec5aaf24a6f62504644a7b6455f2346c3a2154b693f8a8625377aabe53f803626242f25a3	admin@flux58.com	2025-03-21 20:33:20.551835	admin
\.


--
-- Name: logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: flux58_user
--

SELECT pg_catalog.setval('public.logs_id_seq', 1, false);


--
-- Name: system_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: flux58_user
--

SELECT pg_catalog.setval('public.system_logs_id_seq', 4, true);


--
-- Name: assets assets_pkey; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (id);


--
-- Name: clips clips_pkey; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.clips
    ADD CONSTRAINT clips_pkey PRIMARY KEY (id);


--
-- Name: credit_transactions credit_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.credit_transactions
    ADD CONSTRAINT credit_transactions_pkey PRIMARY KEY (id);


--
-- Name: credits credits_pkey; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.credits
    ADD CONSTRAINT credits_pkey PRIMARY KEY (user_id);


--
-- Name: export_jobs export_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.export_jobs
    ADD CONSTRAINT export_jobs_pkey PRIMARY KEY (id);


--
-- Name: logs logs_pkey; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.logs
    ADD CONSTRAINT logs_pkey PRIMARY KEY (id);


--
-- Name: project_assets project_assets_pkey; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.project_assets
    ADD CONSTRAINT project_assets_pkey PRIMARY KEY (id);


--
-- Name: project_timeline project_timeline_pkey; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.project_timeline
    ADD CONSTRAINT project_timeline_pkey PRIMARY KEY (project_id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (token);


--
-- Name: system_logs system_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.system_logs
    ADD CONSTRAINT system_logs_pkey PRIMARY KEY (id);


--
-- Name: system_settings system_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_pkey PRIMARY KEY (key);


--
-- Name: timeline_clips timeline_clips_pkey; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.timeline_clips
    ADD CONSTRAINT timeline_clips_pkey PRIMARY KEY (id);


--
-- Name: timeline_tracks timeline_tracks_pkey; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.timeline_tracks
    ADD CONSTRAINT timeline_tracks_pkey PRIMARY KEY (id);


--
-- Name: user_credits user_credits_pkey; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.user_credits
    ADD CONSTRAINT user_credits_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_assets_project_id; Type: INDEX; Schema: public; Owner: flux58_user
--

CREATE INDEX idx_assets_project_id ON public.project_assets USING btree (project_id);


--
-- Name: idx_assets_type; Type: INDEX; Schema: public; Owner: flux58_user
--

CREATE INDEX idx_assets_type ON public.project_assets USING btree (type);


--
-- Name: idx_clips_asset_id; Type: INDEX; Schema: public; Owner: flux58_user
--

CREATE INDEX idx_clips_asset_id ON public.timeline_clips USING btree (asset_id);


--
-- Name: idx_clips_track_id; Type: INDEX; Schema: public; Owner: flux58_user
--

CREATE INDEX idx_clips_track_id ON public.timeline_clips USING btree (track_id);


--
-- Name: idx_exports_priority; Type: INDEX; Schema: public; Owner: flux58_user
--

CREATE INDEX idx_exports_priority ON public.export_jobs USING btree (priority DESC);


--
-- Name: idx_exports_status; Type: INDEX; Schema: public; Owner: flux58_user
--

CREATE INDEX idx_exports_status ON public.export_jobs USING btree (status);


--
-- Name: idx_exports_user_started; Type: INDEX; Schema: public; Owner: flux58_user
--

CREATE INDEX idx_exports_user_started ON public.export_jobs USING btree (user_id, started_at DESC);


--
-- Name: idx_logs_level; Type: INDEX; Schema: public; Owner: flux58_user
--

CREATE INDEX idx_logs_level ON public.system_logs USING btree (level);


--
-- Name: idx_logs_timestamp; Type: INDEX; Schema: public; Owner: flux58_user
--

CREATE INDEX idx_logs_timestamp ON public.system_logs USING btree ("timestamp" DESC);


--
-- Name: idx_projects_user_updated; Type: INDEX; Schema: public; Owner: flux58_user
--

CREATE INDEX idx_projects_user_updated ON public.projects USING btree (user_id, updated_at DESC);


--
-- Name: idx_sessions_expires_at; Type: INDEX; Schema: public; Owner: flux58_user
--

CREATE INDEX idx_sessions_expires_at ON public.sessions USING btree (expires_at);


--
-- Name: idx_sessions_user_id; Type: INDEX; Schema: public; Owner: flux58_user
--

CREATE INDEX idx_sessions_user_id ON public.sessions USING btree (user_id);


--
-- Name: idx_tracks_project_id; Type: INDEX; Schema: public; Owner: flux58_user
--

CREATE INDEX idx_tracks_project_id ON public.timeline_tracks USING btree (project_id);


--
-- Name: idx_transactions_user_timestamp; Type: INDEX; Schema: public; Owner: flux58_user
--

CREATE INDEX idx_transactions_user_timestamp ON public.credit_transactions USING btree (user_id, "timestamp" DESC);


--
-- Name: assets assets_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: clips clips_asset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.clips
    ADD CONSTRAINT clips_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.assets(id) ON DELETE CASCADE;


--
-- Name: clips clips_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.clips
    ADD CONSTRAINT clips_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: credit_transactions credit_transactions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.credit_transactions
    ADD CONSTRAINT credit_transactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: credits credits_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.credits
    ADD CONSTRAINT credits_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: export_jobs export_jobs_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.export_jobs
    ADD CONSTRAINT export_jobs_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: export_jobs export_jobs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.export_jobs
    ADD CONSTRAINT export_jobs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: project_assets project_assets_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.project_assets
    ADD CONSTRAINT project_assets_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: project_timeline project_timeline_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.project_timeline
    ADD CONSTRAINT project_timeline_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: projects projects_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: sessions sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: system_logs system_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.system_logs
    ADD CONSTRAINT system_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: timeline_clips timeline_clips_asset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.timeline_clips
    ADD CONSTRAINT timeline_clips_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.project_assets(id) ON DELETE CASCADE;


--
-- Name: timeline_clips timeline_clips_track_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.timeline_clips
    ADD CONSTRAINT timeline_clips_track_id_fkey FOREIGN KEY (track_id) REFERENCES public.timeline_tracks(id) ON DELETE CASCADE;


--
-- Name: timeline_tracks timeline_tracks_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.timeline_tracks
    ADD CONSTRAINT timeline_tracks_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: user_credits user_credits_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.user_credits
    ADD CONSTRAINT user_credits_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO flux58_user;


--
-- PostgreSQL database dump complete
--

