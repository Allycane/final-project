"""
이미 만들어져 있는 chat_sessions / chat_messages 테이블의 FK 제약조건을
ON DELETE CASCADE로 교체하는 1회성 스크립트입니다.

models/chat.py에 ondelete="CASCADE"를 추가했지만, 이건 앞으로 테이블을
"새로 만들 때"만 반영되는 설정입니다. 이미 만들어진 테이블은 저절로 안 바뀌므로
기존 제약조건을 찾아서 지우고 CASCADE 옵션을 붙여 다시 만들어야 합니다.

사용법:
    python scripts/add_cascade_delete_migration.py

주의:
- 운영 DB에 실행하기 전에 반드시 백업을 먼저 떠두세요.
- 이 스크립트는 한 번만 실행하면 됩니다 (이미 CASCADE가 걸려있으면 건너뜁니다).
"""
import os
import sys

from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import engine  # noqa: E402

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# (자식 테이블, FK 컬럼, 부모 테이블, 부모 PK 컬럼)
TARGET_FKS = [
    ("chat_sessions", "user_id", "users", "id"),
    ("chat_messages", "session_id", "chat_sessions", "id"),
]


def find_fk_constraint(conn, table: str, column: str, ref_table: str) -> tuple[str, str] | None:
    """
    information_schema에서 실제 FK 제약조건 이름과 현재 ON DELETE 규칙을 조회합니다.
    반환값: (constraint_name, delete_rule) 또는 없으면 None
    """
    row = conn.execute(
        text(
            """
            SELECT rc.CONSTRAINT_NAME, rc.DELETE_RULE
            FROM information_schema.REFERENTIAL_CONSTRAINTS rc
            JOIN information_schema.KEY_COLUMN_USAGE kcu
              ON rc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
             AND rc.CONSTRAINT_SCHEMA = kcu.CONSTRAINT_SCHEMA
            WHERE rc.CONSTRAINT_SCHEMA = DATABASE()
              AND kcu.TABLE_NAME = :table
              AND kcu.COLUMN_NAME = :column
              AND kcu.REFERENCED_TABLE_NAME = :ref_table
            """
        ),
        {"table": table, "column": column, "ref_table": ref_table},
    ).first()
    return (row[0], row[1]) if row else None


def apply_cascade(conn, table: str, column: str, ref_table: str, ref_column: str):
    existing = find_fk_constraint(conn, table, column, ref_table)

    if existing and existing[1] == "CASCADE":
        print(f"✅ {table}.{column} -> {ref_table}.{ref_column} 는 이미 CASCADE가 설정돼 있습니다. 건너뜁니다.")
        return

    if existing:
        constraint_name = existing[0]
        print(f"🔧 기존 제약조건 발견: {constraint_name} (현재 규칙: {existing[1]}) -> 삭제 후 재생성합니다.")
        conn.execute(text(f"ALTER TABLE `{table}` DROP FOREIGN KEY `{constraint_name}`"))
    else:
        print(f"ℹ️ {table}.{column}에 걸린 FK 제약조건이 없습니다 -> 새로 추가합니다.")

    new_constraint_name = f"fk_{table}_{column}_cascade"
    conn.execute(
        text(
            f"""
            ALTER TABLE `{table}`
            ADD CONSTRAINT `{new_constraint_name}`
            FOREIGN KEY (`{column}`) REFERENCES `{ref_table}` (`{ref_column}`)
            ON DELETE CASCADE
            """
        )
    )
    print(f"✅ {table}.{column} -> {ref_table}.{ref_column} 에 ON DELETE CASCADE 적용 완료 ({new_constraint_name})")


def main():
    with engine.begin() as conn:
        for table, column, ref_table, ref_column in TARGET_FKS:
            apply_cascade(conn, table, column, ref_table, ref_column)

    print("\n모든 작업이 끝났습니다. users 테이블에서 회원을 삭제하면")
    print("chat_sessions -> chat_messages까지 자동으로 함께 삭제됩니다.")


if __name__ == "__main__":
    main()