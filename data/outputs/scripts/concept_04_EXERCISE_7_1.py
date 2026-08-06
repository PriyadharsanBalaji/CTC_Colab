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
        nodes = [Dot().shift(RIGHT * i) for i in range(5)]
        arrows = [Arrow(nodes[i], nodes[i+1]) for i in range(4)]
        self.play(Create(VGroup(*nodes, *arrows)))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 2
        arrows = [Arrow(nodes[i], nodes[i]) for i in range(5)]
        self.play(Create(VGroup(*nodes, *arrows)))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 3
        arrows = [Arrow(nodes[i], nodes[i+1]) for i in range(4)]
        self.play(Create(VGroup(*nodes, *arrows)))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 4
        nodes = [Dot().shift(RIGHT * i) for i in range(6)]
        arrows = [Arrow(nodes[i], nodes[i+1]) for i in range(4)]
        arrows[-1].put_tip()
        self.play(Create(VGroup(*nodes, *arrows)))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 5
        nodes = [Text(chr(65 + i)).shift(RIGHT * i) for i in range(10)]
        arrows = [Arrow(nodes[i], nodes[i+1]) for i in range(4)]
        self.play(Create(VGroup(*nodes, *arrows)))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 6
        nodes = [Dot().shift(RIGHT * i) for i in range(10)]
        arrows = [Arrow(nodes[i], nodes[i+1]) for i in range(3)]
        self.play(Create(VGroup(*nodes, *arrows)))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 7
        nodes = [Text("H").shift(RIGHT * i) for i in range(2)]
        arrows = [Arrow(nodes[i], nodes[i+1]) for i in range(2)]
        self.play(Create(VGroup(*nodes, *arrows)))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 8
        nodes = [Text(chr(65 + i)).shift(RIGHT * i) for i in range(5)]
        arrows = [Arrow(nodes[i], nodes[i+1]) for i in range(2)]
        self.play(Create(VGroup(*nodes, *arrows)))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 9
        formulas = MathTex("P(n, r) = n! / (n-r)!").scale(0.7)
        formulas2 = MathTex("C(n, r) = n! / (r!(n-r)!)").scale(0.7)
        formulas.arrange(DOWN).move_to(ORIGIN)
        self.play(Write(formulas))
        self.wait(2)
        self.play(Write(formulas2))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 10
        recap = Text("In summary, we learned how to calculate permutations and combinations using sets and simple mathematical operations.").scale(0.7)
        recap.move_to(ORIGIN)
        self.play(Write(recap))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))