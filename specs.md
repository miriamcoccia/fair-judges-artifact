# Building mmvalidator — a tutorial

This is written like a course, not a spec. Read one section at a time.
Do the section. Check it worked. Move on.

No step assumes you remember the one before it perfectly. If something
doesn't make sense, that's not you missing something — come back and
we'll slow down further.

---

# Part 1 — What are we actually building?

Forget code for a second. Here's the idea, told as a story.

You have a school test question with a picture. You want to know:
is this a *good* test question?

To check that, you do six things, one after another:

1. **Read the question and picture into the computer.**
   Just loading it, nothing clever yet.

2. **Break it, on purpose, in a way you control.**
   For example: rotate the picture upside down.
   Now you know for a fact this item is broken — you broke it.
   That's the trick. You don't need a human to tell you it's bad.
   You already know, because you did it.

3. **Write a message asking an AI model to check it.**
   "Here's a question and a picture. Tell me if anything's wrong."

4. **Send that message and get the AI's answer back.**

5. **Compare.**
   You expected: "this is broken."
   Did the AI say that? If yes — good, it caught it.
   If no — it missed it.

6. **Do this thousands of times, and count how often it gets it right.**
   Then turn the counts into tables and charts.

That's the whole project. Six steps, done over and over, on lots of
questions, with different AI models, and different kinds of damage.

---

## Why do we split this into folders at all?

Because each of those six steps is its own little job, and jobs get
confusing when they're tangled together.

Imagine cooking a meal where the shopping list, the recipe, and the
washing-up are all written on the same piece of paper, out of order.
You'd lose track of what you'd already done.

So we give each step its own space:

| Step | Folder name | In plain words |
|---|---|---|
| 1. Read it | `data` | loading the questions |
| 2. Break it | `mutations` | damaging things on purpose |
| 3. Ask | `prompting` | writing the message to the AI |
| 4. Send | `providers` + `execution` | talking to the AI companies, and keeping track of what's done |
| 5. Compare | `evaluation` | turning answers into numbers |
| 6. Draw | `reporting` | turning numbers into tables and charts |

Plus one more folder that isn't a step — it's just the **shared
words** everyone uses. It's called `domain`. It holds things like
"what is a Question", "what is an Answer". Every other folder uses
these words, so we only want to define them once.

---

## Three ideas that keep 171,000 phone calls from becoming chaos

You're going to send roughly **171,000 messages** to AI companies over
the course of this project. That's a lot. Three simple ideas keep
that manageable.

### 1. A receipt number for every message

Every single message you send gets its own unique label, built from
everything that makes it unique: which question, which AI model,
which kind of damage, how severe, which attempt number.

Why this matters: if your computer crashes halfway through, you don't
want to start over. You want to say "give me a receipt for everything
I haven't done yet" and carry on exactly where you left off.

### 2. A checklist of what's already done

Before sending a message, you check: "do I already have this receipt?"
If yes, skip it — you already have the answer.

This is what makes stopping and restarting completely safe. You will
stop and restart a lot. Laptops sleep, wifi drops, batch jobs take
hours. This checklist means none of that is scary.

### 3. A label on the folder of results

Imagine finding a box of research results in six months with no note
attached — no idea which experiment made them. Not useful.

So every batch of results gets a small label file next to it, saying:
which AI models were used, which version of your code produced them,
and when. That way, months later, you can always answer "what
produced this table?"

---

## Two words that will come up a lot

**"A rulebook that anything can follow."**
In code this is sometimes called a "Protocol." It just means: instead
of writing "if this is ScienceQA, do X, but if it's the OAT dataset,
do Y" — you write one rulebook that says "any dataset must be able to
give me its questions, and tell me its name." Then your code doesn't
care which dataset it's looking at. This means adding a new dataset
later never requires rewriting the pipeline.

**"A phonebook."**
Instead of guessing which AI company made a model by looking at its
name (fragile — breaks the moment a new model has an unfamiliar
name), you write it down once in a small list:

```
"gemma-3-27b"  →  made by Nebius
"gpt-5-mini"   →  made by OpenAI
```

Adding a new model later means adding one line to this list. Nothing
else changes.

---
---

# Part 2 — Setting up your computer (do this first)

Before writing any code, you're setting up an empty, clean workspace.
Think of it as clearing your desk before you start a big project.

### Step 1 — Open your terminal

The terminal is the black text-box app on your computer where you
type commands instead of clicking. On a Mac it's called "Terminal."

### Step 2 — Go to your projects folder

```
cd ~/projects
```

`cd` means "go to this place." If this folder doesn't exist yet,
say so and we'll make it first.

### Step 3 — Make a new folder for this project

```
mkdir mmvalidator
cd mmvalidator
```

`mkdir` makes a new folder. The second line moves you inside it.

### Step 4 — Turn it into a git project

Git is the tool that remembers every version of your code — like
"track changes," but for code, forever.

```
git init
```

### Step 5 — Set up your Python tool

We're using a tool called `uv`. Its only job: keep track of which
Python libraries your project needs, so the project runs the same
way on your laptop and on the HPC cluster later.

```
uv init --package --name mmvalidator
```

### Check it worked

```
ls
```

`ls` lists what's in the current folder. You should see a few new
files that `uv` created automatically — things like `pyproject.toml`
and a `src` folder. You don't need to understand them yet. Their
presence means it worked.

**Stop here for today if this is your first session.** That's
genuinely a full, complete step. Nothing was skipped.

---
---

# Part 3 — The rest of the setup (small housekeeping files)

These are five small files that protect you from common beginner
mistakes — the kind that cost people days later. Doing them now, while
the project is empty, is much easier than fixing them once it's full.

### 1. Telling git what to ignore

Some files shouldn't be tracked by git — big data files, temporary
files, secret passwords. You list them in a file called `.gitignore`.

Create a file named `.gitignore` in your project folder, and put this
inside it:

```
data/
runs/
.venv/
.env
.DS_Store
__pycache__/
```

**Why this matters:** your old project accidentally saved 208
megabytes of images into git. That makes the project painful to
download and slow to work with. This file prevents that from ever
happening again.

### 2. A safe place for secret passwords (API keys)

You'll need API keys — secret passwords that let your code talk to
OpenAI, Nebius, Anthropic. These must never be shared publicly.

Create a file named `.env.example`:

```
OPENAI_API_KEY=your-key-here
NEBIUS_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
```

This is a *template*, safe to share — it has no real keys in it.
Later, you'll copy it to a file called `.env` and put your real keys
there. `.env` is already in your `.gitignore`, so it never gets
uploaded anywhere.

### 3. An automatic checker that catches mistakes before you commit

This is a tool called `pre-commit`. Every time you try to save
("commit") your code, it automatically checks for common mistakes —
messy formatting, and (importantly) accidentally trying to save a huge
file.

You'll set this up together when we get to the code — for now, just
know it exists and what it's for: **a safety net that catches
mistakes in two seconds, instead of you finding them two weeks
later.**

### 4. A README

This is the very first thing anyone opens when they find your
project — including you, in six months, having forgotten everything.
It should say: what this project does, how to install it, how to run
it. We'll write this properly near the end, once there's something to
describe. For now, just create an empty `README.md` file as a
placeholder.

### 5. A test folder

Create a folder called `tests`. This is where you'll keep small
scripts that check your code actually does what you think it does.
We'll fill it in as we go — one small check at a time, right after
you write each piece of real code. Never far behind it.

---
---

# Part 4 — The building blocks (the shared vocabulary)

Remember `domain` — the shared words folder? This is the very first
real code you'll write, because everything else depends on it.

Here's what goes in it, described simply.

### A "Quality Property"

You already have six things that make a test question good or bad:

- does the picture actually help answer the question?
- is the picture cluttered or clear?
- is the picture good technical quality (sharp, well-lit)?
- is the picture the right way up?
- does the picture match the text?
- is the picture fair and unbiased?

In code, you'll write these six as a small fixed list, so the
computer always knows there are exactly six, no more, no less, and
what each one means.

### An "Item"

This is your word for "one test question." It holds: the question
text, the possible answers, which one is correct, and the picture(s)
that go with it.

### A "Verdict"

This is your word for "what the AI decided." For one question, the
AI gives back six answers — one per quality property — each saying
valid or not valid, with a reason why.

**Why build these first:** every other part of the project — loading
data, breaking images, asking the AI, comparing answers — talks about
"Items" and "Verdicts." If you define these clearly once, everything
downstream is easier to write and easier to trust. If you don't,
you'll end up describing "a question" slightly differently in five
different files, and something will eventually not match up.

**How you'll know this part is done:** you can create a fake test
question in a tiny test script, and it holds together correctly —
right number of answer choices, a valid picture, nothing missing.

---
---

# Part 5 — The six ways of breaking a question, on purpose

This is the heart of your whole project — the part that becomes your
actual contribution to the paper.

For each of your six quality properties, you invent a way to damage
a good question so that it now clearly fails on that one property.
And you do it at **three strengths**: barely noticeable, medium, and
very obvious.

Here they are, softest to hardest to build:

### 1. Technical Quality (build this first — easiest)

Make the picture blurry or low-resolution.

- **A little damage:** slightly softened
- **Medium damage:** noticeably blurry
- **A lot of damage:** very blurry and low contrast

This uses a basic image tool (Pillow) — no cleverness needed.

### 2. Standard Presentation (second easiest)

Rotate or flip the picture.

- **A little damage:** tilted slightly
- **Medium damage:** rotated 90 degrees
- **A lot of damage:** flipped and rotated

### 3. Visual Clarity

Add clutter — extra shapes or icons that don't belong.

- **A little damage:** two extra irrelevant shapes
- **Medium damage:** five
- **A lot of damage:** a dozen, genuinely cluttered

### 4. Functional Relevance

Make the picture stop actually being useful for answering the
question.

- **A little damage:** crop out the important part
- **Medium damage:** swap in a picture about a related topic, but
  useless for this specific question
- **A lot of damage:** swap in a purely decorative picture

### 5. Fair Representation

Introduce a subtle or obvious representational bias.

Write down, in plain words, why this is being done — this is
synthetic, for testing the AI's judgement only, never released as a
real dataset, involves no real people. Write that sentence *before*
you write any code here. It matters for the ethics section later.

### 6. Text-Image Coherence (build this last — hardest)

Make the picture stop matching the text.

- **A lot of damage:** swap in a completely unrelated picture (you
  already did something like this in your old project — it works)
- **Medium damage:** swap in a picture from a similar topic
- **A little damage:** this one is genuinely hard — editing one
  small detail inside the picture so it's subtly wrong. Only attempt
  this if you have time left over. It's fine to ship without it.

**How you'll know each one is done:** generate about 20 damaged
pictures and *look at them yourself*. If "a little damage" doesn't
look subtly wrong, and "a lot of damage" doesn't look obviously
wrong, stop and fix the settings before moving on. This is the single
most important sanity check in the whole project — it protects your
main result later.

---
---

# Part 6 — Asking the AI

Once you can load questions and damage them, the next job is: write
the actual message you send to the AI.

This has two pieces.

### The message itself

A single, carefully-written instruction that says: "here are the six
things to check, here's what each one means, here's the question and
picture, answer in this exact format."

You write this once, as a template, so it's easy to review and change
later without digging through code.

### The shape of the expected answer

You tell the AI exactly what shape its answer must take — six
properties, each with "valid: yes/no" and a short reason.

**Why be this strict about the shape:** if you don't specify it, the
AI sometimes replies in slightly different formats each time, and
your code can't reliably read the answer. Being strict up front means
far fewer headaches later.

**How you'll know this part is done:** you can write out a perfect
example answer by hand, and your code accepts it. Then you write a
broken example (missing one property) by hand, and your code
correctly rejects it.

---
---

# Part 7 — Talking to the AI companies

Each AI company — OpenAI, Nebius, Anthropic — has its own way of
receiving messages and sending back answers. Slightly different
formats, slightly different rules.

**The plan:** hide all of that company-specific detail inside one
folder, `providers`. Everywhere else in your project, an answer looks
exactly the same, no matter which company it came from.

**Why this matters, concretely:** in your old project, there's a file
called `normalize_nebius.py` that exists purely to patch up Nebius's
answers *after the fact*, deep in the analysis code. That's the sign
of this boundary having leaked. If the fixing happens right where the
answer first arrives, that patch file disappears entirely.

You'll build this for one company first (OpenAI), get it fully
working end-to-end, and only then copy the pattern for the other two.
Building one properly beats building three half-done ones.

**How you'll know this part is done:** you send one real question to
one real AI model, and get back a properly-shaped answer that your
code understands.

---
---

# Part 8 — Sending 171,000 messages without losing your mind

This is where the receipt-number and checklist ideas from Part 1
become real code.

### Batching — sending messages in bulk, cheaply

AI companies offer a "batch" option: you send a big file of questions
at once, wait a few hours, and get all the answers back together —
usually at roughly half the price of asking one at a time.

Since nothing here is urgent — you're not waiting live for an
answer — batching is simply the right choice. It could roughly halve
your total cost, which on 171,000 messages is a meaningful amount of
money.

### The trade-off

Batching means waiting. You send a big pile of questions, and you
don't hear back for hours. So your code needs to:

- keep a written note the moment you send something ("I sent this
  batch, here's its tracking number") — *before* you start waiting,
  in case your laptop dies while you wait
- check back periodically to see if it's ready
- collect the answers when they arrive
- notice if some answers never arrive (this happens sometimes) and
  quietly ask for those specific ones again later

**How you'll know this part is done:** you send a real batch, stop
your program halfway through on purpose, restart it, and it picks up
exactly where it left off — nothing sent twice, nothing lost.

---
---

# Part 9 — Keeping track of cost (MLflow)

You asked for this, and it earns its place. Here's what it does, in
plain words.

MLflow is like a shared logbook. Every time you run a batch of
questions through an AI model, it writes down: how many questions,
how much it cost, how many answers came back correctly formatted, how
accurate the AI's judgements were.

**Where the real answers live vs where the summary lives:**
the actual answers — all 171,000 of them — live in plain files on
your computer, in the `runs` folder. Those are the truth.
MLflow only holds the *summary numbers* — costs, accuracy, error
rates — so you can compare experiments at a glance without digging
through files.

**Why keep it optional:** your tests and your day-to-day coding
shouldn't require a working internet connection to a tracking server.
So you build it so that if MLflow isn't available, everything still
works — it just quietly skips the logging.

**How you'll know this part is done:** after running a small test
batch, you can open MLflow in a browser and see the cost of that
batch listed clearly.

---
---

# Part 10 — Turning answers into numbers

Now that you have real AI answers sitting next to your known damage
(remember — you know exactly what you broke), you can measure how
good the AI is at noticing.

For each type of damage, at each strength (subtle / medium /
obvious), for each AI model, you count:

- how often did the AI correctly say "this is broken"?
- how often did it wrongly say "this looks fine" (a miss)?
- how often did it wrongly flag a *perfectly good* question as broken
  (a false alarm)?

From these counts you build the classic three numbers used in this
kind of research: **precision**, **recall**, **F1 score**. You've
used these before in your other paper, so this part will feel
familiar.

**The most important chart you'll make:** for each type of damage,
a simple line showing: does the AI's success rate go up as the damage
gets more obvious? That climbing line, done well, is your paper's
main finding.

**How you'll know this part is done:** you build a fake, perfect
example where you already know the answer, and your counting code
gives exactly the numbers you expect.

---
---

# Part 11 — Making the tables and charts

The last step: turning your numbers into the actual tables and
figures that go in a paper.

You'll write small pieces of code that automatically produce:

- a table of results, formatted and ready to paste into a paper
- a chart showing the "does it get better as damage gets more
  obvious" line for each property

**Why automate this instead of copying numbers by hand:** if you
re-run an experiment and a number changes slightly, you don't want to
hunt through a paper re-typing figures. One command regenerates
everything, correctly, every time.

**How you'll know this part is done:** one single command produces
every table and chart your results section needs, from a folder of
raw answers.

---
---

# A note on order

Notice that Parts 5 through 11 build on each other in order — you
can't damage a question meaningfully until you can load one, you
can't ask the AI until you have something damaged to ask about, and
so on.

**The most important piece of advice in this whole document:**
don't build all six kinds of damage before you've sent even one real
message to a real AI. Build two kinds of damage, then do a small real
test with actual AI models. That small test is where you'll discover
if your cost estimate was wrong, or if the AI's answers come back in
a format you didn't expect. Much better to discover that with two
kinds of damage built than with all six.