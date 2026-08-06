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
        title = Text("Factorial Basics").scale(1.5)
        formula = MathTex(r"n! = n \times (n-1) \times (n-2) \times \ldots \times 1")
        arrow = Arrow(start=RIGHT, end=RIGHT + 2 * RIGHT).next_to(formula, RIGHT)
        self.play(Write(title), Write(formula), Create(arrow))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 2
        title = Text("Evaluate 8! and 4! - 3!").scale(1.5)
        factorial_8 = MathTex(r"8! = 8 \times 7 \times 6 \times 5 \times 4 \times 3 \times 2 \times 1 = 40320")
        factorial_4_minus_3 = MathTex(r"4! - 3! = 24 - 6 = 18")
        self.play(Write(title), Write(factorial_8), Write(factorial_4_minus_3))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 3
        title = Text("Check if 3! + 4! = 7!").scale(1.5)
        equation = MathTex(r"3! + 4! = 6 + 24 = 30")
        self.play(Write(title), Write(equation))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 4
        title = Text("Solve for x").scale(1.5)
        equation = MathTex(r"6! \times 2! = 7! \div x")
        solution = MathTex(r"x = \frac{7!}{6! \times 2!}")
        self.play(Write(title), Write(equation), Write(solution))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 5
        title = Text("Evaluate n! / (n-r)! for n=6, r=2").scale(1.5)
        formula = MathTex(r"6! / (6-2)! = 6! / 4! = 15")
        self.play(Write(title), Write(formula))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 6
        title = Text("Evaluate n! / (n-r)! for n=9, r=5").scale(1.5)
        formula = MathTex(r"9! / (9-5)! = 9! / 4! = 126")
        self.play(Write(title), Write(formula))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 7
        title = Text("Recap").scale(1.5)
        formulas = VGroup(
            MathTex(r"n! = n \times (n-1) \times (n-2) \times \ldots \times 1"),
            MathTex(r"n! - (n-1)! = n-1"),
            MathTex(r"n! / (n-r)! = n \times (n-1) \times \ldots \times (n-r+1)")
        ).arrange(DOWN).scale(0.7).move_to(ORIGIN)
        self.play(Write(title), Write(formulas))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))