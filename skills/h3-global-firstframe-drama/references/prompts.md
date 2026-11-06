# 提示词模板：全局参考图 → 分镜首帧 → MiniMax H3 I2VA

这些模板是给 AI 创剧客户端使用的指令规范，不代表模型已生成图片或视频。所有 {变量} 必须从剧本、资产库、位置编辑器和实际适配层填入，不得虚构。

## 1. GPT Image 2：首次生成全局参考图

输入：
- 场景原始参考图 {scene_asset_image}
- 人物参考图 {character_ref_images}（优先四视图、当前服装状态）
- 重要道具参考图 {prop_ref_images}
- 位置编辑器布局 {editor_layout}（坐标、站姿、朝向、道具归属、相机轴线）
- 当前场景状态 {global_state_id}

提示词（英文结构化，必要中文内容保留）：

~~~text
Create ONE cohesive cinematic MASTER GLOBAL REFERENCE image.
Environment source of truth: {scene_asset_image}.
Identity/wardrobe source of truth: {character_ref_images}.
Prop appearance source of truth: {prop_ref_images}.
Spatial layout source of truth: {editor_layout}.

Scene: {scene_description}
Room geometry and permanent features: {fixed_geometry}
Character positions, orientation, poses and wardrobe: {characters_editor_positions}
Prop positions, orientation and ownership: {props_editor_positions}
Lighting, time of day, visual style: {lighting_and_style}
Global state ID: {global_state_id}

Respect exact spatial relationships and character identities.
Output ONE master reference view, NOT a storyboard collage,
NOT a positioning schematic, NOT a shot-by-shot guide.
No arrows, labels, UI marks, watermark or text overlay.
~~~

检查：场景结构不变、门窗家具方向正确、角色不重复、站位/道具清楚，所有引用的资产真实存在。生成结果存到 global_states[].global_reference_image，保留历史版本，不得覆盖。

## 2. GPT Image 2：更新全局参考图 v2/v3...

输入：旧版全局参考图 {previous_global_image}、上一版编辑器布局、当前编辑器布局、状态差异 {state_delta}、必要原始角色/场景/道具参考。

~~~text
Edit the PREVIOUS master global scene image into a NEW persistent state.
Old state: {parent_state_id}; new state: {global_state_id}.
Apply ONLY these persistent changes: {state_delta}.
Follow updated editor layout exactly: {editor_layout}.
Preserve all unaffected room geometry, background, characters,
wardrobe, furniture, lighting style and other prop positions.
Maintain coherent spatial scale, perspective and identity.
Render one clean master scene reference image.
Do not create a per-shot placement guide or multiple frames.
~~~

只有持续站位/姿势/朝向、重要道具/门窗状态、服装/场景持续变化才新建版本；表情、瞬时动作、景别及机位变化不更新。

## 3. GPT Image 2：每镜直接从全局图生成首帧

输入：当前镜头 global_state_in 对应的 {global_reference_image}、分镜起点状态、机位/景别、原始角色/道具参考（仅当需要修补细节）。**禁止制作新的逐镜位置参考图。**

~~~text
Generate ONE cinematic FIRST FRAME for shot {shot_id}.
MASTER SPATIAL AUTHORITY: {global_reference_image} of {global_state_in}.
Preserve stable room layout, character identities and wardrobe,
starting positions, orientation and persistent prop states.

Camera angle/height/shot size: {camera}
Visible scene geometry from this exact camera direction: {visible_background}
Characters/props at shot START: {start_state}
Emotions and light: {expression_and_lighting}
Action that MUST occur AFTER this first frame: {main_action}.
Never show the completed action or the next scene's state prematurely.

Output ONE clean FIRST frame only. No storyboard grid,
position guide, annotations, subtitle or watermark.
~~~

审查重点：人物左右与站位、特写的背后背景、角色是否提前完成动作、是否增加不存在的家具或人物。失败只重试本镜首帧，不无故重建全局图。

## 4. MiniMax H3：统一 I2VA 首帧生视频

首帧作为实际视频 API 的图片参数上传或引用；文本中的 Picture 1 仅指该分镜首帧，**不是全局参考图**。不要仅把本地路径写在文字中冒充实际图片输入。

~~~text
For the target video, at 0.00 seconds into the target video,
<Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description:
[Shot 1] Start exactly from the provided first frame.
Keep identities, clothing, scene geometry and established
positions consistent. Continuous single shot of {duration}s.
Subject performance: {performance}.
Action progression: {main_action}.
Camera behavior: {camera_motion}.
End state: {end_state}.
Spoken content: {dialogue_or_voiceover}.

overall_soundscape:
{ambient_sound}; {action_sound}; {nonverbal_sound}.
Do not invent additional dialogue.

non_diegetic_music: none
~~~

### 4.1 语言/声音类型

- 角色对白：On-screen spoken dialogue by {character_id}, with accurate lip movement: "{中文原文}". 仅该角色口型同步。
- 内心独白：Voice-over internal monologue for {character_id}, off-screen audio only; NO visible character mouth movement: "{中文原文}".
- 旁白：Off-screen narrator voice-over; NO lip sync: "{中文原文}".
- 无台词：No dialogue, no voice-over.
- 所有台词保留用户确认的中文原文，不把内心独白自动转换为角色开口说话。
- 一角色一固定音色；若 H3 实际接口无法可靠绑定音色，交给后期 TTS/配音，不宣称模型自动完成。
- 对话镜头保持紧凑；避免无意义停顿、过长纯动作镜头。整集 BGM 在剪辑合成阶段统一添加。
- 如 H3 返回视频时长比成片所需长，只截取可用片段；generation_duration_seconds 是 API 支持的单次生成时长，target_cut_seconds 可更短。

### 4.2 补救

默认只走 I2VA；先在同模式优化提示词/首帧重试。仅当项目明确 allow_fl2va_fallback=true 且有 I2VA 失败记录时，才允许对单镜使用 FL2VA；否则跳过并标记剧情连续性风险。

说明：如项目已安装 MiniMax H3 官方提示词 Skill，可结合其当前 I2VA 规范调整具体接口字段。模板中的参数应以当前实际 API 能力为准。
