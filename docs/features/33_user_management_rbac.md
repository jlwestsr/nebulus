# Feature: User Management & RBAC

## 1. Overview
**Branch**: `feat/user-management`

Implement detailed user management and Role-Based Access Control (RBAC) to manage permissions beyond simple authentication.

## 2. Requirements
List specific, testable requirements:
- [ ] **User Roles**:
    - [ ] Define roles: `admin`, `user`, `viewer`.
    - [ ] Store roles in User metadata or database.
- [ ] **Admin Dashboard**:
    - [ ] UI to list all users.
    - [ ] Ability to promote/demote users.
    - [ ] Ability to ban/delete users.
- [ ] **Permissions**:
    - [ ] Restrict "Delete Chat", "Configure Models" to Admins.
    - [ ] Restrict "Image Gen" to specific roles (optional).

## 3. Technical Implementation
- **Modules**: `gantry/auth/rbac.py`, `gantry/ui/admin_dashboard.py`
- **Dependencies**: N/A (Extend existing Auth/DB).
- **Data**: Update User schema in DB.

## 4. Verification Plan
**Automated Tests**:
- [ ] Script: `pytest tests/auth/test_rbac.py`
- [ ] Logic Verified: Users cannot access Admin routes, Admins can access everything.

**Manual Verification**:
- [ ] Step 1: Login as standard user. Try to access Admin panel. Verify denied.
- [ ] Step 2: Login as Admin. Promote another user.
- [ ] Step 3: Verify promoted user has new permissions.

## 5. Workflow Checklist
Follow the AI Behavior strict workflow:
- [ ] **Branch**: Created `feat/user-management` branch?
- [ ] **Work**: Implemented changes?
- [ ] **Test**: All tests pass (`pytest`)?
- [ ] **Doc**: Updated `README.md` and `walkthrough.md`?
- [ ] **Data**: `git add .`, `git commit`, `git push`?
