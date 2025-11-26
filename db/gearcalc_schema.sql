--
-- PostgreSQL database dump
--

\restrict RK6ezVtuUNwasfsgvTfhOUl8Ye8dJZ5v5BB6St6iu33BgxTkxqHMX5597iRjHvU

-- Dumped from database version 18.0
-- Dumped by pg_dump version 18.0

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
-- Name: gearcalc; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA gearcalc;


ALTER SCHEMA gearcalc OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: mat_table; Type: TABLE; Schema: gearcalc; Owner: postgres
--

CREATE TABLE gearcalc.mat_table (
    id integer NOT NULL,
    material text NOT NULL,
    load_type text NOT NULL,
    sigma_fp_p double precision NOT NULL,
    nf0 double precision NOT NULL
);


ALTER TABLE gearcalc.mat_table OWNER TO postgres;

--
-- Name: mat_table_id_seq; Type: SEQUENCE; Schema: gearcalc; Owner: postgres
--

CREATE SEQUENCE gearcalc.mat_table_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE gearcalc.mat_table_id_seq OWNER TO postgres;

--
-- Name: mat_table_id_seq; Type: SEQUENCE OWNED BY; Schema: gearcalc; Owner: postgres
--

ALTER SEQUENCE gearcalc.mat_table_id_seq OWNED BY gearcalc.mat_table.id;


--
-- Name: module_table; Type: TABLE; Schema: gearcalc; Owner: postgres
--

CREATE TABLE gearcalc.module_table (
    series text NOT NULL,
    m double precision NOT NULL
);


ALTER TABLE gearcalc.module_table OWNER TO postgres;

--
-- Name: yf1_table; Type: TABLE; Schema: gearcalc; Owner: postgres
--

CREATE TABLE gearcalc.yf1_table (
    z1 integer NOT NULL,
    x double precision NOT NULL,
    yf1 double precision NOT NULL
);


ALTER TABLE gearcalc.yf1_table OWNER TO postgres;

--
-- Name: mat_table id; Type: DEFAULT; Schema: gearcalc; Owner: postgres
--

ALTER TABLE ONLY gearcalc.mat_table ALTER COLUMN id SET DEFAULT nextval('gearcalc.mat_table_id_seq'::regclass);


--
-- Data for Name: mat_table; Type: TABLE DATA; Schema: gearcalc; Owner: postgres
--

COPY gearcalc.mat_table (id, material, load_type, sigma_fp_p, nf0) FROM stdin;
1	Стали 20Х и 40Х (цементация)	Нереверсивная	300	4000000
2	Стали 20Х и 40Х (цементация)	Реверсивная	220	4000000
3	Сталь 30ХГТ	Нереверсивная	300	4000000
4	Сталь 30ХГТ	Реверсивная	220	4000000
5	Сталь 40Х (азотирование)	Нереверсивная	240	4000000
6	Сталь 40Х (азотирование)	Реверсивная	215	4000000
7	Сталь 40ХФА (закалка + отпуск)	Нереверсивная	290	4000000
8	Сталь 40ХФА (закалка + отпуск)	Реверсивная	260	4000000
9	Чугун СЧ 32–52	Нереверсивная	115	1000000
10	Чугун СЧ 32–52	Реверсивная	80	1000000
11	Высокопрочный чугун ВЧ 30–2	Нереверсивная	120	1000000
12	Высокопрочный чугун ВЧ 30–2	Реверсивная	85	1000000
13	Стальное литьё 40ХЛ	Нереверсивная	135	4000000
14	Стальное литьё 40ХЛ	Реверсивная	90	4000000
\.


--
-- Data for Name: module_table; Type: TABLE DATA; Schema: gearcalc; Owner: postgres
--

COPY gearcalc.module_table (series, m) FROM stdin;
1-й	1.25
1-й	1.5
1-й	2
1-й	2.5
1-й	3
1-й	4
1-й	5
1-й	6
1-й	8
1-й	10
1-й	12
2-й	1.375
2-й	1.75
2-й	2.25
2-й	2.75
2-й	3.5
2-й	4.5
2-й	5.5
2-й	7
2-й	9
2-й	11
2-й	14
\.


--
-- Data for Name: yf1_table; Type: TABLE DATA; Schema: gearcalc; Owner: postgres
--

COPY gearcalc.yf1_table (z1, x, yf1) FROM stdin;
18	0.7	3.17
18	0.5	3.38
18	0.3	3.64
18	0.1	4.23
20	0.7	3.22
20	0.5	3.33
20	0.3	3.58
20	0.1	4.11
21	0.7	3.22
21	0.5	3.33
21	0.3	3.58
21	0.1	4.11
22	0.7	3.24
22	0.5	3.31
22	0.3	3.56
22	0.1	4.04
22	-0.1	4.09
24	0.7	3.27
24	0.5	3.27
24	0.3	3.53
24	0.1	3.98
24	-0.1	3.92
25	0.7	3.29
25	0.5	3.25
25	0.3	3.52
25	0.1	3.95
25	-0.1	3.9
\.


--
-- Name: mat_table_id_seq; Type: SEQUENCE SET; Schema: gearcalc; Owner: postgres
--

SELECT pg_catalog.setval('gearcalc.mat_table_id_seq', 14, true);


--
-- Name: mat_table mat_table_pkey; Type: CONSTRAINT; Schema: gearcalc; Owner: postgres
--

ALTER TABLE ONLY gearcalc.mat_table
    ADD CONSTRAINT mat_table_pkey PRIMARY KEY (id);


--
-- Name: mat_table mat_unique; Type: CONSTRAINT; Schema: gearcalc; Owner: postgres
--

ALTER TABLE ONLY gearcalc.mat_table
    ADD CONSTRAINT mat_unique UNIQUE (material, load_type);


--
-- Name: module_table module_unique; Type: CONSTRAINT; Schema: gearcalc; Owner: postgres
--

ALTER TABLE ONLY gearcalc.module_table
    ADD CONSTRAINT module_unique UNIQUE (series, m);


--
-- Name: yf1_table yf1_table_pk; Type: CONSTRAINT; Schema: gearcalc; Owner: postgres
--

ALTER TABLE ONLY gearcalc.yf1_table
    ADD CONSTRAINT yf1_table_pk PRIMARY KEY (z1, x);


--
-- PostgreSQL database dump complete
--

\unrestrict RK6ezVtuUNwasfsgvTfhOUl8Ye8dJZ5v5BB6St6iu33BgxTkxqHMX5597iRjHvU

