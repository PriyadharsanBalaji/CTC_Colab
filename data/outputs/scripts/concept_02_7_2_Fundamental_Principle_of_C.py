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
        pants = VGroup(*[Circle(radius=0.5) for _ in range(3)]).arrange(RIGHT, buff=1)
        shirts = VGroup(*[Circle(radius=0.5) for _ in range(2)]).arrange(RIGHT, buff=1)
        pants.shift(LEFT * 2)
        shirts.shift(RIGHT * 2)
        self.play(Create(pants), Create(shirts))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 2
        pant_choices = VGroup(*[Arrow(start=pants[i].get_center(), end=pants[i].get_center() + UP * 1.5) for i in range(3)])
        self.play(Create(pant_choices))
        self.play(Write(MathTex("3 \\text{ choices for pants}").next_to(pant_choices, UP)))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 3
        shirt_choices = VGroup(*[Arrow(start=shirts[i].get_center(), end=shirts[i].get_center() + UP * 1.5) for i in range(2)])
        self.play(Create(shirt_choices))
        self.play(Write(MathTex("2 \\text{ choices for shirts}").next_to(shirt_choices, UP)))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 4
        pairs = VGroup(*[VGroup(pants[i], shirts[j]).arrange(DOWN, buff=0.5) for i in range(3) for j in range(2)])
        pairs.arrange(RIGHT, buff=2)
        self.play(Create(pairs))
        self.play(Write(MathTex("3 \\times 2 = 6").next_to(pairs, UP)))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 5
        fp_formula = MathTex("m \\times n").scale(0.7)
        self.play(Create(fp_formula))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 6
        fp_three_events = MathTex("m \\times n \\times p").scale(0.7)
        self.play(Create(fp_three_events))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 7
        applying_principle = VGroup(
            Text("Applying the Principle"),
            Text("Choose Pant, then Choose Shirt").next_to(Text("Applying the Principle"), DOWN)
        ).arrange(DOWN).move_to(ORIGIN)
        self.play(Create(applying_principle))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 8
        applying_principle_sabnam = VGroup(
            Text("Applying the Principle to Sabnam"),
            Text("Choose School Bag, then Tiffin Box, then Water Bottle").next_to(Text("Applying the Principle to Sabnam"), DOWN)
        ).arrange(DOWN).move_to(ORIGIN)
        self.play(Create(applying_principle_sabnam))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 9
        recap = VGroup(
            Text("Recap"),
            Text("Fundamental Principle of Counting: m \\times n \\times p").next_to(Text("Recap"), DOWN)
        ).arrange(DOWN).move_to(ORIGIN)
        self.play(Create(recap))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))