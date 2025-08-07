# FFMPEG Video Splitter

一個使用 FFmpeg 將長視頻分割成 30 分鐘片段並提取音頻的 Python 工具。

## 功能特點

- 🎥 自動將長視頻分割成 30 分鐘片段
- 🎵 同時提取每個片段的 MP3 音頻文件
- ⚡ 使用 FFmpeg 的 copy 模式，快速無損分割
- 📁 自動創建輸出目錄並按檔名分類
- 🔧 自動檢測系統中的 FFmpeg 安裝路徑

## 系統需求

- Python 3.6+
- FFmpeg（已安裝並可在命令行使用）

## 安裝 FFmpeg

### macOS
```bash
brew install ffmpeg
```

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

### Windows
從 [FFmpeg 官網](https://ffmpeg.org/download.html) 下載並安裝

## 使用方法

### 基本用法
```bash
python3 video-splitter.py your-video.mp4
```

### 輸出結果
工具會創建一個以原檔名命名的文件夾（例如：`your-video_parts/`），包含：
- `your-video_part1.mp4` - 第一個 30 分鐘視頻片段
- `your-video_part1.mp3` - 第一個片段的音頻
- `your-video_part2.mp4` - 第二個視頻片段
- `your-video_part2.mp3` - 第二個片段的音頻
- ... 以此類推

## 支援格式

- **輸入格式**：所有 FFmpeg 支援的視頻格式（MP4, AVI, MKV, MOV 等）
- **輸出格式**：MP4 視頻 + MP3 音頻

## 範例

```bash
# 分割一個 2 小時的電影
python3 video-splitter.py movie.mp4

# 輸出：
# movie_parts/
# ├── movie_part1.mp4  (30 分鐘)
# ├── movie_part1.mp3
# ├── movie_part2.mp4  (30 分鐘) 
# ├── movie_part2.mp3
# ├── movie_part3.mp4  (30 分鐘)
# ├── movie_part3.mp3
# ├── movie_part4.mp4  (30 分鐘)
# └── movie_part4.mp3
```

## 錯誤排除

### FFmpeg 未找到
```
Error: FFmpeg is not installed or not found in PATH.
```
**解決方案**：確保 FFmpeg 已正確安裝並可在命令行使用

### 視頻文件不存在
```
Error: Video file 'filename' not found.
```
**解決方案**：檢查檔案路徑是否正確

### 無法取得視頻時長
```
Error: Could not get video duration.
```
**解決方案**：確保視頻檔案沒有損壞，格式受 FFmpeg 支援

## 許可證

MIT License

## 作者

[Your Name]