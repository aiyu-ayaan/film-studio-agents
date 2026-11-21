//! Pipeline progress read from the files each film-studio stage leaves behind.
//! Works the same whichever agent is driving, because it never parses agent output.

use serde_json::{json, Value};
use std::path::Path;

#[derive(serde::Serialize, Clone)]
pub struct Check {
    pub label: String,
    pub ok: bool,
}

#[derive(serde::Serialize, Clone)]
pub struct Stage {
    pub id: &'static str,
    pub label: &'static str,
    pub about: &'static str,
    pub done: bool,
    pub checks: Vec<Check>,
}

#[derive(serde::Serialize, Clone)]
pub struct Status {
    pub title: String,
    pub stages: Vec<Stage>,
    /// index of the first stage not done (== stages.len() when all done)
    pub current: usize,
    /// 0.0..=1.0, scene clips count as a fraction of their stage
    pub progress: f64,
    pub scenes_done: usize,
    pub scenes_total: usize,
    pub final_video: Option<String>,
    /// master format from plan.json: width, height, fps, duration_s, voice_engine, captions, speech
    pub master: Value,
    /// per scene: id, skill, brief, frames, seconds, clip (abs path or null), text
    pub scenes: Vec<Value>,
    /// narration lines: id, text
    pub lines: Vec<Value>,
}

const STAGES: [(&str, &str, &str); 11] = [
    ("0", "Brief", "Goal, audience, platform, length and format written down in BRIEF.md."),
    ("1", "Script", "Narration written as speech, one line per beat, into plan.json."),
    ("2", "Storyboard", "Lines split into scenes, a skill picked per scene, one look fixed in style.md. You approve script and storyboard here (gate G1)."),
    ("3", "Voice", "Local voiceover (Kokoro or Pocket TTS) made, checked by a transcriber, and every scene length locked to the frame."),
    ("4", "Scenes", "One silent clip per scene, rendered by its skill at the master size and length."),
    ("5", "Music", "Music bed and sound effects picked, each with a licence and credit."),
    ("6", "Assemble", "Clips cut together, voice and ducked music mixed, loudness set to -14 LUFS."),
    ("6b", "Captions", "Captions burned in from the word timings; the clean master is kept aside."),
    ("7", "Review", "Contact sheet and sound critique checked; weak scenes fixed."),
    ("8", "Deliver", "NOTE.md filled with credits, licences and QA numbers."),
    ("9", "Cleanup", "Rebuildable bulk deleted; the film, sources and audio kept."),
];

fn differs_from_template(root: &Path, dir: &Path, name: &str) -> bool {
    match std::fs::read(dir.join(name)) {
        Ok(cur) => std::fs::read(root.join("templates/project").join(name)).map_or(true, |t| t != cur),
        Err(_) => false,
    }
}

fn non_empty_dir(p: &Path) -> bool {
    std::fs::read_dir(p).map_or(false, |mut d| d.next().is_some())
}

fn c(label: impl Into<String>, ok: bool) -> Check {
    Check { label: label.into(), ok }
}

pub fn project_status(root: &Path, dir: &Path) -> Status {
    let plan: Value = std::fs::read_to_string(dir.join("plan.json"))
        .ok()
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or(Value::Null);
    let scenes = plan["scenes"].as_array().cloned().unwrap_or_default();
    let lines = plan["lines"].as_array().cloned().unwrap_or_default();
    let fps = plan["master"]["fps"].as_f64().unwrap_or(30.0);
    let clip_of = |s: &Value| {
        let rel = s["clip"].as_str().map(str::to_owned)
            .unwrap_or_else(|| format!("scenes/{}/clip.mp4", s["id"].as_str().unwrap_or("")));
        let p = dir.join(rel);
        p.is_file().then(|| p.display().to_string())
    };
    let scenes_done = scenes.iter().filter(|s| clip_of(s).is_some()).count();
    let n = scenes.len();
    let final_mp4 = dir.join("renders/final.mp4");
    let has_final = final_mp4.is_file();
    let note = differs_from_template(root, dir, "NOTE.md");
    let speech = plan["master"]["speech"] != Value::Bool(false);
    let all_framed = n > 0 && scenes.iter().all(|s| s["frames"].is_number());

    let checks: [Vec<Check>; 11] = [
        vec![c("BRIEF.md filled in", differs_from_template(root, dir, "BRIEF.md"))],
        if speech {
            vec![c("plan.json written", !plan.is_null()), c(format!("{} narration lines", lines.len()), !lines.is_empty())]
        } else {
            vec![c("plan.json written", !plan.is_null()), c("No-speech film: script is on-screen text", n > 0)]
        },
        vec![
            c(format!("{n} scenes planned"), n > 0),
            c("style.md (look of the film)", dir.join("style.md").is_file()),
            c("STORYBOARD.md", dir.join("STORYBOARD.md").is_file()),
        ],
        if speech {
            vec![c("audio/vo/vo.wav voiceover", dir.join("audio/vo/vo.wav").is_file()), c("Every scene has a frame count", all_framed)]
        } else {
            vec![c("Every scene timed to the music's beats", all_framed)]
        },
        vec![c(format!("{scenes_done} of {n} scene clips rendered"), n > 0 && scenes_done == n)],
        vec![c("Music bed set in plan.json", plan["music"]["path"].as_str().is_some_and(|p| !p.is_empty()))],
        vec![c("renders/final.mp4", has_final)],
        vec![c("Clean master moved to renders/.clean/", dir.join("renders/.clean/final.mp4").is_file())],
        vec![c("renders/contact.png contact sheet", dir.join("renders/contact.png").is_file())],
        vec![c("NOTE.md credits filled in", note)],
        vec![
            c("Film kept", has_final),
            c("build/ emptied", !non_empty_dir(&dir.join("build"))),
            c("Scene clips removed (re-render to edit)", scenes_done == 0),
        ],
    ];
    let mut done: Vec<bool> = checks.iter().map(|cs| cs.iter().all(|c| c.ok)).collect();
    // cleanup only counts once the film is delivered
    done[10] &= note;
    // a later stage done implies earlier ones (cleanup deletes earlier artifacts)
    for i in (0..done.len() - 1).rev() {
        done[i] |= done[i + 1];
    }
    let current = done.iter().position(|d| !d).unwrap_or(done.len());
    let mut units = done.iter().filter(|d| **d).count() as f64;
    if current == 4 && n > 0 {
        units += scenes_done as f64 / n as f64;
    }

    let text_of: std::collections::HashMap<&str, &str> = lines.iter()
        .filter_map(|l| Some((l["id"].as_str()?, l["text"].as_str().unwrap_or(""))))
        .collect();
    Status {
        title: plan["title"].as_str().unwrap_or("").to_string(),
        stages: STAGES.iter().zip(done).zip(checks)
            .map(|(((id, label, about), done), checks)| Stage { id, label, about, done, checks })
            .collect(),
        current,
        progress: units / STAGES.len() as f64,
        scenes_done,
        scenes_total: n,
        final_video: has_final.then(|| final_mp4.display().to_string()),
        master: json!({
            "width": plan["master"]["width"], "height": plan["master"]["height"], "fps": plan["master"]["fps"],
            "duration_s": plan["master"]["duration_s"], "voice_engine": plan["master"]["voice_engine"],
            "voice": plan["master"]["voice"], "captions": plan["master"]["captions"], "speech": speech,
        }),
        scenes: scenes.iter().map(|s| {
            let text: Vec<&str> = s["line_ids"].as_array().into_iter().flatten()
                .filter_map(|id| text_of.get(id.as_str()?).copied()).collect();
            json!({
                "id": s["id"], "skill": s["skill"], "brief": s["brief"], "frames": s["frames"],
                "seconds": s["frames"].as_f64().map(|f| f / fps).or(s["seconds"].as_f64()),
                "clip": clip_of(s), "text": text.join(" "),
            })
        }).collect(),
        lines: lines.iter().map(|l| json!({"id": l["id"], "text": l["text"]})).collect(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn stages_follow_files() {
        let root = tempfile::tempdir().unwrap();
        let tpl = root.path().join("templates/project");
        fs::create_dir_all(&tpl).unwrap();
        fs::write(tpl.join("BRIEF.md"), "# Brief\n").unwrap();
        fs::write(tpl.join("NOTE.md"), "# Note\n").unwrap();
        let p = root.path().join("projects/x");
        fs::create_dir_all(p.join("scenes/s1")).unwrap();
        fs::create_dir_all(p.join("audio/vo")).unwrap();
        fs::write(p.join("BRIEF.md"), "# Brief\n").unwrap();
        fs::write(p.join("NOTE.md"), "# Note\n").unwrap();

        let s = project_status(root.path(), &p);
        assert_eq!(s.current, 0);
        assert_eq!(s.progress, 0.0);

        fs::write(p.join("BRIEF.md"), "# Brief\nGoal: bees\n").unwrap();
        fs::write(p.join("style.md"), "").unwrap();
        fs::write(p.join("STORYBOARD.md"), "").unwrap();
        fs::write(p.join("audio/vo/vo.wav"), "").unwrap();
        fs::write(
            p.join("plan.json"),
            r#"{"title":"Bees","master":{"fps":30},"lines":[{"id":"l1","text":"Hi."}],
               "scenes":[{"id":"s1","frames":90,"line_ids":["l1"]},{"id":"s2","frames":90}]}"#,
        )
        .unwrap();
        fs::write(p.join("scenes/s1/clip.mp4"), "x").unwrap();
        let s = project_status(root.path(), &p);
        assert_eq!(s.title, "Bees");
        assert_eq!(s.current, 4, "voice done, scenes half done");
        assert_eq!((s.scenes_done, s.scenes_total), (1, 2));
        assert!((s.progress - 4.5 / 11.0).abs() < 1e-9);
        assert_eq!(s.scenes[0]["text"], "Hi.");
        assert_eq!(s.scenes[0]["seconds"], 3.0);
        assert!(!s.stages[4].checks[0].ok);

        // after cleanup: clips gone, film + note kept => everything done
        fs::remove_file(p.join("scenes/s1/clip.mp4")).unwrap();
        fs::create_dir_all(p.join("renders")).unwrap();
        fs::write(p.join("renders/final.mp4"), "x").unwrap();
        fs::write(p.join("NOTE.md"), "# Note\nCredits\n").unwrap();
        let s = project_status(root.path(), &p);
        assert_eq!(s.current, 11);
        assert!(s.stages.iter().all(|st| st.done));
        assert!(s.final_video.is_some());
    }
}
