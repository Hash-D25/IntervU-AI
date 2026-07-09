# 04 - Resume Upload

## Goal

Let authenticated users upload a **PDF resume**. Validate it, store the file on
disk with a unique name, and persist **metadata + relative file path** in the
database. **No parsing yet.**

## Scope

**In:** PDF validation (magic bytes + MIME), max size (5 MB), local file storage
behind an interface, `resumes` table, upload/list/get/delete routes, tests,
migration `0003_resumes`.

**Out:** resume parsing, skills extraction, vector indexing, S3 storage impl.

---

## Architecture

```
POST /resumes/upload  (router - Upload Controller)
        │
        ▼
   ResumeService       (validate → store file → persist metadata → commit)
        │
        ├── LocalFileStorageService   (unique path on disk)
        └── ResumeRepository          (metadata only)
```

| Layer | File | Role |
| ----- | ---- | ---- |
| Controller | `router.py` | Multipart upload, auth, DTO mapping |
| Service | `service.py` | Orchestration + commit + rollback cleanup |
| Storage | `storage.py` | `FileStorageService` protocol + local impl |
| Repository | `repository.py` | DB access, user-scoped queries |
| Validators | `validators.py` | Chunked read + PDF magic/MIME checks |

Routes are **protected** with `CurrentUserDep`. Business features never touch
the filesystem directly.

---

## Database - `resumes`

| Column | Notes |
| ------ | ----- |
| `user_id` | FK → users, CASCADE |
| `original_filename` | Client filename |
| `stored_path` | **Relative** path, e.g. `resumes/{user_id}/{uuid}.pdf` |
| `file_size_bytes` | |
| `content_type` | `application/pdf` |

File bytes are **never** stored in Postgres.

---

## Validation

- **Magic bytes** must start with `%PDF-` (don't trust extension alone).
- **MIME** must be `application/pdf` when the client sends a content type.
- **Max size** - `RESUME_MAX_SIZE_MB` (default 5); read in 64 KB chunks and
  fail fast with **413**.
- **Empty file** → **400**.

---

## File storage

Backends are selected with `RESUME_STORAGE_BACKEND`:

| Backend | Value | `stored_path` holds | `file_url` in response |
| ------- | ----- | ----------------- | ---------------------- |
| Local disk | `local` (default) | relative path | `null` |
| Cloudinary | `cloudinary` | Cloudinary public_id | secure HTTPS URL |

- On DB failure after save: **rollback + delete** the orphaned file.
- `uploads/` is gitignored (local backend only).

**Cloudinary:** PDFs upload as **raw** resources. Public ID:
`resumes/{user_id}/{uuid}`. SDK calls run in `asyncio.to_thread`. Credentials
from [Cloudinary Console](https://console.cloudinary.com/) → Dashboard.

---

## API (`/api/v1/resumes`)

| Method | Path | Auth | Response |
| ------ | ---- | ---- | -------- |
| POST | `/upload` | yes | `ResumeResponse` (201) |
| GET | `/` | yes | list of resumes |
| GET | `/{id}` | yes | single resume |
| DELETE | `/{id}` | yes | 204 |

Ownership enforced in the repository (`get_for_user`).

---

## Config

```env
RESUME_STORAGE_BACKEND=local          # or cloudinary
RESUME_UPLOAD_DIR=uploads
RESUME_MAX_SIZE_MB=5
CLOUDINARY_CLOUD_NAME=                # required when backend=cloudinary
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
```

---

## Migration

`0003_resumes` - applied live → `0003_resumes (head)`.

---

## Testing

- **Unit:** PDF validators, unique storage paths, delete.
- **Integration:** upload → list → get → delete; 401 without token; 400 for
  non-PDF. Uses temp upload dir via dependency override.

```bash
pytest -q   # 25 passed (including resume tests)
```

---

## How to try it (Swagger)

1. Register + login → copy `access_token`.
2. **Authorize** with `Bearer <token>`.
3. `POST /api/v1/resumes/upload` → choose a PDF file.
4. `GET /api/v1/resumes/` to list uploads.

---

## What's next

Iteration 05 - **resume parsing** (extract skills, projects, technologies,
experience) using the stored file path, keeping prompts in `app/ai/prompts`.
