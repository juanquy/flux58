--
-- PostgreSQL database dump
--

-- Dumped from database version 12.22 (Ubuntu 12.22-0ubuntu0.20.04.2)
-- Dumped by pg_dump version 12.22 (Ubuntu 12.22-0ubuntu0.20.04.2)

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
-- Name: credit_transactions; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.credit_transactions OWNER TO postgres;

--
-- Name: credits; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.credits (
    user_id character varying(36) NOT NULL,
    total integer NOT NULL,
    used integer NOT NULL
);


ALTER TABLE public.credits OWNER TO postgres;

--
-- Name: export_jobs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.export_jobs (
    id character varying(36) NOT NULL,
    project_id character varying(36) NOT NULL,
    user_id character varying(36) NOT NULL,
    output_path text NOT NULL,
    format character varying(20) NOT NULL,
    width integer NOT NULL,
    height integer NOT NULL,
    fps integer NOT NULL,
    video_bitrate character varying(50) NOT NULL,
    audio_bitrate character varying(50) NOT NULL,
    start_frame integer NOT NULL,
    end_frame integer,
    started_at timestamp without time zone NOT NULL,
    completed_at timestamp without time zone,
    status character varying(50) NOT NULL,
    priority integer DEFAULT 0,
    progress real DEFAULT 0,
    error text
);


ALTER TABLE public.export_jobs OWNER TO postgres;

--
-- Name: project_assets; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.project_assets OWNER TO postgres;

--
-- Name: project_timeline; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.project_timeline OWNER TO postgres;

--
-- Name: projects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.projects (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    user_id character varying(36) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.projects OWNER TO postgres;

--
-- Name: sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sessions (
    token character varying(36) NOT NULL,
    user_id character varying(36) NOT NULL,
    username character varying(100) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    ip_address character varying(50),
    user_agent text,
    last_activity timestamp without time zone
);


ALTER TABLE public.sessions OWNER TO postgres;

--
-- Name: system_logs; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.system_logs OWNER TO postgres;

--
-- Name: system_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.system_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.system_logs_id_seq OWNER TO postgres;

--
-- Name: system_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.system_logs_id_seq OWNED BY public.system_logs.id;


--
-- Name: system_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_settings (
    key character varying(100) NOT NULL,
    value text NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.system_settings OWNER TO postgres;

--
-- Name: timeline_clips; Type: TABLE; Schema: public; Owner: postgres
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


ALTER TABLE public.timeline_clips OWNER TO postgres;

--
-- Name: timeline_tracks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.timeline_tracks (
    id character varying(36) NOT NULL,
    project_id character varying(36) NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.timeline_tracks OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id character varying(36) NOT NULL,
    username character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    role character varying(50) NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: system_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_logs ALTER COLUMN id SET DEFAULT nextval('public.system_logs_id_seq'::regclass);


--
-- Data for Name: credit_transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.credit_transactions (id, user_id, amount, "timestamp", type, description, status) FROM stdin;
\.


--
-- Data for Name: credits; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.credits (user_id, total, used) FROM stdin;
6034a526-2ca0-4ca6-a67c-bde23a5a35c3	9999	0
\.


--
-- Data for Name: export_jobs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.export_jobs (id, project_id, user_id, output_path, format, width, height, fps, video_bitrate, audio_bitrate, start_frame, end_frame, started_at, completed_at, status, priority, progress, error) FROM stdin;
\.


--
-- Data for Name: project_assets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.project_assets (id, project_id, name, filename, path, type, added_at) FROM stdin;
\.


--
-- Data for Name: project_timeline; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.project_timeline (project_id, duration, width, height, fps_num, fps_den, sample_rate, channels, channel_layout) FROM stdin;
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.projects (id, name, description, user_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sessions (token, user_id, username, created_at, expires_at, ip_address, user_agent, last_activity) FROM stdin;
81bbaa74-512e-466f-b570-6c39ce23cbf8	6034a526-2ca0-4ca6-a67c-bde23a5a35c3	admin	2025-03-15 23:53:25.452158	2025-04-14 23:53:25.452158	\N	\N	2025-03-15 23:53:25.452158
\.


--
-- Data for Name: system_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_logs (id, "timestamp", level, module, message, user_id, ip_address) FROM stdin;
1	2025-03-15 23:47:12.601858	INFO	app	Application starting	\N	\N
2	2025-03-15 23:47:12.614013	INFO	app	Initialized default landing page settings	\N	\N
3	2025-03-15 23:47:13.066318	INFO	app	Application starting	\N	\N
4	2025-03-15 23:49:38.770396	INFO	app	Application starting	\N	\N
5	2025-03-15 23:49:38.831185	INFO	app	Application starting	\N	\N
6	2025-03-15 23:49:38.896945	INFO	app	Application starting	\N	\N
7	2025-03-15 23:49:38.945546	INFO	app	Application starting	\N	\N
8	2025-03-15 23:52:42.496757	INFO	app	Application starting	\N	\N
9	2025-03-15 23:52:42.592936	INFO	app	Application starting	\N	\N
10	2025-03-15 23:52:42.688516	INFO	app	Application starting	\N	\N
11	2025-03-15 23:52:42.735647	INFO	app	Application starting	\N	\N
12	2025-03-15 23:53:28.206638	INFO	app	Application starting	\N	\N
13	2025-03-15 23:53:28.242027	INFO	app	Application starting	\N	\N
14	2025-03-15 23:53:28.243088	INFO	app	Application starting	\N	\N
15	2025-03-15 23:53:28.289967	INFO	app	Application starting	\N	\N
16	2025-03-16 00:00:27.52422	INFO	app	Application starting	\N	\N
17	2025-03-16 00:00:27.985221	INFO	app	Application starting	\N	\N
18	2025-03-16 00:01:08.171513	INFO	admin	Admin accessed landing page editor	6034a526-2ca0-4ca6-a67c-bde23a5a35c3	192.168.200.112
19	2025-03-16 00:01:35.248017	INFO	admin	Admin accessed landing page editor	6034a526-2ca0-4ca6-a67c-bde23a5a35c3	192.168.200.112
\.


--
-- Data for Name: system_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_settings (key, value, updated_at) FROM stdin;
landing_page_settings	{"hero": {"title": "FLUX58 AI MEDIA LABS", "subtitle": "Create stunning videos with our AI-powered platform", "text": "No downloads required. Edit from anywhere with our cloud-based video editor. Powered by IBM POWER8 architecture.", "bg_color": "#343a40", "text_color": "#ffffff", "image": "img/hero-image.jpg"}, "features": {"title": "Key Features", "accent_color": "#007bff", "cards": [{"icon": "bi-cloud-arrow-up", "title": "Cloud-Powered", "text": "Edit videos directly in your browser with no software to install."}, {"icon": "bi-cpu", "title": "AI Processing", "text": "Advanced AI-based video processing for stunning results."}, {"icon": "bi-hdd", "title": "Secure Storage", "text": "Your projects are safely stored in our secure cloud environment."}]}, "cta": {"title": "Start Creating Amazing Videos Today", "subtitle": "Join thousands of content creators who trust FLUX58", "button_text": "Start Creating Now", "button_color": "#007bff"}, "navbar": {"brand_text": "FLUX58 AI MEDIA LABS", "bg_color": "#212529", "text_color": "#ffffff", "logo": "img/custom/FLUXLOGO2.png", "menu_items": [{"text": "Home", "url": "/", "visible": true}, {"text": "Dashboard", "url": "/dashboard", "visible": true, "requires_login": true}, {"text": "Projects", "url": "/projects", "visible": true, "requires_login": true}, {"text": "Credits", "url": "/credits", "visible": true, "requires_login": true}, {"text": "Pricing", "url": "/pricing", "visible": true}]}}	2025-03-16 00:01:35.24387
\.


--
-- Data for Name: timeline_clips; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.timeline_clips (id, track_id, asset_id, "position", duration, start_point, end_point, properties) FROM stdin;
\.


--
-- Data for Name: timeline_tracks; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.timeline_tracks (id, project_id, name) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, username, password_hash, email, created_at, role) FROM stdin;
6034a526-2ca0-4ca6-a67c-bde23a5a35c3	admin	scrypt:32768:8:1$zPi2AYCElBUJQbWA$ad041e385ff57fb39618d7fd68710e06f6821cd49bfbc78431441b18328694791620c035a78164563ed7d9d79b001b32f42fe5ffbdf1aaf38d1bfc64b2a1ae77	admin@example.com	2025-03-15 23:53:25.452158	admin
\.


--
-- Name: system_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.system_logs_id_seq', 19, true);


--
-- Name: credit_transactions credit_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credit_transactions
    ADD CONSTRAINT credit_transactions_pkey PRIMARY KEY (id);


--
-- Name: credits credits_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credits
    ADD CONSTRAINT credits_pkey PRIMARY KEY (user_id);


--
-- Name: export_jobs export_jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.export_jobs
    ADD CONSTRAINT export_jobs_pkey PRIMARY KEY (id);


--
-- Name: project_assets project_assets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_assets
    ADD CONSTRAINT project_assets_pkey PRIMARY KEY (id);


--
-- Name: project_timeline project_timeline_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_timeline
    ADD CONSTRAINT project_timeline_pkey PRIMARY KEY (project_id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (token);


--
-- Name: system_logs system_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_logs
    ADD CONSTRAINT system_logs_pkey PRIMARY KEY (id);


--
-- Name: system_settings system_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_pkey PRIMARY KEY (key);


--
-- Name: timeline_clips timeline_clips_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timeline_clips
    ADD CONSTRAINT timeline_clips_pkey PRIMARY KEY (id);


--
-- Name: timeline_tracks timeline_tracks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timeline_tracks
    ADD CONSTRAINT timeline_tracks_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_assets_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_assets_project_id ON public.project_assets USING btree (project_id);


--
-- Name: idx_assets_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_assets_type ON public.project_assets USING btree (type);


--
-- Name: idx_clips_asset_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_clips_asset_id ON public.timeline_clips USING btree (asset_id);


--
-- Name: idx_clips_track_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_clips_track_id ON public.timeline_clips USING btree (track_id);


--
-- Name: idx_exports_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_exports_priority ON public.export_jobs USING btree (priority DESC);


--
-- Name: idx_exports_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_exports_status ON public.export_jobs USING btree (status);


--
-- Name: idx_exports_user_started; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_exports_user_started ON public.export_jobs USING btree (user_id, started_at DESC);


--
-- Name: idx_logs_level; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_logs_level ON public.system_logs USING btree (level);


--
-- Name: idx_logs_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_logs_timestamp ON public.system_logs USING btree ("timestamp" DESC);


--
-- Name: idx_projects_user_updated; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_projects_user_updated ON public.projects USING btree (user_id, updated_at DESC);


--
-- Name: idx_sessions_expires_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sessions_expires_at ON public.sessions USING btree (expires_at);


--
-- Name: idx_sessions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_sessions_user_id ON public.sessions USING btree (user_id);


--
-- Name: idx_tracks_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tracks_project_id ON public.timeline_tracks USING btree (project_id);


--
-- Name: idx_transactions_user_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_transactions_user_timestamp ON public.credit_transactions USING btree (user_id, "timestamp" DESC);


--
-- Name: credit_transactions credit_transactions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credit_transactions
    ADD CONSTRAINT credit_transactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: credits credits_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.credits
    ADD CONSTRAINT credits_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: export_jobs export_jobs_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.export_jobs
    ADD CONSTRAINT export_jobs_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: export_jobs export_jobs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.export_jobs
    ADD CONSTRAINT export_jobs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: project_assets project_assets_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_assets
    ADD CONSTRAINT project_assets_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: project_timeline project_timeline_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_timeline
    ADD CONSTRAINT project_timeline_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: projects projects_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: sessions sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: system_logs system_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_logs
    ADD CONSTRAINT system_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: timeline_clips timeline_clips_asset_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timeline_clips
    ADD CONSTRAINT timeline_clips_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES public.project_assets(id) ON DELETE CASCADE;


--
-- Name: timeline_clips timeline_clips_track_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timeline_clips
    ADD CONSTRAINT timeline_clips_track_id_fkey FOREIGN KEY (track_id) REFERENCES public.timeline_tracks(id) ON DELETE CASCADE;


--
-- Name: timeline_tracks timeline_tracks_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.timeline_tracks
    ADD CONSTRAINT timeline_tracks_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

