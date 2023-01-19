CREATE TABLE IF NOT EXISTS "queue" (
    "server" character varying(32) NOT NULL,
    "index" integer,
    "isPlaying" boolean,
    "requester" character varying(50),
    "textChannel" character varying(50),
    "track" character varying(128),
    "title" character varying(512),
    "duration" integer,
    CONSTRAINT "queue_pkey" PRIMARY KEY ("server")
);