CREATE TABLE IF NOT EXISTS game_events (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    player TEXT NOT NULL,
    action TEXT NOT NULL,

    xp_delta INT NOT NULL,
    karma_delta INT NOT NULL,
    karma_total INT NOT NULL,

    rank TEXT NOT NULL,

    energy_source TEXT NULL
);

CREATE INDEX IF NOT EXISTS idx_game_events_ts ON game_events(ts);
CREATE INDEX IF NOT EXISTS idx_game_events_action ON game_events(action);
CREATE INDEX IF NOT EXISTS idx_game_events_rank ON game_events(rank);
