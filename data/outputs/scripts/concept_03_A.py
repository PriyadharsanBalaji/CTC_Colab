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
        flags = VGroup(*[Text(f"Flag {i+1}", font_size=30) for i in range(4)])
        staff = Line([-3, 0, 0], [3, 0, 0], color=WHITE)
        flags.arrange(DOWN, center=True).next_to(staff, UP)
        self.play(Create(staff), Create(flags))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 2
        arrow = Arrow(staff.get_end(), flags[1].get_center(), color=WHITE)
        self.play(Create(arrow), Write(MathTex("4 \\times 3 = 12", font_size=30).next_to(arrow, RIGHT)))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 3
        number_cards = VGroup(*[Text(str(i), font_size=30) for i in range(1, 6)])
        number_cards.arrange(RIGHT, center=True).to_edge(UP)
        self.play(Create(number_cards))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 4
        arrow = Arrow(number_cards[1].get_center(), number_cards[0].get_center(), color=WHITE)
        self.play(Create(arrow), Write(MathTex("2 \\times 5 = 10", font_size=30).next_to(arrow, LEFT)))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 5
        formula = MathTex("P(n, r) = n \\times (n-1) \\times (n-2) \\times \\ldots \\times (n-r+1)", font_size=30)
        self.play(Write(formula))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 6
        self.play(Write(MathTex("P(4, 2) = 4 \\times 3 = 12", font_size=30)))
        self.play(Write(MathTex("P(5, 2) = 2 \\times 5 = 10", font_size=30)))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 7
        flags = VGroup(*[Text(f"Flag {i+1}", font_size=30) for i in range(5)])
        flags.arrange(RIGHT, center=True).to_edge(UP)
        self.play(Create(flags))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 8
        self.play(Write(MathTex("2 + 3 + 4 + 5 = 14", font_size=30)))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 9
        recap = VGroup(
            Text("Permutations", font_size=40),
            Text("are calculated using the multiplication principle.", font_size=30),
            Text("We can apply this principle to various scenarios.", font_size=30)
        ).arrange(DOWN, center=True).to_edge(UP)
        self.play(Create(recap))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))