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
        title = Text("Understanding Permutations").to_edge(UP)
        circle1 = Circle(radius=0.5).shift(LEFT * 2)
        circle2 = Circle(radius=0.5).shift(RIGHT * 2)
        circle3 = Circle(radius=0.5).shift(RIGHT * 0.5)
        arrow = Arrow(start=circle1.get_center(), end=circle2.get_center())
        self.add(title, circle1, circle2, circle3, arrow)
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 2
        title = Text("Calculating Permutations").to_edge(UP)
        formula = MathTex("nPn = n!").scale(0.7).to_edge(DOWN)
        self.add(title, formula)
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 3
        title = Text("No Repeated Digits").to_edge(UP)
        formula = MathTex("nPn = n!").scale(0.7).to_edge(DOWN)
        n = MathTex("n").scale(0.7).next_to(formula, LEFT)
        self.add(title, formula, n)
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 4
        title = Text("Calculating Permutations with No Repeats").to_edge(UP)
        formula = MathTex("9P3 = 9! / (9-3)!").scale(0.7).to_edge(DOWN)
        result = MathTex("720").scale(0.7).next_to(formula, RIGHT)
        self.add(title, formula, result)
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 5
        title = Text("Permutations with Specific Conditions").to_edge(UP)
        circles = VGroup(*[Circle(radius=0.5).shift(RIGHT * i) for i in range(6)])
        circle2 = circles[1]
        arrow = Arrow(start=circle2.get_center(), end=circle2.get_center() + DOWN)
        self.add(title, circles, arrow)
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 6
        title = Text("Calculating Permutations with Conditions").to_edge(UP)
        formula = MathTex("3 * 5P2 = 3 * 20 = 60").scale(0.7).to_edge(DOWN)
        result = MathTex("60").scale(0.7).next_to(formula, RIGHT)
        self.add(title, formula, result)
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 7
        title = Text("Combinations").to_edge(UP)
        word = Text("EQUATION").to_edge(DOWN)
        circles = VGroup(*[Circle(radius=0.5).shift(RIGHT * i) for i in range(8)])
        circle1 = circles[0]
        arrow = Arrow(start=circle1.get_center(), end=circle1.get_center() + DOWN)
        self.add(title, word, circles, arrow)
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 8
        title = Text("Calculating Combinations").to_edge(UP)
        formula = MathTex("nCr = n! / (r!(n-r)!)").scale(0.7).to_edge(DOWN)
        n = MathTex("n").scale(0.7).next_to(formula, LEFT)
        r = MathTex("r").scale(0.7).next_to(formula, RIGHT)
        self.add(title, formula, n, r)
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 9
        title = Text("Combinations with Conditions").to_edge(UP)
        word = Text("EQUATION").to_edge(DOWN)
        circles = VGroup(*[Circle(radius=0.5).shift(RIGHT * i) for i in range(8)])
        circle1 = circles[0]
        arrow = Arrow(start=circle1.get_center(), end=circle1.get_center() + DOWN)
        self.add(title, word, circles, arrow)
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 10
        title = Text("Calculating Combinations with Conditions").to_edge(UP)
        formula = MathTex("8C8 = 1").scale(0.7).to_edge(DOWN)
        result = MathTex("1").scale(0.7).next_to(formula, RIGHT)
        self.add(title, formula, result)
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 11
        title = Text("Recap").to_edge(UP)
        formulas = VGroup(
            MathTex("nPn = n!").scale(0.7),
            MathTex("nCr = n! / (r!(n-r)!)").scale(0.7)
        ).arrange(DOWN).to_edge(DOWN)
        self.add(title, formulas)
        self.wait(2)
        self.play(FadeOut(*self.mobjects))