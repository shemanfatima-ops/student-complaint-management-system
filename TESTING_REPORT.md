# Student Complaint Management System - Testing Report

## Project modules

| Module | Purpose and observed implementation |
|---|---|
| User Authentication | `routes/auth.py` handles student registration, case-normalized email lookup, password hashing/verification, login, logout, and the protected profile route. |
| Student Profile | `routes/auth.py` and `templates/profile.html` display the logged-in student's name from the session. |
| Complaint Management | `routes/complaints.py` accepts a category and description, creates a complaint ID, saves the complaint, and shows a submission confirmation. Complaint submission now requires an authenticated session. |
| Database Management | `models/database.py` provides the configured SQLite connection and creates the users and complaints tables. `app.py` configures the production database path and initializes the schema when run as a script. |
| User Model | `models/user.py` hashes passwords and verifies them. Registration currently performs its user insert in the authentication route. |
| Templates and Styling | `templates/` contains the registration, login, profile, and complaint pages. `static/css/style.css` styles the shared pages. The complaint pages currently use their own basic markup. |

## Testing approach

The suite uses pytest and Flask's test client. Each test receives a temporary SQLite database under pytest's `tmp_path`; it does not point at or modify the project's `complaints.db`. Test accounts use reserved `.test` email addresses and synthetic names. The database connections opened by the tests are closed, and pytest removes each temporary directory after the test.

Unit tests exercise authentication, user/password and profile behavior, complaint validation and persistence, and SQLite initialization and record access independently. The integration test registers a student, logs in, opens the complaint page, submits a complaint, then joins the saved complaint to the user record to verify ownership.

## Test cases and results

| Test case | Expected result | Actual result |
|---|---|---|
| `test_valid_registration_creates_student` | Registration succeeds; user is stored with a password hash. | PASS |
| `test_invalid_registration_rejects_empty_fields` | Empty required fields are rejected with a validation message. | PASS |
| `test_duplicate_email_is_rejected` | A second registration with the same email is rejected. | PASS |
| `test_valid_login_sets_session` | Correct credentials establish the student session. | PASS |
| `test_incorrect_password_does_not_authenticate` | Incorrect credentials do not establish a session. | PASS |
| `test_logout_clears_session` | Logout clears the session and redirects to login. | PASS |
| `test_profile_redirects_when_not_logged_in` | An unauthenticated profile request redirects to login. | PASS |
| `test_user_password_is_hashed_and_verifiable` | Password hashes differ from plaintext and verify correctly. | PASS |
| `test_student_profile_displays_authenticated_student` | The profile displays the logged-in student's name. | PASS |
| `test_profile_contains_correct_student_information` | The profile session contains the expected student name. | PASS |
| `test_valid_complaint_submission_returns_generated_id` | Valid complaint submission displays an ID in `CMP-XXXXXXXX` format. | PASS |
| `test_complaint_with_empty_fields_is_rejected` | Empty/whitespace complaint fields return HTTP 400. | PASS |
| `test_submitted_complaint_is_saved_with_logged_in_student` | The complaint is stored with the expected content, status, and logged-in user ID. | PASS |
| `test_complaint_submission_requires_login` | An unauthenticated complaint-page request redirects to login. | PASS |
| `test_database_connection_uses_temporary_database` | The database connection uses the test's temporary database path. | PASS |
| `test_table_creation_creates_users_and_complaints_tables` | Initialization creates both required tables. | PASS |
| `test_init_db_can_be_called_more_than_once` | Repeated initialization succeeds. | PASS |
| `test_database_insert_and_retrieve_user` | A user record can be inserted and retrieved. | PASS |
| `test_database_rejects_duplicate_user_email` | SQLite rejects a duplicate user email. | PASS |
| `test_student_registration_login_and_complaint_submission` | Registration, login, complaint page, submission, persistence, and student ownership work together. | PASS |

## Execution results

The complete suite was run with `python -m pytest -v`:

```text
20 passed in 8.07s
```

The individual test modules were also run:

| Test module | Result |
|---|---:|
| Authentication (`test_auth.py`) | 7 passed |
| User and profile (`test_user.py`) | 3 passed |
| Complaints (`test_complaints.py`) | 4 passed |
| Database (`test_database.py`) | 5 passed |
| Integration (`test_integration.py`) | 1 passed |
| **Total** | **20 passed, 0 failed** |

## Missing features and limitations found during inspection

- **Admin management is not implemented:** there are no admin accounts, dashboard, or admin complaint actions.
- **Complaint tracking is not implemented:** the database records a complaint's initial `Pending` status, but there is no route or page to list complaints, check status later, or update status.
- **Complaint subject is not implemented:** the existing submission form and database store category and description only.
- **Student profile details are limited:** the profile displays the name saved in the session; it does not show email or provide profile editing.
- **Validation is limited:** registration checks that name, email, and password are non-empty and relies on SQLite uniqueness for duplicate email. It does not enforce email format server-side or a password-strength policy. Complaint submission checks that category and description are non-empty, but does not enforce a server-side category allowlist.
- **Existing `complaints.db` schema:** inspection found only the existing `users` table. It was not changed during testing; the new complaint table is created by application initialization when the application is run.

## Demonstrating the tests

From the project directory, run the full suite:

```powershell
python -m pytest -v
```

Run an individual module with one of these commands:

```powershell
python -m pytest -v tests/test_auth.py
python -m pytest -v tests/test_user.py
python -m pytest -v tests/test_complaints.py
python -m pytest -v tests/test_database.py
python -m pytest -v tests/test_integration.py
```

The output shows each test name and its `PASSED` result, followed by a summary count. To demonstrate the workflow, run the complete suite first, then run `test_integration.py` to show the end-to-end student complaint flow.
