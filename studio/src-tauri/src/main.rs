// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    // WebKitGTK's DMA-BUF renderer fails on NVIDIA here (EGL/DRI2 errors in the log).
    #[cfg(target_os = "linux")]
    for var in ["WEBKIT_DISABLE_DMABUF_RENDERER"] {
        if std::env::var_os(var).is_none() {
            // SAFETY: first statements in main, before any thread exists
            unsafe { std::env::set_var(var, "1") };
        }
    }
    studio_lib::run()
}
