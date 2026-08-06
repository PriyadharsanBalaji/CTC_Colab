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
        objects = VGroup(*[Text(f"{chr(65+i)}") for i in range(4)]).arrange(RIGHT).to_edge(UP)
        arrow = Arrow(ORIGIN, RIGHT, color=WHITE).next_to(objects, DOWN)
        self.play(Write(objects), Create(arrow))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 2
        choices = VGroup(*[MathTex(f"{i+1}") for i in range(4)]).arrange(RIGHT).to_edge(UP)
        arrows = VGroup(*[Arrow(choices[i].get_bottom(), choices[i+1].get_top(), color=WHITE) for i in range(3)])
        self.play(Write(choices), Create(arrows))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 3
        letters = VGroup(*[MathTex(f"N, U, M, B, E, R") for _ in range(3)]).arrange(RIGHT).to_edge(UP)
        arrows = VGroup(*[Arrow(letters[i].get_bottom(), letters[i+1].get_top(), color=WHITE) for i in range(2)])
        self.play(Write(letters), Create(arrows))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 4
        letters = VGroup(*[MathTex(f"N, U, M, B, E, R") for _ in range(3)]).arrange(RIGHT).to_edge(UP)
        arrows = VGroup(*[Arrow(letters[i].get_bottom(), letters[i].get_bottom(), color=WHITE) for i in range(3)])
        self.play(Write(letters), Create(arrows))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 5
        formula = MathTex(r"n! / (n-r)!").to_edge(UP)
        arrows = VGroup(*[Arrow(formula[i].get_bottom(), formula[i+1].get_top(), color=WHITE) for i in range(2)])
        self.play(Write(formula), Create(arrows))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 6
        formula = MathTex(r"6! / (6-3)!").to_edge(UP)
        self.play(Write(formula))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 7
        formula = MathTex(r"6^3").to_edge(UP)
        self.play(Write(formula))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 8
        recap = VGroup(Text("Permutations are arrangements of objects in a definite order."),
                      MathTex(r"n! / (n-r)!").scale(0.7)).arrange(DOWN).to_edge(UP)
        self.play(Write(recap))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))