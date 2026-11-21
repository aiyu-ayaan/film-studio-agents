//! Loopback HTTP server for the in-app video player.
//! WebKitGTK hands <video> to GStreamer, which cannot read Tauri's asset:// scheme
//! (MEDIA_ERR_SRC_NOT_SUPPORTED); the same file over http plays. Serves only files under
//! projects/, only on 127.0.0.1, only with this run's random token, with Range for seeking.

use std::io::{BufRead, BufReader, Read, Seek, SeekFrom, Write};
use std::net::{TcpListener, TcpStream};
use std::path::{Path, PathBuf};
use std::sync::OnceLock;

static BASE: OnceLock<String> = OnceLock::new();

/// Start once; returns "http://127.0.0.1:<port>/<token>".
pub fn start(projects: PathBuf) -> std::io::Result<()> {
    let listener = TcpListener::bind("127.0.0.1:0")?;
    let port = listener.local_addr()?.port();
    let token = {
        use std::hash::{BuildHasher, Hasher};
        let mut h = std::collections::hash_map::RandomState::new().build_hasher();
        h.write_u128(std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_nanos());
        format!("{:016x}", h.finish())
    };
    let _ = BASE.set(format!("http://127.0.0.1:{port}/{token}"));
    let prefix = format!("/{token}/");
    std::thread::spawn(move || {
        for s in listener.incoming().flatten() {
            let (p, pre) = (projects.clone(), prefix.clone());
            std::thread::spawn(move || { let _ = serve(s, &p, &pre); });
        }
    });
    Ok(())
}

/// URL the webview can play for a file inside projects/.
pub fn url(path: &str) -> Option<String> {
    let enc: String = path.bytes().map(|b| match b {
        b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'/' => (b as char).to_string(),
        _ => format!("%{b:02X}"),
    }).collect();
    Some(format!("{}{}", BASE.get()?, enc))
}

fn decode(s: &str) -> Option<String> {
    let b = s.as_bytes();
    let mut out = Vec::with_capacity(b.len());
    let mut i = 0;
    while i < b.len() {
        if b[i] == b'%' {
            out.push(u8::from_str_radix(s.get(i + 1..i + 3)?, 16).ok()?);
            i += 3;
        } else {
            out.push(b[i]);
            i += 1;
        }
    }
    String::from_utf8(out).ok()
}

fn serve(mut s: TcpStream, projects: &Path, prefix: &str) -> std::io::Result<()> {
    let mut r = BufReader::new(s.try_clone()?);
    let mut line = String::new();
    r.read_line(&mut line)?;
    let target = line.split_whitespace().nth(1).unwrap_or("");
    let mut range: Option<(u64, Option<u64>)> = None;
    loop {
        let mut h = String::new();
        if r.read_line(&mut h)? == 0 || h.trim().is_empty() { break; }
        if let Some(v) = h.to_ascii_lowercase().strip_prefix("range: bytes=") {
            let (a, b) = v.trim().split_once('-').unwrap_or(("0", ""));
            range = Some((a.parse().unwrap_or(0), b.parse().ok()));
        }
    }
    let file = target.strip_prefix(prefix).map(|p| format!("/{}", p.split('?').next().unwrap_or("")))
        .and_then(|p| decode(&p))
        .and_then(|p| PathBuf::from(p).canonicalize().ok())
        .filter(|p| p.starts_with(projects) && p.is_file());
    let Some(file) = file else {
        return s.write_all(b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n");
    };
    let mut f = std::fs::File::open(&file)?;
    let len = f.metadata()?.len();
    let ctype = match file.extension().and_then(|e| e.to_str()) {
        Some("mp4") => "video/mp4", Some("webm") => "video/webm", Some("mov") => "video/quicktime",
        Some("png") => "image/png", _ => "application/octet-stream",
    };
    let (start, end) = match range {
        Some((a, b)) if a < len => (a, b.unwrap_or(len - 1).min(len - 1)),
        _ => (0, len.saturating_sub(1)),
    };
    let n = if len == 0 { 0 } else { end - start + 1 };
    let head = if range.is_some() {
        format!("HTTP/1.1 206 Partial Content\r\nContent-Range: bytes {start}-{end}/{len}\r\n")
    } else {
        "HTTP/1.1 200 OK\r\n".to_string()
    };
    s.write_all(format!("{head}Content-Type: {ctype}\r\nContent-Length: {n}\r\nAccept-Ranges: bytes\r\nConnection: close\r\n\r\n").as_bytes())?;
    f.seek(SeekFrom::Start(start))?;
    std::io::copy(&mut f.take(n), &mut s)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn serves_ranges_only_inside_projects() {
        let dir = tempfile::tempdir().unwrap();
        let projects = dir.path().join("projects");
        std::fs::create_dir_all(projects.join("a b")).unwrap();
        let film = projects.join("a b/final.mp4");
        std::fs::write(&film, b"0123456789").unwrap();
        std::fs::write(dir.path().join("secret.txt"), b"no").unwrap();
        start(projects.canonicalize().unwrap()).unwrap();

        let get = |u: &str, range: &str| {
            let rest = u.strip_prefix("http://").unwrap();
            let (host, path) = rest.split_once('/').unwrap();
            let mut s = TcpStream::connect(host).unwrap();
            write!(s, "GET /{path} HTTP/1.1\r\nHost: x\r\n{range}\r\n").unwrap();
            let mut out = String::new();
            s.read_to_string(&mut out).unwrap();
            out
        };
        let u = url(film.canonicalize().unwrap().to_str().unwrap()).unwrap();
        assert!(u.contains("a%20b"));
        let r = get(&u, "Range: bytes=2-5\r\n");
        assert!(r.starts_with("HTTP/1.1 206") && r.ends_with("2345"), "{r}");
        assert!(get(&u, "").ends_with("0123456789"));
        let outside = url(dir.path().join("secret.txt").canonicalize().unwrap().to_str().unwrap()).unwrap();
        assert!(get(&outside, "").starts_with("HTTP/1.1 404"));
        let tok = BASE.get().unwrap().rsplit('/').next().unwrap();
        assert!(get(&u.replacen(tok, "0000000000000000", 1), "").starts_with("HTTP/1.1 404"));
    }
}
