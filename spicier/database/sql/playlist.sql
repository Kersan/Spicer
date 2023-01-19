CREATE TABLE IF NOT EXISTS "playlist" (
    "user" character varying(32) NOT NULL,
    "name" character varying(50),
    "title" character varying(512),
    "link" character varying(128),
    CONSTRAINT "playlist_pkey" PRIMARY KEY ("user")
);