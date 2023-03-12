CREATE TABLE IF NOT EXISTS "server" (
    "id" bigint NOT NULL,
    "prefix" character varying(10),
    "channel" bigint,
    CONSTRAINT "server_pkey" PRIMARY KEY ("id")
);