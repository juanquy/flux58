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
caebde28-b272-4165-86cb-ab01eae9dbb5	e017c72e-5642-49ab-8875-f72323a052ca	5000	2025-03-21 22:34:21.130808	initial	Initial test credits	completed
\.


--
-- Data for Name: credits; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.credits (user_id, total, used) FROM stdin;
e017c72e-5642-49ab-8875-f72323a052ca	5000	0
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
8bbef700-43f7-4909-9276-6fef43a6e504	60	1920	1080	30	1	48000	2	3
253a897b-5b6c-4e8b-a833-947cd6fa77f1	60	1920	1080	30	1	48000	2	3
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.projects (id, user_id, name, description, created_at, updated_at, settings) FROM stdin;
8bbef700-43f7-4909-9276-6fef43a6e504	e017c72e-5642-49ab-8875-f72323a052ca	test 2	test	2025-03-21 22:39:21.325537	2025-03-21 22:39:21.325537	\N
253a897b-5b6c-4e8b-a833-947cd6fa77f1	e017c72e-5642-49ab-8875-f72323a052ca	Test Project 2025-03-22 01:15:32	Created by automated test script	2025-03-22 01:15:32.121266	2025-03-22 01:15:32.121266	\N
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
5	2025-03-21 20:42:21.823719	INFO	app	Application starting	\N	\N
6	2025-03-21 20:42:22.188619	INFO	app	Application starting	\N	\N
7	2025-03-21 20:42:25.773068	INFO	app	Application starting	\N	\N
8	2025-03-21 20:42:26.116242	INFO	app	Application starting	\N	\N
9	2025-03-21 20:43:55.993634	INFO	app	Application starting	\N	\N
10	2025-03-21 20:43:56.345669	INFO	app	Application starting	\N	\N
11	2025-03-21 20:44:03.274032	INFO	app	Application starting	\N	\N
12	2025-03-21 20:44:03.656782	INFO	app	Application starting	\N	\N
13	2025-03-21 20:44:27.629504	INFO	app	Application starting	\N	\N
14	2025-03-21 20:44:27.990968	INFO	app	Application starting	\N	\N
15	2025-03-21 20:48:06.274262	INFO	app	Application starting	\N	\N
16	2025-03-21 20:48:06.646337	INFO	app	Application starting	\N	\N
17	2025-03-21 20:51:04.972031	INFO	app	Application starting	\N	\N
18	2025-03-21 20:51:05.335663	INFO	app	Application starting	\N	\N
19	2025-03-21 20:51:25.018951	INFO	app	Application starting	\N	\N
20	2025-03-21 20:51:25.383285	INFO	app	Application starting	\N	\N
21	2025-03-21 20:51:49.466615	INFO	app	Application starting	\N	\N
22	2025-03-21 20:51:49.822375	INFO	app	Application starting	\N	\N
23	2025-03-21 20:52:03.095278	INFO	app	Application starting	\N	\N
24	2025-03-21 20:52:03.478257	INFO	app	Application starting	\N	\N
25	2025-03-21 20:52:52.312119	INFO	app	Application starting	\N	\N
26	2025-03-21 20:55:49.176522	INFO	app	Application starting	\N	\N
27	2025-03-21 21:16:07.40815	INFO	app	Application starting	\N	\N
28	2025-03-21 21:24:34.1249	INFO	app	Application starting	\N	\N
29	2025-03-21 21:28:54.889735	INFO	app	Application starting	\N	\N
30	2025-03-21 21:31:26.100051	INFO	app	Application starting	\N	\N
31	2025-03-21 21:35:04.981283	INFO	app	Application starting	\N	\N
32	2025-03-21 21:38:32.660963	INFO	app	Application starting	\N	\N
33	2025-03-21 21:41:47.770569	INFO	app	Application starting	\N	\N
34	2025-03-21 21:42:01.695293	INFO	app	Application starting	\N	\N
35	2025-03-21 21:48:31.598474	INFO	app	Application starting	\N	\N
36	2025-03-21 21:52:56.404039	INFO	app	Application starting	\N	\N
37	2025-03-21 22:03:46.27383	INFO	app	Application starting	\N	\N
\.


--
-- Data for Name: system_settings; Type: TABLE DATA; Schema: public; Owner: flux58_user
--

COPY public.system_settings (key, value, updated_at) FROM stdin;
hero_bg_image		2025-03-22 00:14:27.647736
landing_page_hero_image	img/custom/hero_1742602487.png	2025-03-22 00:14:47.23099
landing_page_title	FLUX58 AI MEDIA LABS	2025-03-22 00:14:54.62546
landing_page_subtitle	Powerful AI-Enhanced Video Editing	2025-03-22 00:14:54.637874
landing_page_description	Create professional videos with our cloud-based video editor, powered by AI	2025-03-22 00:14:54.640198
hero_bg_color	#343a40	2025-03-22 00:14:54.642691
hero_text_color	#ffffff	2025-03-22 00:14:54.644746
hero_bg_image_overlay	False	2025-03-22 00:14:54.646875
navbar_logo	img/logo_1742595597.png	2025-03-21 22:19:57.984611
test_fix_direct	SUCCESS	2025-03-22 02:31:27.208957
test_setting	test_value_66a54f19	2025-03-21 21:46:46.616935
features_title	Features	2025-03-21 21:47:46.047958
features_accent_color	#007bff	2025-03-21 21:47:46.061071
feature1_icon	bi-camera-video	2025-03-21 21:47:46.063261
feature1_title	Video Editing	2025-03-21 21:47:46.065581
feature1_text	Edit video with our powerful cloud-based editor	2025-03-21 21:47:46.067753
feature2_icon	bi-robot	2025-03-21 21:47:46.069883
feature2_title	AI Enhancement	2025-03-21 21:47:46.071904
feature2_text	Leverage AI to enhance your videos automatically	2025-03-21 21:47:46.073961
feature3_icon	bi-cloud-upload	2025-03-21 21:47:46.076152
feature3_title	Cloud Storage	2025-03-21 21:47:46.078449
feature3_text	Store your projects securely in the cloud	2025-03-21 21:47:46.08072
cta_title	Ready to get started?	2025-03-21 21:47:46.082952
cta_subtitle	Sign up today and create amazing videos.	2025-03-21 21:47:46.08521
cta_button_text	Get Started	2025-03-21 21:47:46.08734
cta_button_color	#007bff	2025-03-21 21:47:46.089772
test_fix_script	test_value_from_fix_script	2025-03-21 21:47:46.092037
test_db_impl_1742593686	test_value_2025-03-21T21:48:06.292557	2025-03-21 21:48:06.292576
flux58_startup_1742593711	STARTUP_TEST	2025-03-21 21:48:31.331425
navbar_brand_text	FLUX58 AI MEDIA LABS	2025-03-22 00:05:50.22867
navbar_bg_color	#212529	2025-03-22 00:05:50.241362
navbar_text_color	#000000	2025-03-22 00:05:50.243688
navbar_menu_items	[]	2025-03-22 00:05:50.246071
page_bg_color	#ffffff	2025-03-22 00:06:11.207337
content_bg_color	#ffffff	2025-03-22 00:06:11.220414
content_text_color	#212529	2025-03-22 00:06:11.222631
page_bg_image	img/custom/page_bg_1742601971.png	2025-03-22 00:06:11.228801
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
e017c72e-5642-49ab-8875-f72323a052ca	test	scrypt:32768:8:1$Wb1tGWD6ut0P3cCr$b89320de93e0295d4a27cf6b891e6d2e7c2f77af401cce75db8d4c12e4c980a83fe7effcb660c50c12a49ba772f60cb0d2aa8731e7a6886484b475e3600800ff	test@example.com	2025-03-21 22:34:21.130808	user
\.


--
-- Name: logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: flux58_user
--

SELECT pg_catalog.setval('public.logs_id_seq', 1, false);


--
-- Name: system_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: flux58_user
--

SELECT pg_catalog.setval('public.system_logs_id_seq', 37, true);


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

