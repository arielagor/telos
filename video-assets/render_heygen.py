#!/usr/bin/env python3
"""Render the Telos walkthrough beats with HeyGen Avatar V (v3), per beat.

Resumable: tracks submitted video_ids in heygen/render-ids.json, polls until each is
completed, downloads to heygen/<beat>.mp4. Avatar V gives natural hand gestures (v2 freezes
hands). Renders carry light-gray pillarbars -> fixed later in compositing (crop + blur-fill).

Usage:
  python render_heygen.py            # submit any pending beats, then poll+download all
  python render_heygen.py status     # just print status
Env: HEYGEN_API_KEY
"""
import json, os, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
HEYGEN = os.path.join(HERE, "heygen")
os.makedirs(HEYGEN, exist_ok=True)
IDS = os.path.join(HEYGEN, "render-ids.json")
KEY = os.environ.get("HEYGEN_API_KEY", "")
CREATE = "https://api.heygen.com/v3/videos"
STATUS = "https://api.heygen.com/v1/video_status.get?video_id="


def _req(url, method="GET", body=None):
    data = json.dumps(body).encode() if body is not None else None
    headers = {"X-Api-Key": KEY, "Content-Type": "application/json", "Accept": "application/json"}
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"_http_error": e.code, "_body": e.read().decode("utf-8", "ignore")[:500]}


def load_ids():
    return json.load(open(IDS)) if os.path.exists(IDS) else {}


def save_ids(d):
    json.dump(d, open(IDS, "w"), indent=2)


def submit(beats, avatar_id, voice_id, title):
    ids = load_ids()
    for b in beats:
        bid = b["id"]
        if ids.get(bid, {}).get("video_id"):
            continue
        body = {"type": "avatar", "avatar_id": avatar_id, "engine": {"type": "avatar_v"},
                "script": b["script"], "voice_id": voice_id, "resolution": "1080p",
                "aspect_ratio": "16:9", "title": f"{title} {bid}"}
        resp = _req(CREATE, "POST", body)
        vid = (resp.get("data") or {}).get("video_id")
        if vid:
            ids[bid] = {"video_id": vid, "status": "processing"}
            print(f"submitted {bid} -> {vid}")
        else:
            print(f"SUBMIT FAILED {bid}: {json.dumps(resp)[:400]}")
        save_ids(ids)
        time.sleep(2)
    return ids


def poll_and_download(beats):
    ids = load_ids()
    pending = {b["id"] for b in beats if not os.path.exists(os.path.join(HEYGEN, b["id"] + ".mp4"))}
    while pending:
        for bid in sorted(list(pending)):
            vid = ids.get(bid, {}).get("video_id")
            if not vid:
                pending.discard(bid); continue
            resp = _req(STATUS + vid)
            d = resp.get("data") or {}
            st = d.get("status")
            ids[bid]["status"] = st
            if st == "completed":
                url = d.get("video_url")
                out = os.path.join(HEYGEN, bid + ".mp4")
                try:
                    urllib.request.urlretrieve(url, out)
                    print(f"downloaded {bid} ({os.path.getsize(out)//1024} KB)")
                    pending.discard(bid)
                except Exception as e:
                    print(f"download failed {bid}: {e}")
            elif st == "failed":
                print(f"RENDER FAILED {bid}: {json.dumps(d)[:300]}")
                pending.discard(bid)
            else:
                print(f"{bid}: {st}")
        save_ids(ids)
        if pending:
            time.sleep(20)
    print("all beats downloaded")


def main():
    cfg = json.load(open(os.path.join(HERE, "beats.json")))
    if not KEY:
        print("HEYGEN_API_KEY unset"); return 1
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        print(json.dumps(load_ids(), indent=2)); return 0
    submit(cfg["beats"], cfg["avatar_id"], cfg["voice_id"], cfg.get("title", "Telos"))
    poll_and_download(cfg["beats"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
