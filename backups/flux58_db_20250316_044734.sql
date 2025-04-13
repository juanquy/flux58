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
-- Name: assets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.assets (
    id character varying(50) NOT NULL,
    project_id character varying(50) NOT NULL,
    name character varying(255) NOT NULL,
    type character varying(50) NOT NULL,
    file_extension character varying(20) NOT NULL,
    file_path character varying(255) NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.assets OWNER TO postgres;

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
-- Name: exports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exports (
    id character varying(50) NOT NULL,
    project_id character varying(50) NOT NULL,
    user_id character varying(50) NOT NULL,
    format character varying(20) NOT NULL,
    resolution character varying(50) NOT NULL,
    status character varying(20) NOT NULL,
    progress integer NOT NULL,
    file_path character varying(255) NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.exports OWNER TO postgres;

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
-- Data for Name: assets; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.assets (id, project_id, name, type, file_extension, file_path, created_at) FROM stdin;
\.


--
-- Data for Name: credit_transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.credit_transactions (id, user_id, amount, "timestamp", type, description, status) FROM stdin;
f203447e-88c1-441a-a66b-1b0a477e1d3d	9098d630-f606-40f9-b2dd-51167540ed71	5000	2025-03-16 00:07:24.421177	initial	Initial test credits	completed
\.


--
-- Data for Name: credits; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.credits (user_id, total, used) FROM stdin;
6034a526-2ca0-4ca6-a67c-bde23a5a35c3	9999	0
9098d630-f606-40f9-b2dd-51167540ed71	5000	0
\.


--
-- Data for Name: export_jobs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.export_jobs (id, project_id, user_id, output_path, format, width, height, fps, video_bitrate, audio_bitrate, start_frame, end_frame, started_at, completed_at, status, priority, progress, error) FROM stdin;
\.


--
-- Data for Name: exports; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exports (id, project_id, user_id, format, resolution, status, progress, file_path, created_at) FROM stdin;
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
51274d3d-8755-44ac-94c3-8c102b6e1715	60	1920	1080	30	1	48000	2	3
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.projects (id, name, description, user_id, created_at, updated_at) FROM stdin;
51274d3d-8755-44ac-94c3-8c102b6e1715	Social Media Video	Video optimized for social media platforms	9098d630-f606-40f9-b2dd-51167540ed71	2025-03-16 00:50:18.842912	2025-03-16 00:50:18.842912
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
20	2025-03-16 00:08:06.72164	INFO	app	Application starting	\N	\N
21	2025-03-16 00:08:06.774792	INFO	app	Application starting	\N	\N
22	2025-03-16 00:08:06.833107	INFO	app	Application starting	\N	\N
23	2025-03-16 00:08:06.919341	INFO	app	Application starting	\N	\N
24	2025-03-16 00:13:26.11429	INFO	app	Application starting	\N	\N
25	2025-03-16 00:13:26.159153	INFO	app	Application starting	\N	\N
26	2025-03-16 00:13:26.240958	INFO	app	Application starting	\N	\N
27	2025-03-16 00:13:26.337428	INFO	app	Application starting	\N	\N
28	2025-03-16 00:22:14.47185	INFO	app	Application starting	\N	\N
29	2025-03-16 00:22:14.486374	INFO	app	Application starting	\N	\N
30	2025-03-16 00:22:14.514469	INFO	app	Application starting	\N	\N
31	2025-03-16 00:22:14.531756	INFO	app	Application starting	\N	\N
32	2025-03-16 00:25:57.482547	INFO	admin	Admin accessed landing page editor	6034a526-2ca0-4ca6-a67c-bde23a5a35c3	192.168.200.112
33	2025-03-16 00:26:12.957488	INFO	admin	Admin accessed landing page editor	6034a526-2ca0-4ca6-a67c-bde23a5a35c3	192.168.200.112
34	2025-03-16 00:26:28.878284	INFO	admin	Admin accessed landing page editor	6034a526-2ca0-4ca6-a67c-bde23a5a35c3	192.168.200.112
35	2025-03-16 00:26:40.085082	INFO	admin	Admin accessed landing page editor	6034a526-2ca0-4ca6-a67c-bde23a5a35c3	192.168.200.112
36	2025-03-16 00:26:48.611355	INFO	admin	Admin accessed landing page editor	6034a526-2ca0-4ca6-a67c-bde23a5a35c3	192.168.200.112
37	2025-03-16 00:27:02.0266	INFO	admin	Admin accessed landing page editor	6034a526-2ca0-4ca6-a67c-bde23a5a35c3	192.168.200.112
38	2025-03-16 00:27:53.709589	INFO	admin	Admin accessed landing page editor	6034a526-2ca0-4ca6-a67c-bde23a5a35c3	192.168.200.112
39	2025-03-16 00:28:00.681183	INFO	admin	Admin accessed landing page editor	6034a526-2ca0-4ca6-a67c-bde23a5a35c3	192.168.200.112
40	2025-03-16 00:30:46.217732	INFO	app	Application starting	\N	\N
41	2025-03-16 00:41:54.850492	INFO	app	Application starting	\N	\N
42	2025-03-16 00:41:54.922279	INFO	app	Application starting	\N	\N
43	2025-03-16 00:41:54.929764	INFO	app	Application starting	\N	\N
44	2025-03-16 00:41:54.948067	INFO	app	Application starting	\N	\N
45	2025-03-16 00:45:14.024962	INFO	app	Application starting	\N	\N
46	2025-03-16 00:45:14.0746	INFO	app	Application starting	\N	\N
47	2025-03-16 00:45:14.149837	INFO	app	Application starting	\N	\N
48	2025-03-16 00:45:14.237752	INFO	app	Application starting	\N	\N
49	2025-03-16 00:45:14.877598	INFO	app	Application starting	\N	\N
50	2025-03-16 00:45:14.978518	INFO	app	Application starting	\N	\N
51	2025-03-16 00:45:15.056667	INFO	app	Application starting	\N	\N
52	2025-03-16 00:45:15.105326	INFO	app	Application starting	\N	\N
53	2025-03-16 00:45:15.878652	INFO	app	Application starting	\N	\N
54	2025-03-16 00:45:15.894159	INFO	app	Application starting	\N	\N
55	2025-03-16 00:45:15.994549	INFO	app	Application starting	\N	\N
56	2025-03-16 00:45:16.065162	INFO	app	Application starting	\N	\N
57	2025-03-16 00:45:16.873932	INFO	app	Application starting	\N	\N
58	2025-03-16 00:45:16.895324	INFO	app	Application starting	\N	\N
59	2025-03-16 00:45:16.917037	INFO	app	Application starting	\N	\N
60	2025-03-16 00:45:17.011571	INFO	app	Application starting	\N	\N
61	2025-03-16 00:45:17.872421	INFO	app	Application starting	\N	\N
62	2025-03-16 00:45:17.903283	INFO	app	Application starting	\N	\N
63	2025-03-16 00:45:17.993201	INFO	app	Application starting	\N	\N
64	2025-03-16 00:45:18.070999	INFO	app	Application starting	\N	\N
65	2025-03-16 00:45:27.05369	INFO	app	Application starting	\N	\N
66	2025-03-16 00:45:27.5308	INFO	app	Application starting	\N	\N
67	2025-03-16 00:46:00.84466	INFO	admin	Admin accessed landing page editor	6034a526-2ca0-4ca6-a67c-bde23a5a35c3	192.168.200.112
68	2025-03-16 00:46:31.684226	INFO	admin	Admin accessed landing page editor	6034a526-2ca0-4ca6-a67c-bde23a5a35c3	192.168.200.112
69	2025-03-16 00:49:04.694581	INFO	app	Application starting	\N	\N
70	2025-03-16 00:49:05.151828	INFO	app	Application starting	\N	\N
71	2025-03-16 00:49:12.330737	INFO	app	Application starting	\N	\N
72	2025-03-16 00:49:12.399633	INFO	app	Application starting	\N	\N
73	2025-03-16 00:49:12.459351	INFO	app	Application starting	\N	\N
74	2025-03-16 00:49:12.5254	INFO	app	Application starting	\N	\N
75	2025-03-16 00:50:48.552093	INFO	app	Application starting	\N	\N
76	2025-03-16 00:50:48.587207	INFO	app	Application starting	\N	\N
77	2025-03-16 00:50:48.624659	INFO	app	Application starting	\N	\N
78	2025-03-16 00:50:48.628806	INFO	app	Application starting	\N	\N
79	2025-03-16 00:53:29.738026	INFO	app	Application starting	\N	\N
80	2025-03-16 00:53:29.782989	INFO	app	Application starting	\N	\N
81	2025-03-16 00:53:29.843376	INFO	app	Application starting	\N	\N
82	2025-03-16 00:53:29.893745	INFO	app	Application starting	\N	\N
83	2025-03-16 01:00:34.693776	INFO	app	Application starting	\N	\N
84	2025-03-16 01:00:34.757181	INFO	app	Application starting	\N	\N
85	2025-03-16 01:00:34.796246	INFO	app	Application starting	\N	\N
86	2025-03-16 01:00:34.828964	INFO	app	Application starting	\N	\N
87	2025-03-16 01:00:35.625051	INFO	app	Application starting	\N	\N
88	2025-03-16 01:00:35.706981	INFO	app	Application starting	\N	\N
89	2025-03-16 01:00:35.750743	INFO	app	Application starting	\N	\N
90	2025-03-16 01:00:35.836662	INFO	app	Application starting	\N	\N
91	2025-03-16 01:00:36.622695	INFO	app	Application starting	\N	\N
92	2025-03-16 01:00:36.637665	INFO	app	Application starting	\N	\N
93	2025-03-16 01:00:36.688719	INFO	app	Application starting	\N	\N
94	2025-03-16 01:00:36.709455	INFO	app	Application starting	\N	\N
95	2025-03-16 01:00:37.377496	INFO	app	Application starting	\N	\N
96	2025-03-16 01:00:37.422253	INFO	app	Application starting	\N	\N
97	2025-03-16 01:00:37.502417	INFO	app	Application starting	\N	\N
98	2025-03-16 01:00:37.515005	INFO	app	Application starting	\N	\N
99	2025-03-16 01:00:38.133192	INFO	app	Application starting	\N	\N
100	2025-03-16 01:00:38.222736	INFO	app	Application starting	\N	\N
101	2025-03-16 01:00:38.238219	INFO	app	Application starting	\N	\N
102	2025-03-16 01:00:38.276324	INFO	app	Application starting	\N	\N
103	2025-03-16 01:15:03.382795	INFO	app	Application starting	\N	\N
104	2025-03-16 01:17:58.582498	INFO	app	Application starting	\N	\N
105	2025-03-16 01:19:34.727029	INFO	app	Application starting	\N	\N
106	2025-03-16 01:19:35.142917	INFO	app	Application starting	\N	\N
107	2025-03-16 01:23:34.285566	INFO	app	Application starting	\N	\N
108	2025-03-16 01:23:34.702498	INFO	app	Application starting	\N	\N
109	2025-03-16 01:24:25.527868	INFO	app	Application starting	\N	\N
110	2025-03-16 01:24:25.953715	INFO	app	Application starting	\N	\N
111	2025-03-16 01:26:49.464766	INFO	app	Application starting	\N	\N
112	2025-03-16 01:26:49.877518	INFO	app	Application starting	\N	\N
113	2025-03-16 01:29:32.230522	INFO	app	Application starting	\N	\N
114	2025-03-16 01:29:32.646677	INFO	app	Application starting	\N	\N
115	2025-03-16 01:29:57.96832	INFO	app	Application starting	\N	\N
116	2025-03-16 01:29:58.389632	INFO	app	Application starting	\N	\N
117	2025-03-16 01:34:56.989689	INFO	app	Application starting	\N	\N
118	2025-03-16 01:34:57.030567	INFO	app	Application starting	\N	\N
119	2025-03-16 01:34:57.101462	INFO	app	Application starting	\N	\N
120	2025-03-16 01:34:57.124466	INFO	app	Application starting	\N	\N
121	2025-03-16 01:38:05.970847	INFO	app	Application starting	\N	\N
122	2025-03-16 01:38:05.986346	INFO	app	Application starting	\N	\N
123	2025-03-16 01:38:06.046017	INFO	app	Application starting	\N	\N
124	2025-03-16 01:38:06.057571	INFO	app	Application starting	\N	\N
125	2025-03-16 01:39:03.226944	INFO	app	Application starting	\N	\N
126	2025-03-16 01:39:11.555311	INFO	app	Application starting	\N	\N
127	2025-03-16 01:39:11.617307	INFO	app	Application starting	\N	\N
128	2025-03-16 01:39:11.684998	INFO	app	Application starting	\N	\N
129	2025-03-16 01:39:11.740091	INFO	app	Application starting	\N	\N
130	2025-03-16 01:39:33.897848	INFO	app	Application starting	\N	\N
131	2025-03-16 01:39:33.980766	INFO	app	Application starting	\N	\N
132	2025-03-16 01:39:34.062813	INFO	app	Application starting	\N	\N
133	2025-03-16 01:39:34.092079	INFO	app	Application starting	\N	\N
134	2025-03-16 01:44:08.990289	INFO	app	Application starting	\N	\N
135	2025-03-16 01:44:09.062168	INFO	app	Application starting	\N	\N
136	2025-03-16 01:44:09.1424	INFO	app	Application starting	\N	\N
137	2025-03-16 01:44:09.15275	INFO	app	Application starting	\N	\N
138	2025-03-16 01:46:38.36723	INFO	app	Application starting	\N	\N
139	2025-03-16 01:47:25.515702	INFO	app	Application starting	\N	\N
140	2025-03-16 01:47:25.567703	INFO	app	Application starting	\N	\N
141	2025-03-16 01:47:41.052352	INFO	app	Application starting	\N	\N
142	2025-03-16 01:47:41.145125	INFO	app	Application starting	\N	\N
143	2025-03-16 01:47:41.202741	INFO	app	Application starting	\N	\N
144	2025-03-16 01:47:41.273701	INFO	app	Application starting	\N	\N
145	2025-03-16 01:48:47.444633	INFO	app	Application starting	\N	\N
146	2025-03-16 01:49:25.775973	INFO	app	Application starting	\N	\N
147	2025-03-16 01:49:25.837962	INFO	app	Application starting	\N	\N
148	2025-03-16 01:49:25.925626	INFO	app	Application starting	\N	\N
149	2025-03-16 01:49:25.955065	INFO	app	Application starting	\N	\N
150	2025-03-16 01:50:44.181294	INFO	app	Application starting	\N	\N
151	2025-03-16 01:50:44.2272	INFO	app	Application starting	\N	\N
152	2025-03-16 01:50:44.329618	INFO	app	Application starting	\N	\N
153	2025-03-16 01:50:44.358828	INFO	app	Application starting	\N	\N
154	2025-03-16 01:51:55.576906	INFO	app	Application starting	\N	\N
155	2025-03-16 01:51:55.593415	INFO	app	Application starting	\N	\N
156	2025-03-16 01:51:55.619078	INFO	app	Application starting	\N	\N
157	2025-03-16 01:51:55.69499	INFO	app	Application starting	\N	\N
158	2025-03-16 01:52:16.900595	INFO	app	Application starting	\N	\N
159	2025-03-16 01:52:16.980522	INFO	app	Application starting	\N	\N
160	2025-03-16 01:52:16.983833	INFO	app	Application starting	\N	\N
161	2025-03-16 01:52:16.991506	INFO	app	Application starting	\N	\N
162	2025-03-16 01:52:50.817356	INFO	app	Application starting	\N	\N
163	2025-03-16 01:52:50.860614	INFO	app	Application starting	\N	\N
164	2025-03-16 01:52:50.914807	INFO	app	Application starting	\N	\N
165	2025-03-16 01:52:51.006301	INFO	app	Application starting	\N	\N
166	2025-03-16 01:54:17.236435	INFO	app	Application starting	\N	\N
167	2025-03-16 01:55:09.532621	INFO	app	Application starting	\N	\N
168	2025-03-16 01:55:09.550627	INFO	app	Application starting	\N	\N
169	2025-03-16 01:55:09.647494	INFO	app	Application starting	\N	\N
170	2025-03-16 01:55:09.744157	INFO	app	Application starting	\N	\N
171	2025-03-16 01:57:46.4448	INFO	app	Application starting	\N	\N
172	2025-03-16 01:57:46.517886	INFO	app	Application starting	\N	\N
173	2025-03-16 01:57:46.618161	INFO	app	Application starting	\N	\N
174	2025-03-16 01:57:46.715376	INFO	app	Application starting	\N	\N
175	2025-03-16 02:02:49.965529	INFO	app	Application starting	\N	\N
176	2025-03-16 02:02:50.040884	INFO	app	Application starting	\N	\N
177	2025-03-16 02:02:50.073844	INFO	app	Application starting	\N	\N
178	2025-03-16 02:02:50.171484	INFO	app	Application starting	\N	\N
179	2025-03-16 02:04:35.79587	INFO	app	Application starting	\N	\N
180	2025-03-16 02:04:35.82679	INFO	app	Application starting	\N	\N
181	2025-03-16 02:04:35.835591	INFO	app	Application starting	\N	\N
182	2025-03-16 02:04:35.856076	INFO	app	Application starting	\N	\N
183	2025-03-16 02:07:14.15174	INFO	app	Application starting	\N	\N
184	2025-03-16 02:08:35.887659	INFO	app	Application starting	\N	\N
185	2025-03-16 02:08:35.899153	INFO	app	Application starting	\N	\N
186	2025-03-16 02:08:35.981863	INFO	app	Application starting	\N	\N
187	2025-03-16 02:08:35.988024	INFO	app	Application starting	\N	\N
188	2025-03-16 02:10:50.608885	INFO	app	Application starting	\N	\N
189	2025-03-16 02:10:50.643945	INFO	app	Application starting	\N	\N
190	2025-03-16 02:10:50.700031	INFO	app	Application starting	\N	\N
191	2025-03-16 02:10:50.787706	INFO	app	Application starting	\N	\N
192	2025-03-16 02:16:17.946699	INFO	app	Application starting	\N	\N
193	2025-03-16 02:16:18.01808	INFO	app	Application starting	\N	\N
194	2025-03-16 02:16:18.078329	INFO	app	Application starting	\N	\N
195	2025-03-16 02:16:18.135832	INFO	app	Application starting	\N	\N
196	2025-03-16 02:17:19.709947	INFO	app	Application starting	\N	\N
197	2025-03-16 02:17:19.754613	INFO	app	Application starting	\N	\N
198	2025-03-16 02:17:19.784031	INFO	app	Application starting	\N	\N
199	2025-03-16 02:17:19.806224	INFO	app	Application starting	\N	\N
200	2025-03-16 02:39:19.038224	INFO	app	Application starting	\N	\N
201	2025-03-16 02:42:41.738184	INFO	app	Application starting	\N	\N
202	2025-03-16 02:42:41.818484	INFO	app	Application starting	\N	\N
203	2025-03-16 02:42:41.851463	INFO	app	Application starting	\N	\N
204	2025-03-16 02:42:41.890446	INFO	app	Application starting	\N	\N
205	2025-03-16 02:46:17.500049	INFO	app	Application starting	\N	\N
206	2025-03-16 02:46:17.53035	INFO	app	Application starting	\N	\N
207	2025-03-16 02:46:17.624209	INFO	app	Application starting	\N	\N
208	2025-03-16 02:46:17.708503	INFO	app	Application starting	\N	\N
209	2025-03-16 02:50:49.078243	INFO	app	Application starting	\N	\N
210	2025-03-16 02:52:55.344028	INFO	app	Application starting	\N	\N
211	2025-03-16 02:53:25.424638	INFO	app	Application starting	\N	\N
212	2025-03-16 02:53:25.467574	INFO	app	Application starting	\N	\N
213	2025-03-16 02:53:25.520922	INFO	app	Application starting	\N	\N
214	2025-03-16 02:53:25.571301	INFO	app	Application starting	\N	\N
215	2025-03-16 02:57:08.334396	INFO	app	Application starting	\N	\N
216	2025-03-16 02:57:08.367048	INFO	app	Application starting	\N	\N
217	2025-03-16 02:57:08.367081	INFO	app	Application starting	\N	\N
218	2025-03-16 02:57:08.459409	INFO	app	Application starting	\N	\N
219	2025-03-16 02:59:33.846149	INFO	app	Application starting	\N	\N
220	2025-03-16 02:59:33.86171	INFO	app	Application starting	\N	\N
221	2025-03-16 02:59:33.880088	INFO	app	Application starting	\N	\N
222	2025-03-16 02:59:33.923899	INFO	app	Application starting	\N	\N
223	2025-03-16 03:00:03.936408	INFO	app	Application starting	\N	\N
224	2025-03-16 03:00:03.998795	INFO	app	Application starting	\N	\N
225	2025-03-16 03:00:04.088742	INFO	app	Application starting	\N	\N
226	2025-03-16 03:00:04.124164	INFO	app	Application starting	\N	\N
227	2025-03-16 03:02:32.986	INFO	app	Application starting	\N	\N
228	2025-03-16 03:02:32.985989	INFO	app	Application starting	\N	\N
229	2025-03-16 03:02:33.006443	INFO	app	Application starting	\N	\N
230	2025-03-16 03:02:33.02126	INFO	app	Application starting	\N	\N
231	2025-03-16 03:19:22.43114	INFO	app	Application starting	\N	\N
232	2025-03-16 03:19:22.431151	INFO	app	Application starting	\N	\N
233	2025-03-16 03:19:22.465041	INFO	app	Application starting	\N	\N
234	2025-03-16 03:19:22.540642	INFO	app	Application starting	\N	\N
235	2025-03-16 03:20:44.064212	INFO	app	Application starting	\N	\N
236	2025-03-16 03:20:44.11273	INFO	app	Application starting	\N	\N
237	2025-03-16 03:20:44.146347	INFO	app	Application starting	\N	\N
238	2025-03-16 03:20:44.221879	INFO	app	Application starting	\N	\N
239	2025-03-16 03:21:21.62439	ERROR	app	Error loading editor: Object of type datetime is not JSON serializable\nTraceback (most recent call last):\n  File "/home/juanquy/OpenShot/test_app/app.py", line 868, in editor_page\n    project = project_manager.get_project(project_id)\n  File "/home/juanquy/OpenShot/test_app/projects.py", line 66, in get_project\n    self._save_project_file(project_id, project)\n  File "/home/juanquy/OpenShot/test_app/projects.py", line 248, in _save_project_file\n    json.dump(openshot_project, f, indent=2)\n  File "/usr/lib/python3.8/json/__init__.py", line 179, in dump\n    for chunk in iterable:\n  File "/usr/lib/python3.8/json/encoder.py", line 431, in _iterencode\n    yield from _iterencode_dict(o, _current_indent_level)\n  File "/usr/lib/python3.8/json/encoder.py", line 405, in _iterencode_dict\n    yield from chunks\n  File "/usr/lib/python3.8/json/encoder.py", line 438, in _iterencode\n    o = _default(o)\n  File "/usr/lib/python3.8/json/encoder.py", line 179, in default\n    raise TypeError(f'Object of type {o.__class__.__name__} '\nTypeError: Object of type datetime is not JSON serializable\n	\N	\N
240	2025-03-16 03:26:06.26167	ERROR	app	Error loading editor: Object of type datetime is not JSON serializable\nTraceback (most recent call last):\n  File "/home/juanquy/OpenShot/test_app/app.py", line 868, in editor_page\n    project = project_manager.get_project(project_id)\n  File "/home/juanquy/OpenShot/test_app/projects.py", line 66, in get_project\n    if project:\n  File "/home/juanquy/OpenShot/test_app/projects.py", line 248, in _save_project_file\n  File "/usr/lib/python3.8/json/__init__.py", line 179, in dump\n    for chunk in iterable:\n  File "/usr/lib/python3.8/json/encoder.py", line 431, in _iterencode\n    yield from _iterencode_dict(o, _current_indent_level)\n  File "/usr/lib/python3.8/json/encoder.py", line 405, in _iterencode_dict\n    yield from chunks\n  File "/usr/lib/python3.8/json/encoder.py", line 438, in _iterencode\n    o = _default(o)\n  File "/usr/lib/python3.8/json/encoder.py", line 179, in default\n    raise TypeError(f'Object of type {o.__class__.__name__} '\nTypeError: Object of type datetime is not JSON serializable\n	\N	\N
241	2025-03-16 03:27:03.487445	INFO	app	Application starting	\N	\N
242	2025-03-16 03:27:03.545465	INFO	app	Application starting	\N	\N
243	2025-03-16 03:27:03.62665	INFO	app	Application starting	\N	\N
244	2025-03-16 03:27:03.689772	INFO	app	Application starting	\N	\N
245	2025-03-16 03:27:22.053901	INFO	app	Application starting	\N	\N
246	2025-03-16 03:27:22.133059	INFO	app	Application starting	\N	\N
247	2025-03-16 03:27:22.151499	INFO	app	Application starting	\N	\N
248	2025-03-16 03:27:22.196917	INFO	app	Application starting	\N	\N
249	2025-03-16 03:27:34.273943	INFO	app	Application starting	\N	\N
250	2025-03-16 03:27:34.32446	INFO	app	Application starting	\N	\N
251	2025-03-16 03:27:34.327014	INFO	app	Application starting	\N	\N
252	2025-03-16 03:27:34.36178	INFO	app	Application starting	\N	\N
253	2025-03-16 03:28:56.199759	INFO	app	Final project structure before template rendering: {"id": "51274d3d-8755-44ac-94c3-8c102b6e1715", "name": "Social Media Video", "description": "Video optimized for social media platforms", "user_id": "9098d630-f606-40f9-b2dd-51167540ed71", "created_at": "2025-03-16T00:50:18.842912", "updated_at": "2025-03-16T00:50:18.842912", "timeline": {"duration": 60.0, "width": 1920, "height": 1080, "fps": {"num": 30, "den": 1}, "sample_rate": 48000, "channels": 2, "channel_layout": 3, "tracks": []}, "assets": []}	\N	\N
254	2025-03-16 03:28:56.248545	ERROR	app	Error loading editor: list object has no element 0\nTraceback (most recent call last):\n  File "/home/juanquy/OpenShot/test_app/app.py", line 938, in editor_page\n    return render_template(\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/flask/templating.py", line 150, in render_template\n    return _render(app, template, context)\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/flask/templating.py", line 131, in _render\n    rv = template.render(context)\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/environment.py", line 1295, in render\n    self.environment.handle_exception()\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/environment.py", line 942, in handle_exception\n    raise rewrite_traceback_stack(source=source)\n  File "/home/juanquy/OpenShot/test_app/templates/editor.html", line 1, in top-level template code\n    {% extends "layout.html" %}\n  File "/home/juanquy/OpenShot/test_app/templates/layout.html", line 96, in top-level template code\n    {% block content %}{% endblock %}\n  File "/home/juanquy/OpenShot/test_app/templates/editor.html", line 699, in block 'content'\n    {% for clip in project.timeline.tracks[0].clips if clip.asset_type == 'video' %}\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/environment.py", line 490, in getattr\n    return getattr(obj, attribute)\njinja2.exceptions.UndefinedError: list object has no element 0\n	\N	\N
255	2025-03-16 03:31:14.496788	INFO	app	Application starting	\N	\N
256	2025-03-16 03:31:14.546882	INFO	app	Application starting	\N	\N
257	2025-03-16 03:31:14.584543	INFO	app	Application starting	\N	\N
258	2025-03-16 03:31:14.604899	INFO	app	Application starting	\N	\N
259	2025-03-16 03:34:27.521651	INFO	app	Creating emergency project structure for project_id 51274d3d-8755-44ac-94c3-8c102b6e1715	\N	\N
260	2025-03-16 03:34:27.525089	INFO	app	Final project structure before template rendering: {"id": "51274d3d-8755-44ac-94c3-8c102b6e1715", "name": "Emergency Project", "description": "This project was created as an emergency fix", "user_id": "9098d630-f606-40f9-b2dd-51167540ed71", "created_at": "2025-03-16T03:34:27.522375", "updated_at": "2025-03-16T03:34:27.522383", "timeline": {"tracks": [{"id": "1", "name": "Video Track", "type": "video", "clips": []}, {"id": "2", "name": "Audio Track", "type": "audio", "clips": []}], "duration": 60.0, "scale": 1.0}, "assets": []}	\N	\N
261	2025-03-16 03:36:58.865888	INFO	app	Application starting	\N	\N
262	2025-03-16 03:36:58.918604	INFO	app	Application starting	\N	\N
263	2025-03-16 03:36:59.005769	INFO	app	Application starting	\N	\N
264	2025-03-16 03:36:59.048634	INFO	app	Application starting	\N	\N
265	2025-03-16 03:37:10.472713	INFO	app	Application starting	\N	\N
266	2025-03-16 03:37:10.547314	INFO	app	Application starting	\N	\N
267	2025-03-16 03:37:10.577973	INFO	app	Application starting	\N	\N
268	2025-03-16 03:37:10.629513	INFO	app	Application starting	\N	\N
269	2025-03-16 03:38:58.657426	INFO	app	Final project structure before template rendering: {"id": "51274d3d-8755-44ac-94c3-8c102b6e1715", "name": "Social Media Video", "description": "Video optimized for social media platforms", "user_id": "9098d630-f606-40f9-b2dd-51167540ed71", "created_at": "2025-03-16T00:50:18.842912", "updated_at": "2025-03-16T00:50:18.842912", "timeline": {"duration": 60.0, "width": 1920, "height": 1080, "fps": {"num": 30, "den": 1}, "sample_rate": 48000, "channels": 2, "channel_layout": 3, "tracks": []}, "assets": []}	\N	\N
270	2025-03-16 03:38:58.672766	ERROR	app	Error loading editor: Encountered unknown tag 'endblock'.\nTraceback (most recent call last):\n  File "/home/juanquy/OpenShot/test_app/app.py", line 956, in editor_page\n    return render_template(\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/flask/templating.py", line 149, in render_template\n    template = app.jinja_env.get_or_select_template(template_name_or_list)\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/environment.py", line 1087, in get_or_select_template\n    return self.get_template(template_name_or_list, parent, globals)\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/environment.py", line 1016, in get_template\n    return self._load_template(name, globals)\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/environment.py", line 975, in _load_template\n    template = self.loader.load(self, name, self.make_globals(globals))\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/loaders.py", line 138, in load\n    code = environment.compile(source, name, filename)\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/environment.py", line 771, in compile\n    self.handle_exception(source=source_hint)\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/environment.py", line 942, in handle_exception\n    raise rewrite_traceback_stack(source=source)\n  File "/home/juanquy/OpenShot/test_app/templates/editor.html", line 402, in template\n    {% endblock %}\njinja2.exceptions.TemplateSyntaxError: Encountered unknown tag 'endblock'.\n	\N	\N
271	2025-03-16 03:39:00.84294	INFO	app	Final project structure before template rendering: {"id": "51274d3d-8755-44ac-94c3-8c102b6e1715", "name": "Social Media Video", "description": "Video optimized for social media platforms", "user_id": "9098d630-f606-40f9-b2dd-51167540ed71", "created_at": "2025-03-16T00:50:18.842912", "updated_at": "2025-03-16T00:50:18.842912", "timeline": {"duration": 60.0, "width": 1920, "height": 1080, "fps": {"num": 30, "den": 1}, "sample_rate": 48000, "channels": 2, "channel_layout": 3, "tracks": []}, "assets": []}	\N	\N
272	2025-03-16 03:39:00.854486	ERROR	app	Error loading editor: Encountered unknown tag 'endblock'.\nTraceback (most recent call last):\n  File "/home/juanquy/OpenShot/test_app/app.py", line 956, in editor_page\n    return render_template(\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/flask/templating.py", line 149, in render_template\n    template = app.jinja_env.get_or_select_template(template_name_or_list)\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/environment.py", line 1087, in get_or_select_template\n    return self.get_template(template_name_or_list, parent, globals)\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/environment.py", line 1016, in get_template\n    return self._load_template(name, globals)\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/environment.py", line 975, in _load_template\n    template = self.loader.load(self, name, self.make_globals(globals))\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/loaders.py", line 138, in load\n    code = environment.compile(source, name, filename)\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/environment.py", line 771, in compile\n    self.handle_exception(source=source_hint)\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/environment.py", line 942, in handle_exception\n    raise rewrite_traceback_stack(source=source)\n  File "/home/juanquy/OpenShot/test_app/templates/editor.html", line 402, in template\n    {% endblock %}\njinja2.exceptions.TemplateSyntaxError: Encountered unknown tag 'endblock'.\n	\N	\N
273	2025-03-16 03:40:46.88354	INFO	app	Application starting	\N	\N
274	2025-03-16 03:40:46.918662	INFO	app	Application starting	\N	\N
275	2025-03-16 03:40:46.962269	INFO	app	Application starting	\N	\N
276	2025-03-16 03:40:46.988799	INFO	app	Application starting	\N	\N
277	2025-03-16 03:41:43.853514	INFO	app	Final project structure before template rendering: {"id": "51274d3d-8755-44ac-94c3-8c102b6e1715", "name": "Social Media Video", "description": "Video optimized for social media platforms", "user_id": "9098d630-f606-40f9-b2dd-51167540ed71", "created_at": "2025-03-16T00:50:18.842912", "updated_at": "2025-03-16T00:50:18.842912", "timeline": {"duration": 60.0, "width": 1920, "height": 1080, "fps": {"num": 30, "den": 1}, "sample_rate": 48000, "channels": 2, "channel_layout": 3, "tracks": []}, "assets": []}	\N	\N
278	2025-03-16 03:41:43.90482	ERROR	app	Error loading editor: list object has no element 0\nTraceback (most recent call last):\n  File "/home/juanquy/OpenShot/test_app/app.py", line 956, in editor_page\n    return render_template(\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/flask/templating.py", line 150, in render_template\n    return _render(app, template, context)\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/flask/templating.py", line 131, in _render\n    rv = template.render(context)\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/environment.py", line 1295, in render\n    self.environment.handle_exception()\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/environment.py", line 942, in handle_exception\n    raise rewrite_traceback_stack(source=source)\n  File "/home/juanquy/OpenShot/test_app/templates/editor.html", line 702, in top-level template code\n    {% for clip in project.timeline.tracks[0].clips if clip.asset_type == 'video' %}\n  File "/home/juanquy/openshot_service_venv/lib/python3.8/site-packages/jinja2/environment.py", line 490, in getattr\n    return getattr(obj, attribute)\njinja2.exceptions.UndefinedError: list object has no element 0\n	\N	\N
279	2025-03-16 03:42:04.627819	INFO	app	Application starting	\N	\N
280	2025-03-16 03:42:04.655726	INFO	app	Application starting	\N	\N
281	2025-03-16 03:42:04.695488	INFO	app	Application starting	\N	\N
282	2025-03-16 03:42:04.785084	INFO	app	Application starting	\N	\N
283	2025-03-16 03:42:45.221895	INFO	app	Application starting	\N	\N
284	2025-03-16 03:42:45.250684	INFO	app	Application starting	\N	\N
285	2025-03-16 03:42:45.295113	INFO	app	Application starting	\N	\N
286	2025-03-16 03:42:45.295338	INFO	app	Application starting	\N	\N
287	2025-03-16 03:45:41.597225	INFO	app	Application starting	\N	\N
288	2025-03-16 03:45:41.668537	INFO	app	Application starting	\N	\N
289	2025-03-16 03:45:41.684741	INFO	app	Application starting	\N	\N
290	2025-03-16 03:45:41.74597	INFO	app	Application starting	\N	\N
291	2025-03-16 03:45:56.702054	INFO	app	Application starting	\N	\N
292	2025-03-16 03:45:56.714127	INFO	app	Application starting	\N	\N
293	2025-03-16 03:45:56.798589	INFO	app	Application starting	\N	\N
294	2025-03-16 03:45:56.822651	INFO	app	Application starting	\N	\N
295	2025-03-16 03:46:50.335771	INFO	app	Application starting	\N	\N
296	2025-03-16 03:46:50.390487	INFO	app	Application starting	\N	\N
297	2025-03-16 03:46:50.449023	INFO	app	Application starting	\N	\N
298	2025-03-16 03:46:50.528486	INFO	app	Application starting	\N	\N
299	2025-03-16 03:55:51.260336	INFO	app	Application starting	\N	\N
300	2025-03-16 03:55:51.345611	INFO	app	Application starting	\N	\N
301	2025-03-16 03:55:51.429744	INFO	app	Application starting	\N	\N
302	2025-03-16 03:55:51.428212	INFO	app	Application starting	\N	\N
303	2025-03-16 03:56:48.979227	INFO	app	Application starting	\N	\N
304	2025-03-16 03:56:49.023674	INFO	app	Application starting	\N	\N
305	2025-03-16 03:56:49.028637	INFO	app	Application starting	\N	\N
306	2025-03-16 03:56:49.10242	INFO	app	Application starting	\N	\N
307	2025-03-16 04:07:26.931758	INFO	app	Application starting	\N	\N
308	2025-03-16 04:07:26.943091	INFO	app	Application starting	\N	\N
309	2025-03-16 04:07:26.949691	INFO	app	Application starting	\N	\N
310	2025-03-16 04:07:27.016755	INFO	app	Application starting	\N	\N
311	2025-03-16 04:17:06.509279	INFO	app	Loading editor for project_id: 51274d3d-8755-44ac-94c3-8c102b6e1715, user_id: 9098d630-f606-40f9-b2dd-51167540ed71	\N	\N
312	2025-03-16 04:17:06.513934	INFO	app	Final project structure before template rendering: {"id": "51274d3d-8755-44ac-94c3-8c102b6e1715", "name": "Social Media Video", "description": "Video optimized for social media platforms", "user_id": "9098d630-f606-40f9-b2dd-51167540ed71", "created_at": "2025-03-16T00:50:18.842912", "updated_at": "2025-03-16T00:50:18.842912", "timeline": {"duration": 60.0, "width": 1920, "height": 1080, "fps": {"num": 30, "den": 1}, "sample_rate": 48000, "channels": 2, "channel_layout": 3, "tracks": []}, "assets": []}	\N	\N
\.


--
-- Data for Name: system_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_settings (key, value, updated_at) FROM stdin;
landing_page_settings	{"hero": {"title": "FLUX58 AI MEDIA LABS", "subtitle": "Create stunning videos with our AI-powered platform", "text": "No downloads required. Edit from anywhere with our cloud-based video editor. Powered by IBM POWER8 architecture.", "bg_color": "#343a40", "text_color": "#ffffff", "image": "img/custom/openshot-banner.jpg", "bg_image_overlay": false}, "features": {"title": "Key Features", "accent_color": "#007bff", "cards": [{"icon": "bi-cloud-arrow-up", "title": "Cloud-Powered", "text": "Edit videos directly in your browser with no software to install."}, {"icon": "bi-cpu", "title": "AI Processing", "text": "Advanced AI-based video processing for stunning results."}, {"icon": "bi-hdd", "title": "Secure Storage", "text": "Your projects are safely stored in our secure cloud environment."}]}, "cta": {"title": "Start Creating Amazing Videos Today", "subtitle": "Join thousands of content creators who trust FLUX58", "button_text": "Start Creating Now", "button_color": "#007bff"}, "navbar": {"brand_text": "FLUX58 AI MEDIA LABS", "bg_color": "#212529", "text_color": "#ffffff", "logo": "img/custom/FLUXLOGO1.png", "menu_items": [{"text": "Home", "url": "/", "visible": true}, {"text": "Dashboard", "url": "/dashboard", "visible": true, "requires_login": true}, {"text": "Projects", "url": "/projects", "visible": true, "requires_login": true}, {"text": "Credits", "url": "/credits", "visible": true, "requires_login": true}, {"text": "Pricing", "url": "/pricing", "visible": true}]}}	2025-03-16 00:46:31.680227
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
9098d630-f606-40f9-b2dd-51167540ed71	test	scrypt:32768:8:1$ZaPxvLk98H4x0ifk$f588856b8e65f564625057a5f438621e0651ddde9a5e8a853f30017fac93998bbdfa155e41917938f3d9c65dfe8a642212467c6ec4d11f655efe29306206a122	test@example.com	2025-03-16 00:07:24.421177	user
\.


--
-- Name: system_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.system_logs_id_seq', 312, true);


--
-- Name: assets assets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (id);


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
-- Name: exports exports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exports
    ADD CONSTRAINT exports_pkey PRIMARY KEY (id);


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
-- Name: assets assets_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


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
-- Name: exports exports_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exports
    ADD CONSTRAINT exports_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON DELETE CASCADE;


--
-- Name: exports exports_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exports
    ADD CONSTRAINT exports_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


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

