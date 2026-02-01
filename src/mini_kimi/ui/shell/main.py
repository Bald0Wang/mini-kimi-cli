import sys
import os
from typing import Optional

# 确保能导入 mini_kimi 包
# 在实际项目中，这通常通过安装包或设置 PYTHONPATH 来解决
# 这里为了简单，我们动态添加 src 目录到 sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
# current: src/mini_kimi/ui/shell
# need: src
src_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, src_dir)

from mini_kimi.soul.soul import Soul
from mini_kimi.storage.session_store import SessionStore

def _print_banner():
    banner = r"""
 __  __ _       _   _   _ _           _   _   _
|  \/  (_)_ __ (_) | | / (_) ___ ___ | | | | (_)
| |\/| | | '_ \| | | |/ /| |/ _ / __|| | | | | |
| |  | | | | | | | |   < | |  __\__ \| | | |_| |
|_|  |_|_|_| |_|_| |_|\_\|_|\___|___/|_|  \___/|_|

Mini Kimi CLI — your terminal coding sidekick
"""
    print(banner.rstrip("\n"))

def _print_help():
    print(
        "\nCommands:\n"
        "  /help                Show this help\n"
        "  /exit                Exit\n"
        "  /clear               Start a new session (keeps history on disk)\n"
        "  /session             Show current session + recent sessions\n"
        "  /session load <id>   Load a specific session\n"
    )


def _get_store() -> SessionStore:
    base_dir = os.environ.get("MINI_KIMI_HOME") or os.path.join(os.getcwd(), ".mini_kimi")
    return SessionStore(base_dir=base_dir)


def _start_new_session(store: SessionStore) -> tuple[Soul, str]:
    session_id = store.create_session(title="")
    agent = Soul(session_store=store, session_id=session_id)
    return agent, session_id


def _restore_latest_session(store: SessionStore) -> tuple[Optional[Soul], Optional[str]]:
    session_id = store.get_latest_session_id()
    if not session_id:
        return None, None
    messages = store.load_messages(session_id=session_id)
    if not messages:
        return None, None
    agent = Soul(session_store=store, session_id=session_id, initial_messages=messages)
    return agent, session_id


def main():
    _print_banner()
    print("Type '/help' for commands. Type 'exit' or 'quit' to leave.\n")

    store = _get_store()
    agent, session_id = _restore_latest_session(store)
    if agent and session_id:
        print(f"[Session] Restored: {session_id} ({len(agent.messages)} messages)")
    else:
        agent, session_id = _start_new_session(store)
        print(f"[Session] New: {session_id}")

    while True:
        try:
            user_input = input("\n\033[1;36mUser>\033[0m ")
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input.strip():
                continue

            if user_input.startswith("/"):
                parts = user_input.strip().split()
                cmd = parts[0].lower()

                if cmd in ["/help", "/?"]:
                    _print_help()
                    continue

                if cmd == "/exit":
                    break

                if cmd == "/clear":
                    agent, session_id = _start_new_session(store)
                    print(f"[Session] New: {session_id}")
                    continue

                if cmd == "/session":
                    if len(parts) >= 3 and parts[1].lower() == "load":
                        target_id = parts[2].strip()
                        messages = store.load_messages(session_id=target_id)
                        if not messages:
                            print(f"[Session] Not found or empty: {target_id}")
                            continue
                        agent = Soul(session_store=store, session_id=target_id, initial_messages=messages)
                        session_id = target_id
                        print(f"[Session] Loaded: {session_id} ({len(agent.messages)} messages)")
                        continue

                    print(f"[Session] Current: {session_id} ({len(agent.messages)} messages)")
                    recent = store.list_sessions(limit=5)
                    if recent:
                        print("[Session] Recent:")
                        for s in recent:
                            title = f" - {s.title}" if s.title else ""
                            print(f"  {s.session_id}{title}  updated={s.updated_at}")
                    continue

                print(f"[Unknown Command] {user_input.strip()} (try /help)")
                continue
                
            agent.run(user_input)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
