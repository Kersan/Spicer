CREATE TABLE IF NOT EXISTS "server" (
    "server" character varying(32) NOT NULL,
    "prefix" character varying(10),
    "loop" boolean,
    "loopQueue" boolean,
    "djRole" character varying(50),
    CONSTRAINT "server_pkey" PRIMARY KEY ("server")
);