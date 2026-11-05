# 轻剪视频剪辑 · Qingjian Video Editor

[Windows 1.8.0 免安装版](https://jianji.aichuangju.com/qingjian-license/download/Qingjian-Portable-1.8.0-x64.exe) · [官方网站](https://jianji.aichuangju.com/) · [GitHub Releases](https://github.com/woshisunhai-sys/qingjian-video-editor/releases) · [使用说明](https://jianji.aichuangju.com/qingjian-license/download/Qingjian-Windows-1.8.0-guide.txt)

轻剪用于导入、裁剪和拼接本地视频，添加字幕、背景音乐与配音，再合成为完整视频。本仓库发布公开安装包、说明和问题反馈，软件为专有授权产品。

## Windows 1.8.0 · 2026-11-06

- 选中视频 →“变速”→ 1.2× / 1.5× / 2×，1× 恢复，每段可单独设置。
- 原声同步变速并保持音调，字幕、片段时长和源时间音量关键帧同步调整。
- 背景音乐和独立配音保持原速度。
- 分镜独立音量，支持 0 / −3 / −6 dB 预设及自定义增益。
- 一键统一所有分镜响度，默认目标约 −16 LUFS。
- 对白模式先在本机检测语音片段，再分析与统一对白响度。
- 最终混音默认限制到 −1 dBTP，编码完成后复测真峰值。
- 局部音量关键帧与“只压低这一段”，可处理过响的句子。
- 移除时间线上新增的“前移、后移”按钮，仍可拖动排序。
- 保留本机自动字幕、手动字幕、SRT 导出、录音与系统文字配音。

统一后增益微调归零，关键帧保留。弱音最多提升 12 dB。音质、背景音乐与口音会影响自动字幕及对白分析，请试听并校对。

![变速选项，本地演示使用测试素材](https://jianji.aichuangju.com/qingjian-license/press/qingjian-speed-1.8.0.png)

![音量面板，本地演示使用合成素材](https://jianji.aichuangju.com/qingjian-license/press/qingjian-audio-1.7.0.png)

## 下载

| 版本 | 平台 | 说明 |
| --- | --- | --- |
| [Windows 1.8.0](https://jianji.aichuangju.com/qingjian-license/download/Qingjian-Portable-1.8.0-x64.exe) | Windows 10 / 11 x64 | 单文件 EXE，免安装，内置语音模型 |
| [Android 1.5.1](https://jianji.aichuangju.com/qingjian-license/download/Qingjian-Android-1.5.1-Test.apk) | Android APK | 本次没有更新安卓包，新增音量功能属于 Windows 版 |

## 使用与授权

1. 打开软件，领取本设备一次 24 小时免费试用，或输入购买的授权码。
2. 导入视频，在播放头处分割、裁头、裁尾或删除多余片段，拖动排序。
3. 生成或编辑字幕，添加配音和音乐，按需调整分镜音量与关键帧。
4. 预览并导出，提供 720p / 1080p 选项，格式取决于设备编码支持。

支持十种界面语言，默认跟随设备。视频、音乐、语音识别及音频分析在本机处理。激活、授权验证及导出授权检查需要联网。

下载免费，试用后需付费授权，购买链接、币种和各期限价格以官网对应渠道为准。一个授权码绑定一台设备，期限从首次激活开始。当前没有工程自动保存，退出前请导出保存。Windows 当前没有商业代码签名证书。

## English

Qingjian Windows 1.8.0 is a portable single-file video editor for 64-bit Windows 10/11. Import, split, trim and join local video clips, generate editable captions with a bundled local speech model, add manual subtitles or export SRT, record voiceovers, and use installed Windows text-to-speech voices.

Per-clip speeds of 1.2x, 1.5x and 2x preserve original-audio pitch and retime captions, clip duration and source-anchored volume keyframes. Choose 1x to reset. Music and independent voiceovers retain their speed.

The audio panel includes per-clip gain, loudness normalization with a default −16 LUFS target, dialogue analysis using local voice activity detection, volume keyframes and a range-duck tool. The final mix uses a default −1 dBTP ceiling and is measured again after encoding. Quiet-source boost is limited to 12 dB. Normalizing resets clip gain offsets and preserves keyframes. Review the audio and automatic captions before publishing.

Ten UI languages follow device settings or can be selected manually. Media processing stays on the computer; licensing requires Internet access. The download is free with one 24-hour trial per device, then paid device-bound activation is required. Purchase options are on the official website. Export before closing because project autosave is unavailable. Android remains at 1.5.1 in this release.

## SHA-256

Windows 1.8.0 x64, 378,051,718 bytes:

`a1c5f02d28399e49fd07b9ebab6c8dffb9096d17c09e2ec69166f1078a81e955`

Android 1.5.1 APK:

`8185608862cd874f839bfbf8b6b68c44a03b268bac66edbf0bb2d3efe9fb311e`

## 联系 / Contact

个人开发者 / Independent developer  
黄伟 / Wei Huang · Qingjian · woshisunhai@gmail.com

欢迎通过 Issues 反馈复现步骤、系统版本和报错。请勿公开授权码、密码或私人素材。
