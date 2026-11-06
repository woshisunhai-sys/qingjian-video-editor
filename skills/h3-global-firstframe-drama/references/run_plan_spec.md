# 运行计划 JSON 规范（sidecar v1.0）

本文件定义独立的 run_plan.json；原项目的七字段分镜 JSON **不得覆盖或改写**。通过 source_shot_id 关联已有分镜。

## 关键约束

- scenes[] 保存物理场景和原始资产；global_states[] 保存场景全局参考图的不同持续状态版本；shots[] 保存每镜的生成计划/运行结果。
- global_state_in 决定**首帧引用哪一版全局图**；global_state_out 表示镜头结束后逻辑上进入的持续状态。
- 位置编辑器输出只保存在 global_states[].editor_layout，不给每镜再生成 position_reference_image。
- 变化镜头：首帧用旧版；下一镜开始使用新版。全局图的新版本通过编辑器更新，不要求使用前镜尾帧。
- global_reference_image、first_frame_image、video_file 在未生成时必须为 null；不能凭空填入不存在的路径。
- scenes、global_states 和 shots 在规划态可包含预期资源路径，运行前必须实际验证素材是否存在（文件或客户端资产库）。

## 顶层 JSON

~~~json
{
  "schema_version": "1.0",
  "episode_id": "EP001",
  "config": {
    "image_model": "gpt-image-2",
    "video_model": "MiniMax-H3",
    "video_mode": "I2VA",
    "allow_fl2va_fallback": false,
    "max_video_retries": 1,
    "skip_failed_shots": true,
    "max_parallel_video_jobs": 3
  },
  "scenes": [],
  "global_states": [],
  "shots": []
}
~~~

## scenes[]

- id：物理场景 ID。
- scene_reference_image：已有场景资产图片路径或客户端资产 URI。
- character_reference_images：按 character_id 索引的参考图路径数组。
- prop_reference_images：按 prop_id 索引的参考图路径数组。

## global_states[]

- id：例如 livingroom_v1、livingroom_v2。
- scene_id、parent_state_id：关联物理场景和上一状态；v1 的 parent_state_id=null。
- change_reason：创建/更新全局图的持续变化原因。
- editor_layout：人物/道具坐标、朝向、姿势、当前布景等；坐标系全程一致。
- global_reference_image：实际主全局图路径；未生成时 null。
- status：planned、ready、failed 或 blocked。

## shots[]

必填核心：
- id、source_shot_id、scene_id；
- global_state_in、global_state_out；
- camera、start_state、main_action、end_state；
- first_frame_prompt、h3_prompt；
- generation_duration_seconds（整数、符合当前 H3 API 能力）、target_cut_seconds（大于 0 且不超过生成时长）；
- first_frame_image、video_file（未生成时 null）；
- video_mode（默认只能 I2VA）；
- status（planned、blocked、ready、submitted、accepted、trim、retry_i2va、skipped、manual_review）。

可选运行记录：
- dependencies：前置任务/全局图/首帧的任务 ID 数组；引用的任务必须存在、不得循环依赖。
- task_id：H3 实际提交后返回的真实任务 ID。
- retry_count：非负整数；不得超过配置上限而继续自动提交。
- failure_reason、continuity_warning、trim_range_seconds、quality_checks、updated_at。

## 静态校验

在 Skill 根目录执行：

~~~bash
python scripts/validate_run_plan.py examples/example_run_plan.json
~~~

- 校验 ID 唯一性、场景与版本引用、父子链无循环、镜头起止连续性、禁止逐镜位置参考图、状态与任务必填项、视频模式与时长、依赖关系等。
- 规划态允许未生成素材路径为 null。例子中的 assets/... 是演示占位路径，**不得当成真实存在的媒体文件**。
- 静态校验不等于真实文件存在性/模型生成质量检查；客户端进入任务执行前需验证文件存在及权限。
