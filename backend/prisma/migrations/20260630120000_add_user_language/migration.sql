-- CreateEnum
CREATE TYPE "Language" AS ENUM ('UZ', 'RU');

-- AlterTable
ALTER TABLE "telegram_users" ADD COLUMN     "language" "Language";

