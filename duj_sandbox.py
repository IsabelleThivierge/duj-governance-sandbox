import json, os, time

WORKSPACE = "."
STATE = "state.json"
PROPOSALS = "proposals.jsonl"
COMMITS = "commits.jsonl"
FINAL = "final_plan.md"

def init():
    if not os.path.exists(STATE):
        json.dump({
            "turn": 0,
            "target_files": ["final_plan.md"],
            "last_contributor": None,
            "document_length_bytes": 0
        }, open(STATE, "w"), indent=2)
    for f in [PROPOSALS, COMMITS]:
        open(f, "a").close()
    if not os.path.exists(FINAL):
        open(FINAL, "w").write("# DUJ Heterogeneous Multi-Agent Benchmark Plan\n\n")

def load_state():
    return json.load(open(STATE))

def submit(agent_id, action_type, target_file, content):
    proposal = {
        "proposal_id": f"prop_{int(time.time()*1000)}",
        "timestamp": time.time(),
        "agent_id": agent_id,
        "action_type": action_type,
        "target_file": target_file,
        "content": content
    }
    open(PROPOSALS, "a").write(json.dumps(proposal) + "\n")
    return proposal

def validate(p, s):
    if p["target_file"] not in s["target_files"]:
        return False, "invalid target file"
    if p["action_type"] != "APPEND":
        return False, "only APPEND allowed"
    if not p["content"].strip():
        return False, "empty content"
    if s["last_contributor"] == p["agent_id"]:
        return False, "same agent cannot commit twice consecutively"
    if p["content"].strip() in open(FINAL).read():
        return False, "duplicate content"
    return True, "valid"

def commit_or_reject(p):
    s = load_state()
    ok, reason = validate(p, s)
    if ok:
        open(FINAL, "a").write(p["content"].strip() + "\n\n")
        s["turn"] += 1
        s["last_contributor"] = p["agent_id"]
        s["document_length_bytes"] = os.path.getsize(FINAL)
        json.dump(s, open(STATE, "w"), indent=2)
    open(COMMITS, "a").write(json.dumps({
        "proposal_id": p["proposal_id"],
        "agent_id": p["agent_id"],
        "status": "COMMITTED" if ok else "REJECTED",
        "reason": reason,
        "timestamp": time.time()
    }) + "\n")
    return ok, reason

if __name__ == "__main__":
    init()
    print("DUJ sandbox initialized")
