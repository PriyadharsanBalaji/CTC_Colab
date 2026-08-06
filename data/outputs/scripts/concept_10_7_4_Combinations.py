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
        players = VGroup(Text("X"), Text("Y"), Text("Z")).arrange(RIGHT).shift(UP)
        arrow1 = Arrow(start=players[0].get_bottom(), end=players[1].get_top())
        arrow2 = Arrow(start=players[1].get_bottom(), end=players[0].get_top())
        self.play(FadeIn(players), Create(arrow1), Create(arrow2))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 2
        choices = VGroup(Text("Choose X"), Text("Choose Y"), Text("Choose Z")).arrange(RIGHT).shift(UP)
        self.play(FadeIn(choices))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 3
        same_team = VGroup(Text("X and Y"), Text("Y and X")).arrange(RIGHT).shift(UP)
        rectangle = Rectangle(width=2, height=1).surround(same_team)
        self.play(FadeIn(same_team), Create(rectangle))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 4
        division = MathTex("\\div", "2").shift(DOWN)
        self.play(FadeIn(division))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 5
        formula = MathTex("\\binom{n}{k}").scale(0.7).shift(UP)
        self.play(FadeIn(formula))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 6
        values = MathTex("n =", "3", ", k =", "2").arrange(RIGHT).shift(UP)
        self.play(FadeIn(values))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 7
        result = MathTex("3").scale(0.7).shift(DOWN)
        self.play(FadeIn(result))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 8
        recap_text = Text("To find the number of combinations of n items taken k at a time, use the formula n choose k. It's n! / (k! * (n-k)!).").scale(0.7).shift(DOWN)
        self.play(FadeIn(recap_text))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))