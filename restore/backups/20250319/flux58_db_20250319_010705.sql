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


ALTER TABLE public.export_jobs OWNER TO flux58_user;

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
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    user_id character varying(36) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.projects OWNER TO flux58_user;

--
-- Name: sessions; Type: TABLE; Schema: public; Owner: flux58_user
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


ALTER TABLE public.system_logs_id_seq OWNER TO flux58_user;

--
-- Name: system_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: flux58_user
--

ALTER SEQUENCE public.system_logs_id_seq OWNED BY public.system_logs.id;


--
-- Name: system_settings; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.system_settings (
    key character varying(100) NOT NULL,
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
-- Name: users; Type: TABLE; Schema: public; Owner: flux58_user
--

CREATE TABLE public.users (
    id character varying(36) NOT NULL,
    username character varying(100) NOT NULL,
    password_hash character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    role character varying(50) NOT NULL
);


ALTER TABLE public.users OWNER TO flux58_user;

--
-- Name: system_logs id; Type: DEFAULT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.system_logs ALTER COLUMN id SET DEFAULT nextval('public.system_logs_id_seq'::regclass);


--
-- Data for Name: credit_transactions; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.credit_transactions (id, user_id, amount, "timestamp", type, description, status) FROM stdin;
11a7c9f0-926c-432f-b4c5-7ec57ffe9576	bad635e5-4287-4d6f-b530-ed2beed4f86a	9999	2025-03-19 00:10:29.786203	initial	Admin account setup	completed
\.


--
-- Data for Name: credits; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.credits (user_id, total, used) FROM stdin;
bad635e5-4287-4d6f-b530-ed2beed4f86a	9999	0
\.


--
-- Data for Name: export_jobs; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.export_jobs (id, project_id, user_id, output_path, format, width, height, fps, video_bitrate, audio_bitrate, start_frame, end_frame, started_at, completed_at, status, priority, progress, error) FROM stdin;
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

COPY public.projects (id, name, description, user_id, created_at, updated_at) FROM stdin;
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
1	2025-03-19 00:10:29.673289	INFO	app	Application starting	\N	\N
2	2025-03-19 00:10:29.685762	INFO	app	Creating admin account	\N	\N
3	2025-03-19 00:10:29.78686	INFO	app	Admin account created successfully	\N	\N
4	2025-03-19 00:10:30.175367	INFO	app	Application starting	\N	\N
5	2025-03-19 00:18:06.675198	INFO	app	Application starting	\N	\N
6	2025-03-19 00:18:07.072414	INFO	app	Application starting	\N	\N
7	2025-03-19 00:21:40.942658	INFO	app	Application starting	\N	\N
8	2025-03-19 00:21:41.340249	INFO	app	Application starting	\N	\N
9	2025-03-19 00:24:24.438199	INFO	app	Application starting	\N	\N
10	2025-03-19 00:24:24.843197	INFO	app	Application starting	\N	\N
11	2025-03-19 00:27:19.793568	INFO	app	Application starting	\N	\N
12	2025-03-19 00:27:20.196799	INFO	app	Application starting	\N	\N
13	2025-03-19 00:33:07.689638	INFO	app	Application starting	\N	\N
14	2025-03-19 00:39:33.881979	INFO	app	Application starting	\N	\N
15	2025-03-19 00:39:34.297118	INFO	app	Application starting	\N	\N
16	2025-03-19 00:55:54.064006	INFO	app	Application starting	\N	\N
17	2025-03-19 00:55:54.467623	INFO	app	Application starting	\N	\N
18	2025-03-19 00:57:40.733263	INFO	app	Application starting	\N	\N
19	2025-03-19 00:57:41.138465	INFO	app	Application starting	\N	\N
20	2025-03-19 00:58:31.878282	INFO	app	Application starting	\N	\N
21	2025-03-19 00:58:32.284613	INFO	app	Application starting	\N	\N
22	2025-03-19 01:00:35.289646	INFO	app	Application starting	\N	\N
23	2025-03-19 01:00:35.69015	INFO	app	Application starting	\N	\N
24	2025-03-19 01:05:06.164899	INFO	app	Application starting	\N	\N
25	2025-03-19 01:05:06.551237	INFO	app	Application starting	\N	\N
\.


--
-- Data for Name: system_settings; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.system_settings (key, value, updated_at) FROM stdin;
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
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.users (id, username, password_hash, email, created_at, role) FROM stdin;
bad635e5-4287-4d6f-b530-ed2beed4f86a	admin	scrypt:32768:8:1$iMpyQzNQQBKT2ypW$09ba428dc46d150e9e97e79329383784b2a71cc3b71f4e29cad38a48f0be37fca10363acd36843efdc11e5d51a16ac8adca7d039e33bfeec54d05e968022280a	admin@flux58.com	2025-03-19 00:10:29.784685	admin
\.


--
-- Name: system_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: flux58_user
--

SELECT pg_catalog.setval('public.system_logs_id_seq', 25, true);


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
    ADD CONSTRAINT export_jobs_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: export_jobs export_jobs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.export_jobs
    ADD CONSTRAINT export_jobs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


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
    ADD CONSTRAINT projects_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: sessions sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: flux58_user
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


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
-- PostgreSQL database dump complete
--

