# AI 视频分析提示词模板

将提取的关键帧 + structure.json 喂给视觉模型进行结构化分析，
以下为各维度的提示词模板。

---

## 1. 视觉风格分析

```
Analyze the following key frames from a trending TikTok video.

Provide a structured analysis of the visual style:
- Color palette: dominant colors, warm/cool tone, saturation level
- Filter/grading: what color grading or filter is applied
- Text overlay style: font type, size, color, position, animation (fade/slide/pop)
- Transition types between scenes: cut, dissolve, zoom, swipe, morph
- Camera angle: top-down, eye-level, low angle, handheld vs stabilized
- Aspect ratio usage: how is the 9:16 vertical frame utilized

Output as JSON with keys: color_palette, filter_style, text_overlay, transitions, camera, framing
```

## 2. 内容结构分析

```
Analyze the content structure of this TikTok video using the provided key frames
and scene timestamps.

Break down:
- Hook (0-3s): what grabs attention in the first 3 seconds
- Body: how information/content is delivered (step by step, reveal, build-up)
- Climax/payoff: the main satisfying moment or key information
- CTA/ending: how the video ends (call to action, loop point, cliffhanger)
- Pacing: fast cuts vs slow lingering shots, rhythm pattern

Output as JSON with keys: hook, body_structure, climax, ending, pacing_bpm
```

## 3. 音频模式分析

```
Given the audio track and video structure of this TikTok:

Analyze:
- Music genre and mood (upbeat, chill, dramatic, trending sound)
- Beat synchronization: are visual cuts aligned with music beats
- Voiceover: is there narration, what style (conversational, educational, dramatic)
- Sound effects: any additional SFX (whoosh, pop, ding)
- Audio-visual sync pattern: how audio reinforces visual transitions

Output as JSON with keys: music_genre, mood, beat_sync, voiceover_style, sfx, av_sync_pattern
```

## 4. AI 复刻方案生成

```
Based on the visual style, content structure, and audio analysis of this
trending TikTok video, generate a step-by-step replication plan for AI
video generation.

Include:
1. Shot list: ordered list of scenes with description, duration, camera angle
2. Visual assets needed: what images/videos to generate per scene
3. Text overlays: exact placement, timing, and style for each text element
4. Audio plan: music style, voiceover script outline, SFX timing
5. Recommended AI tools for each step:
   - Image generation: Midjourney / DALL-E / Flux
   - Video generation: Runway Gen-3 / Kling AI / Pika
   - Voice: ElevenLabs / Azure TTS
   - Editing: CapCut / Premiere with AI plugins
6. Estimated generation cost (API calls / credits)

Output as a structured JSON production plan.
```

## 5. 病毒传播性分析

```
Analyze why this TikTok video likely went viral. Consider:

- Hook effectiveness: does it stop the scroll in 1-2 seconds
- Emotional trigger: curiosity, satisfaction, surprise, humor, FOMO
- Shareability: would viewers share this, and why
- Comment bait: does it encourage comments (controversial, relatable, askable)
- Trend alignment: does it ride a current trend/sound/format
- Completion rate signals: is it designed to be watched fully or looped

Output as JSON with keys: hook_score (1-10), emotion, share_factor, comment_bait,
trend_alignment, loop_design, overall_virality_score (1-100)
```

---

## 使用方法

1. 用 `analyze-video.sh` 提取帧和 structure.json
2. 将 `frames/` 目录中的关键帧图片作为视觉输入
3. 将 `structure.json` + `metadata.json` 作为文本上下文
4. 按需选择上述模板喂给视觉模型（如 GPT-4o, Claude 3.5 Sonnet）
5. 综合各维度输出，生成完整的 AI 复刻方案
