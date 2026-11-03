import hashlib
import hmac
import secrets
import sqlite3
from datetime import datetime, timedelta

from config import DATABASE_PATH


_INITIAL_ADMIN_PASSWORD = "Admin123"
_HASH_ALGORITHM = "pbkdf2_sha256"
_HASH_ITERATIONS = 600_000


def _hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, _HASH_ITERATIONS
    )
    return f"{_HASH_ALGORITHM}${_HASH_ITERATIONS}${salt.hex()}${digest.hex()}"


def _verify_password(password, encoded_hash):
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded_hash.split("$")
        if algorithm != _HASH_ALGORITHM:
            return False
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def ensure_admin_password_store():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_password (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                password_hash TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        row = connection.execute(
            "SELECT 1 FROM admin_password WHERE id = 1"
        ).fetchone()
        if row is None:
            connection.execute(
                "INSERT INTO admin_password (id, password_hash) VALUES (1, ?)",
                (_hash_password(_INITIAL_ADMIN_PASSWORD),),
            )


def verify_admin_password(password):
    ensure_admin_password_store()
    with sqlite3.connect(DATABASE_PATH) as connection:
        row = connection.execute(
            "SELECT password_hash FROM admin_password WHERE id = 1"
        ).fetchone()
    return row is not None and _verify_password(password, row[0])


MIN_PASSWORD_LENGTH = 8


def change_admin_password(old_password, new_password, confirm_password):
    """Returns (success, message)."""
    if not verify_admin_password(old_password):
        return False, "Old password is incorrect."
    if len(new_password) < MIN_PASSWORD_LENGTH:
        return False, f"New password must be at least {MIN_PASSWORD_LENGTH} characters."
    if new_password != confirm_password:
        return False, "New password and confirm password do not match."
    if new_password == old_password:
        return False, "New password must be different from the old password."
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            "UPDATE admin_password SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1",
            (_hash_password(new_password),),
        )
    return True, "Admin password changed successfully."


MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 5
_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def ensure_login_audit_store():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS admin_login_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attempted_at TEXT NOT NULL,
                success INTEGER NOT NULL,
                source TEXT
            )
            """
        )


def _now():
    return datetime.now()


def _log_attempt(success, source):
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            "INSERT INTO admin_login_audit (attempted_at, success, source) VALUES (?, ?, ?)",
            (_now().strftime(_TIME_FORMAT), 1 if success else 0, source),
        )


def lockout_remaining_seconds():
    """Seconds left on the lockout, or 0 when login is allowed."""
    ensure_login_audit_store()
    with sqlite3.connect(DATABASE_PATH) as connection:
        last_success = connection.execute(
            "SELECT MAX(id) FROM admin_login_audit WHERE success = 1"
        ).fetchone()[0] or 0
        rows = connection.execute(
            "SELECT attempted_at FROM admin_login_audit WHERE success = 0 AND id > ? "
            "ORDER BY id DESC LIMIT ?",
            (last_success, MAX_FAILED_ATTEMPTS),
        ).fetchall()
    if len(rows) < MAX_FAILED_ATTEMPTS:
        return 0
    last_failure = datetime.strptime(rows[0][0], _TIME_FORMAT)
    remaining = last_failure + timedelta(minutes=LOCKOUT_MINUTES) - _now()
    return max(0, int(remaining.total_seconds()) + 1) if remaining.total_seconds() > 0 else 0


def attempt_admin_login(password, source="Admin Login"):
    """Verify the password with lockout and audit. Returns (success, message)."""
    remaining = lockout_remaining_seconds()
    if remaining:
        minutes, seconds = divmod(remaining, 60)
        return False, f"Too many failed attempts. Try again in {minutes}m {seconds}s."
    success = verify_admin_password(password)
    _log_attempt(success, source)
    if success:
        return True, ""
    if lockout_remaining_seconds():
        return False, f"Wrong Password. Login locked for {LOCKOUT_MINUTES} minutes."
    with sqlite3.connect(DATABASE_PATH) as connection:
        last_success = connection.execute(
            "SELECT MAX(id) FROM admin_login_audit WHERE success = 1"
        ).fetchone()[0] or 0
        failed = connection.execute(
            "SELECT COUNT(*) FROM admin_login_audit WHERE success = 0 AND id > ?",
            (last_success,),
        ).fetchone()[0]
    return False, f"Wrong Password. {MAX_FAILED_ATTEMPTS - failed} attempt(s) left."
