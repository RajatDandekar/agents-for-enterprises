# Lecture films: the quality bar and the house style

Rajat, 2026-10-30: "Visualisations should be detailed with a lot of clarity. This is the level I am looking at: https://www.youtube.com/watch?v=EfYWEXnfXA8 (Vizuara, *Inside Rubin: NVIDIA's most powerful AI chip*). This is the quality I want… with such an engaging narration… All these can be made much more comprehensive and beautiful."

## The reference (watch it first)
"Inside Rubin" (4:41) is a photoreal **Blender Cycles** film:
- detailed physical models (the package, dies, HBM stacks);
- a bright, diffuse studio;
- slow, deliberate camera moves;
- exploded views that open up to show what is inside;
- crisp 2D labels pinned over the render ("8 DRAM dies of 2 GB = 16 GB");
- subtitles;
- a calm, confident narrator telling one clear story from the outside in.

It was made with the Vizuara cinematic pipeline at `/Users/raj/Claude_Brain/programmatic-video-ads/`. Read these before building:
- `skill/cinematic-3d-edit/SKILL.md`;
- `ref/blender-3d.md`, `ref/world-and-theme.md`, `ref/text-overlays.md`, `ref/sound-design.md`, `ref/render-and-composite.md`;
- above all `ref/lessons-log.md`.

The scene code to learn from is `projects/sep25-kernel/blender2/` (the accepted Kernel v3 look). There is no speaker footage here, so skip the matting steps.

## What Rajat has praised and rejected (from the lessons log and this course)
**Praised:**
- photoreal Blender worlds;
- a bright diffuse studio;
- detailed models;
- typed titles;
- word-synced 2D overlays;
- powerful but tasteful music;
- real visualisations, not text cards.

**Rejected:**
- childish, boxy 3D;
- unreadable text inside the 3D (put text in pinned 2D overlays);
- a reused look;
- figurine people (show people by their presence: a chat bubble, a screen, a desk);
- negative or meta framing;
- anything that is not explained.

## The house style for course films
- **Story first.** Each film explains **one idea** on **the same running example the slides just taught** (Emma Clarke, Northbridge Cycles, the real recorded trace). It plays at the **end** of its section, after Rajat has taught the theory, as the beautiful recap that makes it click. It never introduces a term the slides have not.
- **Length.** 60–150 s each, with a clear beginning, middle and end.
- **Picture.**
  - Render in Blender Cycles on Modal GPU (never on the laptop), 1920×1080 at 30 fps.
  - Use detailed, believable models. Tokens are physical tiles. Vectors are columns of glowing cells with real values. Attention is light passing between tiles, its weight shown as brightness. The model is a machine with 24 floors, opened up.
  - Use a bright, diffuse studio with soft shadows and depth of field. Turn visible_glossy off so there are no light-shaped reflections.
- **Text.** All readable text is 2D, composited over the render: pinned labels, number punches, typed titles, subtitles. Use Google Sans Flex. The palette is sky blue `#3c90ff` / `#0b57d0` for the model, ember `#c4511f` for invented or legacy, and green `#1e8e5a` for facts.
- **Narration.** ElevenLabs "Daniel" (`onwK4e9ZLuTAKqWW03F9`, professional British, `eleven_multilingual_v2`). The key is in `/Users/raj/Claude_Brain/cobol-mainframes/.env`; never print it.
  - The script is engaging, plain and concrete: short sentences, real numbers, and a question or turn every 15–20 s.
  - Key every visual beat to a spoken word using ElevenLabs character timings.
- **Music and sound.** Use a calm, inspiring Epidemic Sound bed under the voice, about −20 dB below speech and up in the gaps. Pick a different track from the L1 film's "Envision". Add soft, designed SFX on reveals.
- **Credits** go on a small end card, including the music credit.
- **Numbers.** Every number comes from a recorded run in the course (`flow3d/trace.json`, `brain3d/trace.json`, `experiments/logs`) or is plainly labelled.
- **Delivery.** H.264 mp4 with faststart (plus a WebM copy) and a poster JPG. Keep each file under about 25 MB. Embed with `<video controls>` (never autoplay), plus a "Present" full-screen option.
- **Licensed music** is never committed: `lectures/*/films/music/` is gitignored, and the site build copies the files from disk.

## Process
1. **Style frame first.** Render 3–4 stills of the first film's key shots and look at them critically against the Rubin frames. If they look boxy or toy-like, fix them before rendering motion.
2. Render the frames in parallel chunks on Modal. Composite the overlays, voice and music on Modal with ffmpeg (or skia), not on the laptop.
3. Check by looking: extract frames at every beat, and read the subtitles against the audio timings.
4. Write `films/FILMS.md` with each film's script, shots, durations, provenance and credits.
