# Reference Video Analysis

## Sample Clip

- Source file: `../daily-video-studio/TKhdS4FDGGh0_cWN.mp4`
- Detected duration from Windows metadata: about 19 seconds
- File size: about 862 KB

## Likely Production Workflow

The reference clip is likely made with a simple AI-video assembly pipeline instead of manual editing-heavy production.

### 1. Choose one narrow subject

The video probably follows one building project rather than many unrelated scenes. That makes the clip easy to understand in a short runtime.

### 2. Split the build into discrete stages

A typical sequence is:

1. empty site or excavation
2. foundation or base structure
3. rapid structural growth
4. outer facade completion
5. detail finishing and surroundings
6. completed hero reveal

### 3. Generate stills or keyframes first

The most stable workflow is to generate one image per stage with consistent architecture, camera position, materials, and environment.

### 4. Turn images into short motion clips

Each still is then converted into a 3 to 4 second motion shot using an image-to-video model. Motion is usually subtle:

- crane movement
- dust and workers
- concrete pouring
- facade installation
- camera push or drone rise

### 5. Concatenate clips

A final editor or script assembles the short clips in order. The reference project in this workspace already uses FFmpeg concat for this pattern.

## Design Implications For The New Agent

- Default to 6 segments
- Default to about 3.2 seconds per segment
- Keep one building identity across all segments
- Use English prompts for image/video APIs
- Generate Chinese narration and on-screen text
- Allow planning to work even when media APIs are not wired yet
