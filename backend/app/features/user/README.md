# features/user

Owns the platform user (the interview candidate).

Responsibility: user persistence and lookup. Authentication is a separate,
later concern; for now a user is who an interview belongs to.

Files: `models.py` (User), `repository.py` (UserRepository).
