from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE "roles" (
    "id" VARCHAR(36) NOT NULL PRIMARY KEY,
    "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(255) NOT NULL UNIQUE,
    "description" TEXT,
    "status" VARCHAR(9) NOT NULL DEFAULT 'active' /* active: active\ninactive: inactive\ncancelled: cancelled */
);
CREATE INDEX "idx_roles_name_3e8175" ON "roles" ("name");
CREATE TABLE "users" (
    "id" VARCHAR(36) NOT NULL PRIMARY KEY,
    "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "username" VARCHAR(255) NOT NULL UNIQUE,
    "passwordHash" VARCHAR(255) NOT NULL,
    "status" VARCHAR(9) NOT NULL DEFAULT 'active' /* active: active\nbanned: banned\nsuspended: suspended */
);
CREATE INDEX "idx_users_email_133a6f" ON "users" ("email");
CREATE INDEX "idx_users_usernam_266d85" ON "users" ("username");
CREATE INDEX "idx_users_status_941fc1" ON "users" ("status");
CREATE TABLE "classes" (
    "id" VARCHAR(36) NOT NULL PRIMARY KEY,
    "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "name" VARCHAR(255) NOT NULL,
    "schedule" TIMESTAMP NOT NULL,
    "slots" INT NOT NULL DEFAULT 10,
    "status" VARCHAR(9) NOT NULL DEFAULT 'active' /* active: active\ninactive: inactive\ncancelled: cancelled */,
    "instructor_id" VARCHAR(36) NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX "idx_classes_name_b0bb56" ON "classes" ("name");
CREATE INDEX "idx_classes_schedul_d890b6" ON "classes" ("schedule");
CREATE INDEX "idx_classes_status_0e3156" ON "classes" ("status");
CREATE INDEX "idx_classes_instruc_a407cf" ON "classes" ("instructor_id");
CREATE TABLE "bookings" (
    "id" VARCHAR(36) NOT NULL PRIMARY KEY,
    "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "status" VARCHAR(9) NOT NULL DEFAULT 'active' /* active: active\ninactive: inactive\ncancelled: cancelled */,
    "class__id" VARCHAR(36) NOT NULL REFERENCES "classes" ("id") ON DELETE CASCADE,
    "user_id" VARCHAR(36) NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_bookings_user_id_db1188" UNIQUE ("user_id", "class__id")
);
CREATE INDEX "idx_bookings_status_8c09c6" ON "bookings" ("status");
CREATE INDEX "idx_bookings_class___0111fc" ON "bookings" ("class__id");
CREATE INDEX "idx_bookings_user_id_22d60c" ON "bookings" ("user_id");
CREATE TABLE "refresh_tokens" (
    "id" VARCHAR(36) NOT NULL PRIMARY KEY,
    "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "token" VARCHAR(255) NOT NULL UNIQUE,
    "expiresAt" TIMESTAMP NOT NULL,
    "revoked" TIMESTAMP NOT NULL,
    "status" VARCHAR(9) NOT NULL DEFAULT 'active' /* active: active\ninactive: inactive\ncancelled: cancelled */,
    "user_id" VARCHAR(36) NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX "idx_refresh_tok_user_id_9ddaa8" ON "refresh_tokens" ("user_id");
CREATE TABLE "user_roles" (
    "id" VARCHAR(36) NOT NULL PRIMARY KEY,
    "createdAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "description" TEXT,
    "status" VARCHAR(9) NOT NULL DEFAULT 'active' /* active: active\ninactive: inactive\ncancelled: cancelled */,
    "role_id" VARCHAR(36) NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE,
    "user_id" VARCHAR(36) NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_user_roles_user_id_63f1a8" UNIQUE ("user_id", "role_id")
);
CREATE INDEX "idx_user_roles_role_id_c4864d" ON "user_roles" ("role_id");
CREATE INDEX "idx_user_roles_user_id_31077e" ON "user_roles" ("user_id");
CREATE INDEX "idx_user_roles_user_id_63f1a8" ON "user_roles" ("user_id", "role_id");
CREATE TABLE "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
