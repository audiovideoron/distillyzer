# Session Summary: A Gathering of Words
**Date:** 2026-01-02

## The Poem

```
A Gathering of Words

Why write?
Because, I don't like to be left out.
And I am on the wrong side of the fence
Looking at a gathering of words.
```

## What We Built

1. **Project created:** `a-gathering-of-words` (id: 2) in Distillyzer
2. **New CLI feature:** `--artistic` / `-a` flag for `dz visualize`
   - Committed and pushed to main
   - Generates evocative imagery instead of diagrams
3. **New skill created:** `/linkedin-post` at `.claude/skills/linkedin-post.md`
   - Not yet loaded (requires Claude restart)
4. **GitHub Issue #4:** "Define workflow for researching and scaffolding new applications"

## Key Discoveries

### Nano Banana (Gemini Image Gen) Limitations

1. **No iteration capability** - Each generation is independent. You cannot say "keep the room but change the text." It rebuilds from scratch every time.

2. **Prompts are suggestions, not instructions** - The model interprets loosely. Asking it to "not change the room" results in a different room.

3. **Text placement is unreliable** - Getting specific text to appear "projected onto a wall" vs "floating in space" is not controllable through prompting alone.

4. **Style consistency is hard** - Each generation can drift in style, lighting, composition.

### The Right Approach (Probably)

- **Compositing:** Generate base image, overlay text separately
- **Use right tool for each job:** Image gen for atmosphere, typography tools for text
- **Understand tools before building workflows around them**

### Distillyzer's Role

Important realization: **Distillyzer is the forge, not the sword.**

- Distillyzer should research and scaffold OTHER applications
- "A Gathering of Words" should become its own app, not a Distillyzer feature
- Different projects need different illustration styles (poetry vs video flicker)
- Use `dz project` to track research, then scaffold separate repos

## Illustration Direction (For Future Reference)

The user's vision for "A Gathering of Words" illustration:
- Dark, dimly lit 1970s Los Angeles flophouse room
- Writer as silhouette at typewriter (not prominent)
- Bare lightbulb (not candle)
- Curtained window with streetlight outside
- **The poem text projected through the window onto the wall**
- Soft, hazy, painterly style (not photorealistic)
- Words should be CAST onto the wall surface, not floating
- The poem is the hero of the image

Best attempt saved at: `images/gathering-of-words/dark_shadowy_room_shrouded_in_.png`

## LinkedIn Post Draft

```
Tried to create an illustrated poem with AI today.

The poem was 4 lines. The image generation took 8+ attempts.

Here's what I learned: text-to-image AI can't iterate.

When I said "keep the room dark but fix the text placement," it generated an entirely new room. Brighter. Different furniture. The only thing it kept was... nothing.

Each generation is independent. There's no memory. No "change just this one thing." It rebuilds from scratch every prompt.

I was fighting a fundamental limitation I should have named upfront instead of burning an hour on retry loops.

The actual fix? Probably compositing - generate the base image, overlay text separately. Use the right tool for each job instead of asking one tool to do everything.

Sometimes the best outcome from an experiment is knowing what NOT to build on.

What tools have you tried to force into workflows they weren't designed for?

#aitools #llm #buildinpublic
```

## Files Changed This Session

- `src/distillyzer/visualize.py` - Added `create_artistic_prompt()` and `artistic` parameter
- `src/distillyzer/cli.py` - Added `--artistic/-a` flag to visualize command
- `.claude/skills/linkedin-post.md` - New skill (created)
- `.env` - Added `GEMINI_MODEL="gemini-2.5-flash-image-preview"`

## Next Steps

1. Restart Claude to load the linkedin-post skill
2. Research compositing approach for illustrated poetry
3. Define the workflow for how Distillyzer researches and scaffolds new apps (GitHub #4)
4. Consider what "A Gathering of Words" looks like as its own application
