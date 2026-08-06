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
        books = VGroup(Text("A"), Text("B"), Text("C")).arrange(RIGHT).shift(UP)
        shelf = Rectangle(width=3, height=0.5).shift(DOWN)
        arrow = Arrow(start=books[0].get_bottom(), end=shelf.get_top(), color=WHITE)
        self.play(Create(books), Create(shelf), Create(arrow))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 2
        formula = MathTex("nP = \\frac{n!}{(n-r)!}").scale(0.7).shift(UP)
        self.play(Write(formula))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 3
        example = MathTex("4P3 = 24").scale(0.7).shift(UP)
        result = MathTex("24").scale(0.7).next_to(example, DOWN)
        self.play(Write(example), Write(result))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 4
        formula = MathTex("n^r").scale(0.7).shift(UP)
        self.play(Write(formula))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 5
        example = MathTex("4^3 = 64").scale(0.7).shift(UP)
        result = MathTex("64").scale(0.7).next_to(example, DOWN)
        self.play(Write(example), Write(result))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 6
        formula = MathTex("\\frac{n!}{p_1! p_2! \\cdots p_k!}").scale(0.7).shift(UP)
        self.play(Write(formula))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 7
        example = MathTex("\\text{Arranging 'ROOT'} = 12").scale(0.7).shift(UP)
        result = MathTex("12").scale(0.7).next_to(example, DOWN)
        self.play(Write(example), Write(result))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 8
        recap = VGroup(
            Text("Permutations are about arranging objects in a specific order."),
            Text("Formula: nP = n! / (n-r)!"),
            Text("Repetition: n^r"),
            Text("Non-distinct objects: \\frac{n!}{p_1! p_2! \\cdots p_k!}")
        ).arrange(DOWN).shift(UP)
        self.play(Write(recap))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))