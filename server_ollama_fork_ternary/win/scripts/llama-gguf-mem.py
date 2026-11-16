#!/usr/bin/env python3
"""
Stima la RAM necessaria per caricare un GGUF con llama-server (build CPU)
ed eventualmente suggerisce ctx/KV-cache/batch che ci stanno.

Uso:
  llama-gguf-mem.py <file.gguf> --ctx N --cache q8_0 --batch N [--mem-available BYTES]

Stampa un JSON con: stima per componente, se ci sta (fits) e, in caso
contrario, i valori suggeriti (suggested) ottenuti riducendo prima la KV
cache a q4_0, poi il contesto (dimezzando), poi il batch (dimezzando).

Note:
- La KV cache vale SOLO per i blocchi di attenzione piena (nei modelli
  ibridi tipo qwen35 con full_attention_interval > 1 gli altri blocchi
  sono SSM/lineari e hanno uno state buffer fisso).
- Il "compute buffer" di ggml è stimato con un'euristica
  (n_batch * embedding * blocchi * 2 B) + overhead fisso.
"""
import json, os, struct, sys

# ── parser GGUF minimale (solo stdlib) ──────────────────────────────
def read_u32(b, o): return struct.unpack_from("<I", b, o)[0], o + 4
def read_u64(b, o): return struct.unpack_from("<Q", b, o)[0], o + 8
def read_str(b, o):
    n, o = read_u64(b, o)
    return b[o:o + n].decode("utf-8", "replace"), o + n

def read_value(b, o, t):
    if t in (0, 1): return b[o], o + 1
    if t == 2: return struct.unpack_from("<H", b, o)[0], o + 2
    if t == 3: return struct.unpack_from("<h", b, o)[0], o + 2
    if t == 4: return read_u32(b, o)
    if t == 5: return struct.unpack_from("<i", b, o)[0], o + 4
    if t == 6: return struct.unpack_from("<f", b, o)[0], o + 4
    if t == 7: return b[o] != 0, o + 1
    if t == 8: return read_str(b, o)
    if t == 9:
        et, o = read_u32(b, o)
        n, o = read_u64(b, o)
        for _ in range(n):
            _, o = read_value(b, o, et)
        return None, o
    if t == 10: return read_u64(b, o)
    if t == 11: return struct.unpack_from("<q", b, o)[0], o + 8
    if t == 12: return struct.unpack_from("<d", b, o)[0], o + 8
    raise ValueError(f"tipo GGUF sconosciuto {t}")

def parse_gguf(path, cap=128 * 1024 * 1024):
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        data = f.read(min(cap, size))
    if data[:4] != b"GGUF":
        raise ValueError("non è un file GGUF (magic mancante)")
    o = 4
    _, o = read_u32(data, o)          # version
    n_tensors, o = read_u64(data, o)
    n_kv, o = read_u64(data, o)
    kv = {}
    for _ in range(n_kv):
        k, o = read_str(data, o)
        t, o = read_u32(data, o)
        v, o = read_value(data, o, t)
        kv[k] = v
    ssm_blocks = 0
    attn_blocks = 0
    for i in range(n_tensors):
        name, o = read_str(data, o)
        ndims, o = read_u32(data, o)
        for _ in range(ndims):
            _, o = read_u64(data, o)
        _, o = read_u32(data, o)      # type
        _, o = read_u64(data, o)      # offset
        if name.endswith(".attn_k.weight"):
            attn_blocks += 1
    return kv, {"attn_blocks": attn_blocks, "file_bytes": size}

# ── euristica di memoria ─────────────────────────────────────────────
KV_BYTES = {"f16": 2.0, "q8_0": 1.0, "q4_0": 0.5}   # byte per elemento

def estimate(kv, meta, ctx, cache, batch):
    block_count = int(kv.get("qwen35.block_count") or kv.get("llama.block_count") or 0)
    embd = int(kv.get("qwen35.embedding_length") or kv.get("llama.embedding_length") or 0)
    head_kv = int(kv.get("qwen35.attention.head_count_kv") or kv.get("llama.attention.head_count_kv") or 0)
    k_len = int(kv.get("qwen35.attention.key_length") or kv.get("llama.attention.key_length") or 0)
    v_len = int(kv.get("qwen35.attention.value_length") or kv.get("llama.attention.value_length") or 0)
    ssm_inner = int(kv.get("qwen35.ssm.inner_size") or 0)
    ssm_state = int(kv.get("qwen35.ssm.state_size") or 0)
    full_attn_interval = int(kv.get("qwen35.full_attention_interval") or kv.get("llama.full_attention_interval") or 1)

    attn_blocks = meta["attn_blocks"] or (block_count // max(full_attn_interval, 1))
    ssm_blocks = max(block_count - attn_blocks, 0)

    # pesi: dimensione del file (~ 1:1 con la RAM occupata a runtime)
    model_bytes = meta["file_bytes"]

    # KV cache: solo i blocchi di attenzione piena
    kv_per_token = (k_len + v_len) * head_kv * attn_blocks * KV_BYTES.get(cache, 1.0)
    kv_bytes = kv_per_token * ctx

    # state buffer degli SSM (f32, 64 stati per canale per lo stato)
    ssm_bytes = 0.0
    if ssm_blocks and ssm_inner and ssm_state:
        ssm_bytes = ssm_inner * ssm_state * ssm_blocks * 4.0  # stato
        ssm_bytes += 4 * 4 * ssm_blocks * 2.0                 # conv buffer (piccolo)

    # buffer di calcolo ggml (euristica) + overhead fisso
    compute_bytes = batch * embd * block_count * 2.0 + 400 * 1024 * 1024

    headroom = 256 * 1024 * 1024  # sistema, libs, curl, ecc.
    total = model_bytes + kv_bytes + ssm_bytes + compute_bytes + headroom
    return {
        "block_count": block_count, "attn_blocks": attn_blocks, "ssm_blocks": ssm_blocks,
        "model_bytes": model_bytes, "kv_per_token": kv_per_token,
        "kv_bytes": kv_bytes, "ssm_bytes": ssm_bytes, "compute_bytes": compute_bytes,
        "headroom_bytes": headroom, "total_bytes": total,
    }

def human(n):
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{int(n)} B" if u == "B" else f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} PB"

def main():
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"ok": False, "error": "usage: llama-gguf-mem.py <gguf> --ctx N --cache q8_0 --batch N [--mem-available BYTES]"}))
        return 2
    gguf = args[0]
    opts = {}
    i = 1
    while i < len(args):
        k, v = args[i], args[i + 1] if i + 1 < len(args) else None
        if k in ("--ctx", "--cache", "--batch", "--mem-available"):
            opts[k[2:]] = v
        i += 1
    ctx = int(opts.get("ctx", 2048))
    cache = opts.get("cache", "q8_0")
    batch = int(opts.get("batch", 2048))
    mem_avail = int(opts.get("mem-available", 0) or 0)

    try:
        kv, meta = parse_gguf(gguf)
    except Exception as e:
        print(json.dumps({"ok": False, "error": f"parse GGUF: {e}"}))
        return 1

    if not mem_avail:
        try:
            for line in open("/proc/meminfo"):
                if line.startswith("MemAvailable:"):
                    mem_avail = int(line.split()[1]) * 1024
                    break
        except Exception:
            pass

    e = estimate(kv, meta, ctx, cache, batch)
    out = {
        "ok": True,
        "mem_available": mem_avail,
        "requested": {"ctx": ctx, "cache": cache, "batch": batch},
        "estimate": {k: v for k, v in e.items()},
        "total_human": human(e["total_bytes"]),
        "mem_available_human": human(mem_avail),
        "fits": bool(mem_avail) and e["total_bytes"] <= mem_avail,
        "suggested": {"ctx": ctx, "cache": cache, "batch": batch},
        "notes": [],
    }

    # AUTO-FIT: riduci finché non ci sta (o arriva al minimo)
    cur = {"ctx": ctx, "cache": cache, "batch": batch}
    while not out["fits"] and mem_avail:
        if cur["cache"] == "q8_0":
            cur["cache"] = "q4_0"
            out["notes"].append("KV cache ridotta a q4_0 (metà memoria)")
        elif cur["ctx"] > 1024:
            cur["ctx"] = max(1024, cur["ctx"] // 2)
            out["notes"].append(f"contesto ridotto a {cur['ctx']}")
        elif cur["batch"] > 256:
            cur["batch"] = cur["batch"] // 2
            out["notes"].append(f"batch ridotto a {cur['batch']}")
        else:
            break
        e = estimate(kv, meta, cur["ctx"], cur["cache"], cur["batch"])
        out["fits"] = e["total_bytes"] <= mem_avail
        out["estimate"] = {k: v for k, v in e.items()}
        out["total_human"] = human(e["total_bytes"])
        out["suggested"] = dict(cur)

    if out["fits"] and (cur["ctx"] != ctx or cur["cache"] != cache or cur["batch"] != batch):
        out["notes"].append("configurazione ridotta automaticamente (vedi suggested)")

    print(json.dumps(out))
    return 0

if __name__ == "__main__":
    sys.exit(main())