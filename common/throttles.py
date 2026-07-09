from __future__ import annotations

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class BurstAnonThrottle(AnonRateThrottle):
    scope = "anon_burst"


class AuthBurstThrottle(UserRateThrottle):
    scope = "auth_burst"


class LoginThrottle(AnonRateThrottle):
    scope = "login"


class RegisterThrottle(AnonRateThrottle):
    scope = "register"
