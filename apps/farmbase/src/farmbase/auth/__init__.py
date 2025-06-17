from propelauth_fastapi import init_auth

auth = init_auth(
    "https://6366051.propelauthtest.com",
    "55d4e0fdd0fc9dd65350587b34d5a25982781c1e7eea7b826469337db8f912140473230a1b5a3c6ca37acb21d0ef25fb",
    debug_mode=True,
    log_exceptions=True,
)
