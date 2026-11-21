//! Pipeline progress read from the files each film-studio stage leaves behind.
//! Works the same whichever agent is driving, because it never parses agent output.

use serde_json::Value;
use std::path::Path;

#[derive(serde::Serialize, Clone)]
pub struct Stage {
    pub id: &'static str,
    pub label: &'static str,
    pub done: bool,
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
}

const STAGES: [(&str, &str); 11] = [
    ("0", "Brief"),
    ("1", "Script"),
    ("2", "Storyboard"),
    ("3", "Voice"),
    ("4", "Scenes"),
    ("5", "Music"),
    ("6", "Assemble"),
    ("6b", "Captions"),
    ("7", "Review"),
    ("8", "Deliver"),
    ("9", "Cleanup"),
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

pub fn project_status(root: &Path, dir: &Path) -> Status {
    let plan: Value = std::fs::read_to_string(dir.join("plan.json"))
        .ok()
        .and_then(|s| serde_json::from_str(&s).ok())
        .unwrap_or(Value::Null);
    let scenes = plan["scenes"].as_array().cloned().unwrap_or_default();
    let clip = |s: &Value| {
        let rel = s["clip"].as_str().map(str::to_owned)
            .unwrap_or_else(|| format!("scenes/{}/clip.mp4", s["id"].as_str().unwrap_or("")));
        dir.join(rel).is_file()
    };
    let scenes_done = scenes.iter().filter(|s| clip(s)).count();
    let final_mp4 = dir.join("renders/final.mp4");
    let note = differs_from_template(root, dir, "NOTE.md");

    let raw = [
        differs_from_template(root, dir, "BRIEF.md"),
        plan["lines"].as_array().is_some_and(|l| !l.is_empty())
            || plan["master"]["speech"] == Value::Bool(false) && !scenes.is_empty(),
        dir.join("style.md").is_file() && dir.join("STORYBOARD.md").is_file(),
        !scenes.is_empty() && scenes.iter().all(|s| s["frames"].is_number()),
        !scenes.is_empty() && scenes_done == scenes.len(),
        plan["music"]["path"].as_str().is_some_and(|p| !p.is_empty()),
        final_mp4.is_file(),
        dir.join("renders/.clean/final.mp4").is_file(),
        dir.join("renders/contact.png").is_file(),
        note,
        // cleanup removes build/ contents and scene clips but keeps the film
        final_mp4.is_file() && note && !non_empty_dir(&dir.join("build")) && scenes_done == 0,
    ];
    // a later stage done implies earlier ones (cleanup deletes earlier artifacts)
    let mut done = raw;
    for i in (0..done.len() - 1).rev() {
        done[i] |= done[i + 1];
    }
    let current = done.iter().position(|d| !d).unwrap_or(done.len());
    let mut units = done.iter().filter(|d| **d).count() as f64;
    if current == 4 && !scenes.is_empty() {
        units += scenes_done as f64 / scenes.len() as f64;
    }
    Status {
        title: plan["title"].as_str().unwrap_or("").to_string(),
        stages: STAGES.iter().zip(done).map(|((id, label), done)| Stage { id, label, done }).collect(),
        current,
        progress: units / STAGES.len() as f64,
        scenes_done,
        scenes_total: scenes.len(),
        final_video: final_mp4.is_file().then(|| final_mp4.display().to_string()),
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
        fs::write(p.join("BRIEF.md"), "# Brief\n").unwrap();
        fs::write(p.join("NOTE.md"), "# Note\n").unwrap();

        let s = project_status(root.path(), &p);
        assert_eq!(s.current, 0);
        assert_eq!(s.progress, 0.0);

        fs::write(p.join("BRIEF.md"), "# Brief\nGoal: bees\n").unwrap();
        fs::write(p.join("style.md"), "").unwrap();
        fs::write(p.join("STORYBOARD.md"), "").unwrap();
        fs::write(
            p.join("plan.json"),
            r#"{"title":"Bees","lines":[{"id":"l1"}],
               "scenes":[{"id":"s1","frames":90},{"id":"s2","frames":90}]}"#,
        )
        .unwrap();
        fs::write(p.join("scenes/s1/clip.mp4"), "x").unwrap();
        let s = project_status(root.path(), &p);
        assert_eq!(s.title, "Bees");
        assert_eq!(s.current, 4, "voice done, scenes half done");
        assert_eq!((s.scenes_done, s.scenes_total), (1, 2));
        assert!((s.progress - 4.5 / 11.0).abs() < 1e-9);

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
