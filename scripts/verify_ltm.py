import requests
import time

BASE_URL = "http://localhost:8002"


def _make_request(method, endpoint, **kwargs):
    try:
        url = f"{BASE_URL}{endpoint}"
        resp = requests.request(method, url, **kwargs)
        resp.raise_for_status()
        return resp.json() if resp.content else {}
    except Exception as e:
        print(f"   Failed: {e}")
        try:
            print(resp.text)
        except Exception:
            pass
        return None


def verify_create_conversation():
    print("\n1. Create Conversation")
    data = _make_request(
        "POST",
        "/api/conversations",
        json={"topic": "Integration Test", "user_id": "test_user"},
    )
    if data:
        print(f"   Success: Created conversation {data['id']}")
        return data["id"]
    return None


def verify_add_message(conv_id):
    print("\n2. Add Message")
    data = _make_request(
        "POST",
        f"/api/conversations/{conv_id}/messages",
        json={"content": "Hello World", "sender": "user", "receiver": "ai"},
    )
    if data:
        print(f"   Success: Added message {data['id']}")


def verify_get_messages(conv_id):
    print("\n3. Get Messages")
    msgs = _make_request("GET", f"/api/conversations/{conv_id}/messages")
    if msgs is not None:
        print(f"   Success: Retrieved {len(msgs)} messages")
        if len(msgs) != 1 or msgs[0]["content"] != "Hello World":
            print("   Error: Message content mismatch")


def verify_set_preference():
    print("\n4. Set User Preference")
    res = _make_request(
        "POST",
        "/api/users/test_user/preferences",
        json={"key": "theme", "value": "dark"},
    )
    if res is not None:
        print("   Success: Set preference")


def verify_get_preference():
    print("\n5. Get User Preference")
    prefs = _make_request("GET", "/api/users/test_user/preferences")
    if prefs:
        print(f"   Success: Start prefs: {prefs}")
        if prefs.get("theme") != "dark":
            print("   Error: Preference mismatch")


def verify_update_conversation(conv_id):
    print("\n6. Update Conversation")
    res = _make_request(
        "PUT", f"/api/conversations/{conv_id}", json={"topic": "Updated Topic"}
    )
    if res is not None:
        print("   Success: Updated topic")


def verify_delete_conversation(conv_id):
    print("\n7. Delete Conversation")
    res = _make_request("DELETE", f"/api/conversations/{conv_id}")
    if res is not None:
        print("   Success: Deleted conversation")


def test_endpoints():
    print("Testing LTM Endpoints...")
    conv_id = verify_create_conversation()
    if not conv_id:
        return

    verify_add_message(conv_id)
    verify_get_messages(conv_id)
    verify_set_preference()
    verify_get_preference()
    verify_update_conversation(conv_id)
    verify_delete_conversation(conv_id)


if __name__ == "__main__":
    time.sleep(2)
    test_endpoints()
