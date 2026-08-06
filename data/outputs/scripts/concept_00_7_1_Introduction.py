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
        # Scene 1: Setting the Scene
        grid = VGroup(*[VGroup(*[Text(str(i)) for i in range(10)]) for _ in range(4)]).arrange(RIGHT, buff=0.5).shift(UP*2)
        first_digit = Text("7").set_color(YELLOW).next_to(grid[0][0], UP)
        self.play(Create(grid), Create(first_digit))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 2: Choosing the Second Digit
        second_digit_choices = VGroup(*[Text(str(i)) for i in range(10) if i != 7]).arrange(RIGHT, buff=0.5).shift(UP*2)
        arrow = Arrow(start=first_digit.get_bottom(), end=second_digit_choices[0].get_top(), color=BLUE)
        self.play(Create(second_digit_choices), Create(arrow))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 3: Choosing the Third Digit
        third_digit_choices = VGroup(*[Text(str(i)) for i in range(10) if i != 7 and i != second_digit_choices[0].get_text()]).arrange(RIGHT, buff=0.5).shift(UP*2)
        arrow = Arrow(start=second_digit_choices[0].get_bottom(), end=third_digit_choices[0].get_top(), color=BLUE)
        self.play(Create(third_digit_choices), Create(arrow))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 4: Calculating the Total Combinations
        numbers = VGroup(Text("9"), Text("8"), Text("7")).arrange(RIGHT, buff=0.5).shift(UP*2)
        multiplication_sign = MathTex("\\times").next_to(numbers[1], LEFT)
        result = MathTex("504").scale(0.7).next_to(numbers, DOWN, buff=1)
        self.play(Create(numbers), Create(multiplication_sign))
        self.wait(2)
        self.play(Create(result))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 5: Final Answer
        final_result = MathTex("504").scale(0.7).shift(UP*2)
        self.play(Create(final_result))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Scene 6: Recap
        recap_text = MathTex("9 \\times 8 \\times 7 = 504").scale(0.7).shift(UP*2)
        result = MathTex("504").scale(0.7).next_to(recap_text, DOWN, buff=1)
        self.play(Create(recap_text), Create(result))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))