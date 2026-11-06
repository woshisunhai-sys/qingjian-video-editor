# AI 创剧客户端对接指南

该 Skill 是工作流程规范，并非内置模型/API。以下操作名称是**适配层建议**，不是假设你当前软件已有的真实函数名。客户端需要查询现有能力，把实际方法映射到这些动作。

## 需要提供的 9 类能力

1. get_asset_library(project_id)：读取 CURRENT_ASSET_LIBRARY，使用已有的场景、人物四视图、服装和道具资产。
2. get_storyboard(episode_id)：读取已确认的分镜/台词/起止状态；不修改原分镜 JSON。
3. open_position_editor(scene_id, version, assets, previous_layout?)：通过位置编辑器排布当前全局场景状态。
4. export_editor_layout(scene_id, version)：保存结构化坐标、角色/道具朝向、姿势、背景、机位轴线，可附布局指导图（仅供全局图生成）。
5. generate_global_reference(scene_id, version, scene_asset, character_refs, prop_refs, editor_layout, prior_global?, delta?)：调用 GPT Image 2 首次生成或局部更新全局参考图；输出永久保存且版本不可覆盖。
6. generate_shot_first_frame(shot_id, global_reference_image, prompt, optional_character_refs?)：直接使用当前全局图生成分镜首帧；不生产镜头位置参考图。
7. submit_h3_i2va(shot_id, first_frame, prompt, duration, idempotency_key)：真实提交 MiniMax H3 I2VA 任务并返回 task_id。
8. query_video_task(task_id) / save_video(task_id)：查询、下载、保存真实视频及失败原因。
9. review_and_trim(shot_id, video_file, target_cut_seconds)：检查角色、场景连续性、台词、可用片段并剪辑；在最后合成字幕/BGM/混音。

以上只是协议示例。若软件目前调用 ComfyUI 工作流或其他视频服务，先核实真实请求字段、鉴权、响应结构，再进行映射。不要杜撰 endpoint。

## DAG 任务执行顺序

1. 资产与分镜准备 → 逻辑场景状态规划。
2. 对每个场景创建全局图 v1。状态有持续变化才创建 v2/v3，依赖上一版本全局图和编辑器变更量。
3. 为每个镜头找到 global_state_in 的**现成全局参考图** → 生成该镜头首帧。
4. 首帧完成立即可以排队提交 H3 I2VA；**不等待其他镜头视频完成**。
5. 视频完成 → 质量检查 → 选择接受/裁剪/重试/跳过。
6. 全镜头可用片段整理后，按原分镜顺序完成后期合成。

示例：s001/s002/s003 的首帧均引用 livingroom_v1，s003 的 end_state= livingroom_v2；s004 的首帧必须引用 v2。生成 v2 不强制等待 s003 的 H3 视频完成，但如果 s003 最终失败，提示镜头过渡缺失。

## 错误、并发、数据一致性

- 图片任务队列、视频任务队列分离，按各自服务限速和费用控制并发。
- 任务保存状态、真实 job ID、幂等键、重试次数、失败原因；支持恢复运行，避免重复付费。
- planned/blocked 不可冒充 accepted；ready 需要真实 first_frame_image；submitted 需要真实 task_id；accepted/trim 需要真实视频文件。
- 失败最多按 config.max_video_retries 重试，仍失败则根据配置跳过或标注 manual_review；关键转场失败时写 continuity_warning。
- 独立镜头继续推进，不因为无关任务失败而中断全剧。
- 若不存在任何图像/H3 API，Skill 只输出计划、提示词和明确待连接能力，绝不伪造生成结果。
- 路径要经项目媒体存储/ComfyUI 路径解析器校验，不能信任客户端传入的任意本地路径。
