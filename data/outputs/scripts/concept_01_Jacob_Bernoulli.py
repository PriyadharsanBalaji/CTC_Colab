from manim import *

# --- Safety Monkey Patches for LLM Generated Code ---
_original_create = Create
_original_write = Write
_original_fadein = FadeIn
_original_fadeout = FadeOut

def _safe_wrap(mobj):
    if isinstance(mobj, list):
        return VGroup(*[_safe_wrap(m) for m in mobj])
    return mobj

class SafeCreate(_original_create):
    def __init__(self, mobject, **kwargs):
        super().__init__(_safe_wrap(mobject), **kwargs)

class SafeWrite(_original_write):
    def __init__(self, mobject, **kwargs):
        super().__init__(_safe_wrap(mobject), **kwargs)

class SafeFadeIn(_original_fadein):
    def __init__(self, *mobjects, **kwargs):
        super().__init__(*[_safe_wrap(m) for m in mobjects], **kwargs)

class SafeFadeOut(_original_fadeout):
    def __init__(self, *mobjects, **kwargs):
        super().__init__(*[_safe_wrap(m) for m in mobjects], **kwargs)

Create = SafeCreate
Write = SafeWrite
FadeIn = SafeFadeIn
FadeOut = SafeFadeOut
# ---------------------------------------------------

class ConceptScene(Scene):
    def construct(self):
        # Scene 1
        title = MathTex("Counting Techniques").scale(1.5)
        self.play(FadeIn(title))
        self.wait(2)
        self.play(FadeOut(title))
        self.wait(1)

        # Scene 2
        n_circles = VGroup(*[Dot(radius=0.1) for _ in range(3)]).arrange(RIGHT, buff=0.5)
        m_circles = VGroup(*[Dot(radius=0.1) for _ in range(4)]).arrange(RIGHT, buff=0.5)
        n_circles.shift(LEFT * 2)
        m_circles.shift(RIGHT * 2)
        n_to_m = MathTex("n \\times m").scale(0.7).next_to(n_circles, RIGHT)
        self.play(FadeIn(n_circles), FadeIn(m_circles), FadeIn(n_to_m))
        self.wait(2)
        self.play(FadeOut(n_circles), FadeOut(m_circles), FadeOut(n_to_m))
        self.wait(1)

        # Scene 3
        pants = VGroup(*[Dot(radius=0.1) for _ in range(3)]).arrange(RIGHT, buff=0.5)
        shirts = VGroup(*[Dot(radius=0.1) for _ in range(2)]).arrange(RIGHT, buff=0.5)
        pants.shift(LEFT * 2)
        shirts.shift(RIGHT * 2)
        connections = VGroup(*[Arrow(start=p, end=s) for p in pants for s in shirts])
        self.play(FadeIn(pants), FadeIn(shirts), Create(connections))
        self.wait(2)
        self.play(FadeOut(pants), FadeOut(shirts), FadeOut(connections))
        self.wait(1)

        # Scene 4
        n_circles = VGroup(*[Dot(radius=0.1) for _ in range(3)]).arrange(RIGHT, buff=0.5)
        m_circles = VGroup(*[Dot(radius=0.1) for _ in range(4)]).arrange(RIGHT, buff=0.5)
        n_circles.shift(LEFT * 2)
        m_circles.shift(RIGHT * 2)
        n_to_m = MathTex("n \\times m").scale(0.7).next_to(n_circles, RIGHT)
        self.play(FadeIn(n_circles), FadeIn(m_circles), FadeIn(n_to_m))
        self.wait(2)
        self.play(FadeOut(n_circles), FadeOut(m_circles), FadeOut(n_to_m))
        self.wait(1)

        # Scene 5
        n_to_m = MathTex("n \\times m").scale(0.7)
        box = SurroundingRectangle(n_to_m, color=WHITE)
        self.play(FadeIn(n_to_m), Create(box))
        self.wait(2)
        self.play(FadeOut(n_to_m), FadeOut(box))
        self.wait(1)

        # Scene 6
        n_circles = VGroup(*[Dot(radius=0.1) for _ in range(3)]).arrange(RIGHT, buff=0.5)
        m_circles = VGroup(*[Dot(radius=0.1) for _ in range(4)]).arrange(RIGHT, buff=0.5)
        n_circles.shift(LEFT * 2)
        m_circles.shift(RIGHT * 2)
        n_to_m = MathTex("n \\times m").scale(0.7).next_to(n_circles, RIGHT)
        self.play(FadeIn(n_circles), FadeIn(m_circles), FadeIn(n_to_m))
        self.wait(2)
        self.play(FadeOut(n_circles), FadeOut(m_circles), FadeOut(n_to_m))
        self.wait(1)

        # Scene 7
        title = MathTex("Counting Techniques").scale(1.5)
        self.play(FadeIn(title))
        self.wait(2)
        self.play(FadeOut(title))
        self.wait(1)

        self.play(FadeOut(*self.mobjects))