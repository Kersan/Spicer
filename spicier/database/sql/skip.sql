CREATE TABLE IF NOT EXISTS "skip" (
    "id" SERIAL NOT NULL,
    "server" character varying(50),
    "user" character varying(50),
    CONSTRAINT "skip_pkey" PRIMARY KEY ("id")
);
