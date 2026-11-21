#!/usr/bin/env python3
"""Channel outro: build it once, then reuse the same file at the end of every reel.

  outro.py status                       is there a cached outro? (prints its path and length)
  outro.py make [--force] [--text T] [--voice V] [--seconds S]
                                        build <brand>/outro/outro.mp4 ONCE. If it exists this does nothing,
                                        unless --force (only when the user asks for a new outro).
  outro.py append FILM.mp4 [OUT.mp4]    put the cached outro after FILM. OUT defaults to FILM (in place;
                                        the film without outro is kept in .pre-outro/ next to it).
  outro.py --selftest

Defaults: brand assets/brand/renderstand, voice kokoro am_michael (bin/vo.sh), 2 s, 1080x1920 at 30 fps.
The outro's words are on screen in sync with its voice, so it needs no captions; append it after film-captions.
"""
import argparse, datetime, difflib, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]          # .agents/skills/film-outro/scripts/outro.py
sys.path.insert(0, str(ROOT / ".agents/skills/film-studio/scripts"))
from assemble import run, loudness                  # noqa: E402  (same ffmpeg helpers as the film)

SKILL = Path(__file__).resolve().parents[1]
TAG = "film-outro"
DEFAULT = {"text": "Follow Renderstand, daily reels.", "engine": "kokoro", "voice": "am_michael", "speed": 1.25,
           "seconds": 2.0, "lead_s": 0.05, "tail_s": 0.2, "mark_s": 0.6,
           "width": 1080, "height": 1920, "fps": 30, "lufs": -14, "true_peak": -1.5}


def probe(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration:format_tags=comment",
               "-of", "json", str(path)]).stdout
    j = json.loads(out)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    a, b = v["r_frame_rate"].split("/")
    return {"w": v["width"], "h": v["height"], "fps": round(int(a) / int(b), 3),
            "dur": float(j["format"]["duration"]), "comment": j["format"].get("tags", {}).get("comment", ""),
            "audio": any(s["codec_type"] == "audio" for s in j["streams"])}


def norm(t):
    return re.sub(r"[^a-z0-9]", "", t.lower())


def align(script, asr):
    """Script words get ASR times. ASR may split or mishear a word ('Render stand'), so tokens are merged
    until they are as long as the script word."""
    out, j = [], 0
    for sw in script:
        target, acc, start, end = norm(sw), "", None, None
        while j < len(asr) and len(acc) < len(target):
            acc += norm(asr[j]["text"]); start = asr[j]["start"] if start is None else start; end = asr[j]["end"]; j += 1
        if start is None or difflib.SequenceMatcher(None, acc, target).ratio() < 0.6:
            sys.exit(f"voice and text disagree at {sw!r} (heard {acc!r}); respell the word in --text and rerun with --force")
        out.append({"text": sw, "start": start, "end": end})
    return out


def status(brand):
    o = brand / "outro" / "outro.mp4"
    if o.exists():
        print(f"cached: {o} ({probe(o)['dur']:.2f} s)")
        return True
    print("no outro yet: run `outro.py make` (once)")
    return False


def make(brand, force=False, **over):
    d = brand / "outro"; out, meta = d / "outro.mp4", d / "outro.json"
    if out.exists() and not force:
        print(f"cached, not rebuilt: {out} (use --force only for a new outro)")
        return out
    cfg = {**DEFAULT, **(json.loads(meta.read_text())["config"] if meta.exists() else {}),
           **{k: v for k, v in over.items() if v is not None}}
    src, build = d / "src", d / "build"
    src.mkdir(parents=True, exist_ok=True); build.mkdir(exist_ok=True); (src / "fonts").mkdir(exist_ok=True)
    for f in ("BarlowCondensed-Bold.ttf", "BarlowCondensed-SemiBold.ttf"):
        shutil.copy2(ROOT / "assets/fonts" / f, src / "fonts" / f)

    vo = d / "vo.wav"
    env = {**os.environ, "VO_SPEED": str(cfg["speed"])} if cfg["engine"] == "kokoro" else None
    r = subprocess.run([str(ROOT / "bin/vo.sh"), cfg["engine"], cfg["text"], str(vo), cfg["voice"]], capture_output=True, text=True, env=env)
    if r.returncode or not (d / "vo.words.json").exists():
        sys.exit(f"voice failed:\n{(r.stdout + r.stderr)[-1500:]}")
    words = align(cfg["text"].split(), json.loads((d / "vo.words.json").read_text()))
    vo_dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(vo)]).stdout)
    need = cfg["lead_s"] + vo_dur + cfg["tail_s"]
    dur = round(max(cfg["seconds"], need) * cfg["fps"]) / cfg["fps"]
    if need > cfg["seconds"] + 0.05:
        print(f"note: the voice needs {need:.2f} s, longer than {cfg['seconds']} s; outro is {dur:.2f} s. Shorten --text to fit.")
    timed = [{**w, "start": round(w["start"] + cfg["lead_s"], 3), "end": round(w["end"] + cfg["lead_s"], 3)} for w in words]
    (src / "words.js").write_text("window.OUTRO = " + json.dumps({"words": timed, "duration": dur, "mark_s": cfg["mark_s"]}) + ";\n")
    (src / "index.html").write_text((SKILL / "assets/outro.html").read_text().replace("__DURATION__", f"{dur:.3f}"))

    picture = build / "picture.mp4"
    env = {"HYPERFRAMES_CACHE_DIR": str(Path.home() / ".local/share/hyperframes-cache")}
    r = subprocess.run(["npx", "-y", "hyperframes", "render", "--fps", str(cfg["fps"]), "--quality", "delivery",
                        "--output", str(picture)], cwd=src, capture_output=True, text=True, env={**os.environ, **env})
    if r.returncode or not picture.exists():
        sys.exit(f"render failed:\n{(r.stdout + r.stderr)[-2000:]}")

    # Voice + the brand's render blip on the R's steps + a low land under the channel name.
    ins, fc, mix = ["-i", str(vo)], [f"[0:a]adelay={int(cfg['lead_s'] * 1000)}:all=1[v]"], ["[v]"]
    brand_word = next((w for w in timed if norm(w["text"]) == norm(brand.name)), timed[0])
    for wav, t, gain in (("render-blip.wav", cfg["mark_s"], -8), ("render-land.wav", brand_word["start"], -6)):
        f = ROOT / "assets/sfx" / wav
        if f.exists():
            ins += ["-i", str(f)]; i = len(mix)
            fc.append(f"[{i}:a]volume={gain}dB,adelay={int(t * 1000)}:all=1[s{i}]"); mix.append(f"[s{i}]")
    fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0,apad,atrim=0:{dur:.3f}[pre]")
    pre = build / "pre.wav"
    run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(fc), "-map", "[pre]", "-ar", "48000", "-ac", "2", str(pre)])
    # loudnorm needs 3 s+ of audio; for a 2 s clip: measured gain, then a peak limiter, then one correction pass.
    I, TP = cfg["lufs"], cfg["true_peak"]
    lim = 10 ** ((TP - 0.5) / 20)                 # sample-peak ceiling with 0.5 dB headroom for true peak
    gain, mixed = 0.0, build / "mix.wav"
    for _ in range(3):
        gain += I - loudness(mixed if mixed.exists() and gain else pre)[0]
        run(["ffmpeg", "-y", "-v", "error", "-i", str(pre), "-af",
             f"volume={gain:.2f}dB,alimiter=limit={lim:.4f}:level=disabled:attack=1:release=40,aresample=48000",
             "-ar", "48000", "-ac", "2", str(mixed)])
        if abs(loudness(mixed)[0] - I) < 0.3:
            break
    run(["ffmpeg", "-y", "-v", "error", "-i", str(picture), "-i", str(mixed),
         "-map", "0:v", "-map", "1:a", "-t", f"{dur:.3f}", "-c:v", "libx264", "-crf", "14", "-preset", "faster",
         "-pix_fmt", "yuv420p", "-r", str(cfg["fps"]), "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2", str(out)])
    lufs, tp = loudness(out)
    meta.write_text(json.dumps({"config": cfg, "made": datetime.date.today().isoformat(), "duration_s": dur,
                                "lufs": lufs, "true_peak": tp, "words": timed}, indent=2))
    print(f"made {out}: {dur:.2f} s, {lufs:.1f} LUFS, {tp:.1f} dBTP")
    return out


def append(brand, film, out=None):
    o = brand / "outro" / "outro.mp4"
    if not o.exists():
        sys.exit("no outro yet: run `outro.py make` once")
    film = Path(film).resolve(); out = Path(out).resolve() if out else film
    f, q = probe(film), probe(o)
    if TAG in f["comment"].split():
        sys.exit(f"{film} already ends with the outro")
    if (f["w"], f["h"], f["fps"]) != (q["w"], q["h"], q["fps"]):
        sys.exit(f"size mismatch: film {f['w']}x{f['h']}@{f['fps']}, outro {q['w']}x{q['h']}@{q['fps']}")
    if not f["audio"]:
        sys.exit(f"{film} has no audio track")
    src = film
    if out == film:
        keep = film.parent / ".pre-outro" / film.name
        keep.parent.mkdir(exist_ok=True); shutil.copy2(film, keep); src = keep
    tmp = Path(tempfile.mkdtemp()) / out.name
    a = "aresample=48000,aformat=channel_layouts=stereo"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-i", str(o), "-filter_complex",
         f"[0:a]{a}[a0];[1:a]{a}[a1];[0:v][a0][1:v][a1]concat=n=2:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-crf", "16", "-preset", "faster", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
         "-metadata", f"comment={(f['comment'] + ' ' + TAG).strip()}", "-movflags", "+faststart", str(tmp)])
    out.parent.mkdir(parents=True, exist_ok=True); shutil.move(str(tmp), out)
    print(f"wrote {out}: {f['dur']:.2f} s film + {q['dur']:.2f} s outro = {probe(out)['dur']:.2f} s")


def selftest():
    with tempfile.TemporaryDirectory() as t:
        t = Path(t); brand = t / "brand"; (brand / "outro").mkdir(parents=True)
        mk = lambda p, s, size="1080x1920", c="": run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"testsrc=size={size}:rate=30:d={s}",
                                                     "-f", "lavfi", "-i", f"sine=d={s}", "-shortest", "-pix_fmt", "yuv420p",
                                                     "-metadata", f"comment={c}", str(p)])
        mk(brand / "outro" / "outro.mp4", 2)
        assert make(brand) == brand / "outro" / "outro.mp4"      # cached: returns without building anything
        film = t / "final.mp4"; mk(film, 3, c="film-captions")
        append(brand, film)
        p = probe(film)
        assert abs(p["dur"] - 5) < 0.1 and p["comment"].split() == ["film-captions", TAG], p
        assert (t / ".pre-outro" / "final.mp4").exists()
        for bad in (lambda: append(brand, film), lambda: (mk(t / "wide.mp4", 1, "1920x1080"), append(brand, t / "wide.mp4"))):
            try:
                bad(); raise AssertionError("should refuse")
            except SystemExit:
                pass
    print("outro selftest ok")


def main():
    if sys.argv[1:] == ["--selftest"]:
        return selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["status", "make", "append"])
    ap.add_argument("film", nargs="?"); ap.add_argument("out", nargs="?")
    ap.add_argument("--brand", default=str(ROOT / "assets/brand/renderstand"))
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--text"); ap.add_argument("--voice"); ap.add_argument("--seconds", type=float); ap.add_argument("--speed", type=float)
    a = ap.parse_args(); brand = Path(a.brand).resolve()
    if a.cmd == "status":
        sys.exit(0 if status(brand) else 1)
    if a.cmd == "make":
        make(brand, a.force, text=a.text, voice=a.voice, seconds=a.seconds, speed=a.speed)
    else:
        if not a.film:
            sys.exit("usage: outro.py append FILM.mp4 [OUT.mp4]")
        append(brand, a.film, a.out)


if __name__ == "__main__":
    main()
