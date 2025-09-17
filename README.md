# FFMPEG Video Splitter with YouTube Support

一個使用 FFmpeg 將長視頻分割成 30 分鐘片段並提取音頻的 Python 工具，支援 YouTube 影片下載。

## 功能特點

- 📺 **YouTube 影片下載**：支援 YouTube URL 直接下載（1080p 高品質）
- 🎥 自動將長視頻分割成 30 分鐘片段
- 🎵 **永遠提取音頻**：無論是否分割都會提取完整 MP3 音頻文件（320k 品質）
- ⚡ 使用 FFmpeg 的 copy 模式，快速無損分割
- 🗂️ **有組織的檔案結構**：自動創建主資料夾，並按檔案類型分類（MP3/、MP4/）
- 🔧 自動檢測系統中的 FFmpeg 安裝路徑
- 💾 **保留原檔案**：下載的原始影片檔案永久保留
- 🎯 **智能格式選擇**：自動下載並合併最佳品質的影片和音頻軌道

## 系統需求

- Python 3.6+
- FFmpeg（已安裝並可在命令行使用）
- yt-dlp（用於 YouTube 下載）

## 安裝依賴

```bash
pip3 install yt-dlp
# 或者
pip3 install -r requirements.txt
```

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

### YouTube 影片下載和分割
```bash
# 下載 YouTube 影片並自動分割成 30 分鐘片段
python3 video-splitter.py --youtube "https://www.youtube.com/watch?v=VIDEO_ID"

# 下載 YouTube 影片但不分割，只提取完整音訊
python3 video-splitter.py --youtube "https://www.youtube.com/watch?v=VIDEO_ID" --no-split

# 下載並只處理音訊部分（保留原始影片）
python3 video-splitter.py --youtube "https://www.youtube.com/watch?v=VIDEO_ID" --audio-only
```

### 本地檔案處理
```bash
# 處理本地影片檔案（預設分割）
python3 video-splitter.py your-video.mp4

# 處理本地檔案但不分割
python3 video-splitter.py your-video.mp4 --no-split
```

### 輸出結果

所有檔案都會組織在以影片檔名命名的主資料夾中，並按檔案類型分類：

#### 分割模式（預設）
```
video_title/                      # 主資料夾（以檔案名命名）
├── video_title.mp4              # 原始影片檔案（1080p 高品質）
├── MP3/                         # 音訊檔案專用資料夾
│   ├── video_title.mp3          # 完整音訊檔案
│   ├── video_title_part1.mp3    # 第一個 30 分鐘音訊片段
│   ├── video_title_part2.mp3    # 第二個 30 分鐘音訊片段
│   └── ...                      # 更多音訊片段
└── MP4/                         # 影片片段專用資料夾
    ├── video_title_part1.mp4    # 第一個 30 分鐘影片片段
    ├── video_title_part2.mp4    # 第二個 30 分鐘影片片段
    └── ...                      # 更多影片片段
```

#### 不分割模式（--no-split）
```
video_title/                      # 主資料夾
├── video_title.mp4              # 原始影片檔案（1080p）
├── MP3/                         # 音訊資料夾
│   └── video_title.mp3          # 完整音訊檔案
└── MP4/                         # 空的影片片段資料夾
```

#### 只音訊模式（--audio-only）
```
video_title/                      # 主資料夾
├── video_title.mp4              # 原始影片檔案（保留）
├── MP3/                         # 音訊檔案（分割或完整）
│   ├── video_title.mp3          # 完整音訊檔案
│   ├── video_title_part1.mp3    # 音訊片段（如果分割）
│   └── ...
└── MP4/                         # 空資料夾（只處理音訊）
```

## 支援格式

- **YouTube 輸入**：所有 YouTube 影片 URL（自動下載最高 1080p 品質）
- **本地檔案輸入**：所有 FFmpeg 支援的視頻格式（MP4, AVI, MKV, MOV 等）
- **輸出格式**：MP4 視頻（1080p）+ MP3 音頻（320k）

## 使用範例

### 範例 1：YouTube 講座影片
```bash
# 下載一個 2 小時的線上講座並分割
python3 video-splitter.py --youtube "https://www.youtube.com/watch?v=ABC123"

# 輸出結構：
# 線上講座_題目/
# ├── 線上講座_題目.mp4              # 原始檔案（1080p）
# ├── MP3/
# │   ├── 線上講座_題目.mp3          # 完整音訊（320k）
# │   ├── 線上講座_題目_part1.mp3    # 0-30分鐘音訊
# │   ├── 線上講座_題目_part2.mp3    # 30-60分鐘音訊
# │   └── ...
# └── MP4/
#     ├── 線上講座_題目_part1.mp4    # 0-30分鐘影片
#     ├── 線上講座_題目_part2.mp4    # 30-60分鐘影片
#     └── ...
```

### 範例 2：podcast 節目
```bash
# 下載 podcast，只要完整音訊不分割
python3 video-splitter.py --youtube "https://www.youtube.com/watch?v=DEF456" --no-split

# 輸出結構：
# Podcast_節目名稱/
# ├── Podcast_節目名稱.mp4           # 原始影片（1080p 保留）
# ├── MP3/
# │   └── Podcast_節目名稱.mp3       # 完整音訊檔案
# └── MP4/                           # 空資料夾（未分割）
```

### 範例 3：本地影片處理
```bash
# 分割一個 2 小時的電影
python3 video-splitter.py movie.mp4

# 輸出結構：
# movie/
# ├── movie.mp4                      # 原始檔案（搬移到主資料夾）
# ├── MP3/
# │   ├── movie.mp3                  # 完整音訊（保留）
# │   ├── movie_part1.mp3            # 30 分鐘音訊片段
# │   ├── movie_part2.mp3            # 30 分鐘音訊片段
# │   └── ...
# └── MP4/
#     ├── movie_part1.mp4            # 30 分鐘影片片段
#     ├── movie_part2.mp4            # 30 分鐘影片片段
#     └── ...
```

## 錯誤排除

### FFmpeg 未找到
```
Error: FFmpeg is not installed or not found in PATH.
```
**解決方案**：確保 FFmpeg 已正確安裝並可在命令行使用

### yt-dlp 未安裝
```
ModuleNotFoundError: No module named 'yt_dlp'
```
**解決方案**：安裝 yt-dlp：`pip3 install yt-dlp`

### YouTube URL 無效
```
Error: Invalid YouTube URL
```
**解決方案**：確保使用正確的 YouTube URL 格式

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

### YouTube 下載失敗
```
Error: Failed to download video
```
**解決方案**：
- 檢查網路連線
- 確認 YouTube URL 是否有效
- 某些影片可能有地區限制或私人設定

### 影片品質問題
```
WARNING: You have requested merging of multiple formats but ffmpeg is not installed
```
**解決方案**：
- 確保 FFmpeg 已正確安裝並可在命令行使用
- 工具會自動檢測 FFmpeg 位置並下載 1080p 品質影片
- 如果仍有問題，請檢查 FFmpeg 安裝路徑

## 許可證

MIT License

## 更新紀錄

### v1.1 (最新版本)
- ✅ 新增 YouTube 影片下載支援（使用 yt-dlp）
- ✅ 重新設計檔案組織結構：主資料夾 + MP3/、MP4/ 子資料夾
- ✅ 永遠提取完整音訊檔案（320k 高品質）
- ✅ 新增 `--no-split` 選項：只提取音訊不分割
- ✅ 新增 `--audio-only` 選項：只處理音訊部分
- ✅ 智能檔案命名：自動清理特殊字符
- ✅ 保留原始下載檔案在主資料夾中
- ✅ 改善錯誤處理和使用者體驗

### v1.0
- 基礎影片分割功能
- 本地檔案處理
- 30分鐘片段分割
- 音訊提取功能

## 技術規格

- **支援的 YouTube 格式**：自動選擇最佳品質組合
  - 影片：1080p (format 137) → 720p (136) → 480p (135) → 最佳可用
  - 音訊：140 (m4a 128k) 或最佳可用
  - 自動合併為 MP4 格式
- **音訊品質**：320k MP3 高品質輸出
- **影片處理**：使用 FFmpeg copy 模式，無損快速分割
- **檔案安全**：自動清理檔名中的特殊字符，確保跨平台相容性

## 作者

Video Splitter Tool with YouTube Support