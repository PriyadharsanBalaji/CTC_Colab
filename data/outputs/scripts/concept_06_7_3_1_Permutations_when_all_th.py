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
        objects = VGroup(*[Circle(radius=0.5, color=BLUE) for _ in range(3)]).arrange(RIGHT)
        self.play(Create(objects))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 2
        objects = VGroup(*[Circle(radius=0.5, color=BLUE) for _ in range(3)]).arrange(RIGHT)
        arrow1 = Arrow(start=objects[0].get_right(), end=objects[1].get_left(), color=RED)
        self.play(Create(objects), Create(arrow1))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 3
        objects = VGroup(*[Circle(radius=0.5, color=BLUE) for _ in range(3)]).arrange(RIGHT)
        arrow2 = Arrow(start=objects[1].get_right(), end=objects[2].get_left(), color=RED)
        self.play(Create(objects), Create(arrow2))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 4
        objects = VGroup(*[Circle(radius=0.5, color=BLUE) for _ in range(3)]).arrange(RIGHT)
        arrow1 = Arrow(start=objects[0].get_right(), end=objects[1].get_left(), color=RED)
        arrow2 = Arrow(start=objects[1].get_right(), end=objects[2].get_left(), color=RED)
        formula = MathTex("n! = n(n-1)(n-2)...(n-r+1)").scale(0.7)
        self.play(Create(objects), Create(arrow1), Create(arrow2), Write(formula))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 5
        numbers = VGroup(*[Text(str(i), font_size=30) for i in range(1, 6)]).arrange(RIGHT)
        product = MathTex("1 \\times 2 \\times 3 \\times 4 \\times 5").scale(0.7)
        self.play(Create(numbers), Write(product))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 6
        expressions = VGroup(
            MathTex("5! = 120"),
            MathTex("7! = 5040"),
            MathTex("7! - 5! = 4920")
        ).arrange(DOWN).scale(0.7)
        self.play(Create(expressions))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 7
        formula = MathTex("nPr = \\frac{n!}{(n-r)!}").scale(0.7)
        example = MathTex("5P3 = \\frac{5!}{(5-3)!} = \\frac{5!}{2!} = 60").scale(0.7)
        self.play(Create(formula), Create(example))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 8
        equation = MathTex("x! = 120").scale(0.7)
        solution = MathTex("x = 5").scale(0.7)
        self.play(Create(equation))
        self.wait(2)
        self.play(Create(solution))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 9
        recap = VGroup(
            MathTex("nPr = \\frac{n!}{(n-r)!}"),
            MathTex("n! = n(n-1)(n-2)...(n-r+1)")
        ).arrange(DOWN).scale(0.7)
        self.play(Create(recap))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))