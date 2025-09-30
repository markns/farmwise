from __future__ import annotations

import base64
from pathlib import Path

from pywa.types.flows import (
    CompleteAction,
    FlowJSON,
    Footer,
    Image,
    Layout,
    NavigateAction,
    Next,
    Screen,
    TextBody,
    TextHeading,
)

from farmwise.whatsapp.flows.courses.courses import FlowCourse


def image_to_base64(image: str) -> str:
    module_path = Path(__file__).resolve().parent
    image_path = module_path.joinpath(Path(f"images/{image}"))

    with open(image_path, "rb") as image_file:
        encoded_bytes = base64.b64encode(image_file.read())
        encoded_str = encoded_bytes.decode("utf-8")
    return encoded_str


class PushPullCourse(FlowCourse):
    @property
    def name(self) -> str:
        return "Push-Pull Technique"

    @property
    def description(self) -> str:
        return "how to set up and run a push–pull plot that reduces stemborers, fall armyworm and Striga"

    @property
    def category(self) -> str:
        return "Agronomy"

    def flow_json(self) -> FlowJSON:
        return FlowJSON(
            version=7.0,
            screens=[
                Screen(
                    id="LESSON_ONE",
                    title="What is the push–pull technique?",
                    layout=Layout(
                        children=[
                            TextHeading(text="What is push–pull?"),
                            Image(src=image_to_base64("lesson1.jpg"), aspect_ratio=2, width=508, height=220),
                            TextBody(
                                text="""Push–pull is a way of farming that protects maize and sorghum from pests. 

You plant one crop that pushes the pests away, and another crop around the edges that pulls them out of your crop. 

The push crop is called desmodium, and it grows between the rows of maize. 

The pull crop is Napier grass or Brachiaria grass, planted all around the edge of the field. 

Together they stop insects like stemborer and fall armyworm, and they also fight Striga weed.
"""
                            ),
                            Footer(
                                label="Next",
                                on_click_action=NavigateAction(
                                    next=Next(name="LESSON_TWO"),
                                ),
                            ),
                        ],
                    ),
                ),
                Screen(
                    id="LESSON_TWO",
                    title="How to plan your field",
                    layout=Layout(
                        children=[
                            TextHeading(text="How to plan your field"),
                            Image(src=image_to_base64("lesson2.jpg"), aspect_ratio=2, width=508, height=220),
                            TextBody(
                                text="""First, choose your push crop - Desmodium is the best for this.

After that, choose your pull crop. If your area has enough rain, plant Napier grass.

If your area is drier, use Brachiaria grass because it grows better with less water.

Make your plot not too big – less than 50 metres by 50 metres works best.

Always plant at the beginning of the rains so that everything grows well."""
                            ),
                            Footer(
                                label="Next",
                                on_click_action=NavigateAction(
                                    next=Next(name="LESSON_THREE"),
                                ),
                            ),
                        ],
                    ),
                ),
                Screen(
                    id="LESSON_THREE",
                    title="What you will need",
                    terminal=True,
                    layout=Layout(
                        children=[
                            TextHeading(text="What you will need"),
                            Image(src=image_to_base64("lesson3.jpg"), aspect_ratio=1),
                            TextBody(
                                text="""You will need desmodium seed or vines, and planting materials for Napier or Brachiaria grass.

You can also use some manure or fertiliser to help the border grass grow strong.

A hoe, pegs, and a tape measure will help you to lay out the field neatly."""
                            ),
                            Footer(
                                label="Next",
                                on_click_action=NavigateAction(
                                    next=Next(name="LESSON_FOUR"),
                                ),
                            ),
                        ],
                    ),
                ),
                Screen(
                    id="LESSON_FOUR",
                    title="How to set up the field",
                    terminal=True,
                    layout=Layout(
                        children=[
                            TextHeading(text="How to set up the field"),
                            Image(src=image_to_base64("lesson4.jpg"), aspect_ratio=1),
                            TextBody(
                                text="""Start by planting the border grass. Plant three rows of Napier or three to four rows of Brachiaria all around the outside of your field.

Leave a space of one metre between the grass and the first maize row so you can walk.

Then plant your maize in straight rows. Between each maize row, plant a line of desmodium.

This way, every maize row has desmodium next to it."""
                            ),
                            Footer(
                                label="Next",
                                on_click_action=NavigateAction(
                                    next=Next(name="LESSON_FIVE"),
                                ),
                            ),
                        ],
                    ),
                ),
                Screen(
                    id="LESSON_FIVE",
                    title="Planting day",
                    terminal=True,
                    layout=Layout(
                        children=[
                            TextHeading(text="Planting day"),
                            TextBody(
                                text="""It is best to plant the border grass before the maize, but you can also plant everything at the same time.

Plant the maize first, then sow desmodium seed in shallow lines between the rows.

If you do not have seed, you can use vine cuttings of desmodium.

Cover the seed or vines lightly with soil and press it down gently.

Make sure you plant when the rains have started, or water well if possible."""
                            ),
                            Footer(
                                label="Next",
                                on_click_action=NavigateAction(
                                    next=Next(name="LESSON_SIX"),
                                ),
                            ),
                        ],
                    ),
                ),
                Screen(
                    id="LESSON_SIX",
                    title="Looking after the young plants",
                    terminal=True,
                    layout=Layout(
                        children=[
                            TextHeading(text="Looking after the young plants"),
                            Image(src=image_to_base64("lesson6.jpg"), aspect_ratio=1),
                            TextBody(
                                text="""Keep weeds away so that desmodium and maize can grow well.

After three weeks and again after six weeks, cut back the desmodium so it does not cover the maize.

Use the cuttings as mulch on the soil or as fodder for animals.

If any border grass fails to grow, replant quickly so the border is strong."""
                            ),
                            Footer(
                                label="Next",
                                on_click_action=NavigateAction(
                                    next=Next(name="LESSON_SEVEN"),
                                ),
                            ),
                        ],
                    ),
                ),
                Screen(
                    id="LESSON_SEVEN",
                    title="Checking for pests",
                    terminal=True,
                    layout=Layout(
                        children=[
                            TextHeading(text="Checking for pests"),
                            Image(src=image_to_base64("lesson7.jpg"), aspect_ratio=1),
                            TextBody(
                                text="""Each week, look at your maize leaves. If you see damage, check the Napier or Brachiaria grass at the edge.

Many times, you will find that the insects are laying eggs on the grass and not in your maize. That means the system is working.

If the pests are still too many, you can use handpicking or a safe spray, but usually push–pull reduces the problem a lot."""
                            ),
                            Footer(
                                label="Next",
                                on_click_action=NavigateAction(
                                    next=Next(name="LESSON_EIGHT"),
                                ),
                            ),
                        ],
                    ),
                ),
                Screen(
                    id="LESSON_EIGHT",
                    title="Using the fodder and keeping the system strong",
                    terminal=True,
                    layout=Layout(
                        children=[
                            TextHeading(text="Using the fodder and keeping the system strong"),
                            TextBody(
                                text="""You can cut desmodium and grass to feed your animals, but do not let them graze directly in the field.

Keep the grass border thick and replace sick or dead plants. Healthy borders protect your maize and also give you good fodder."""
                            ),
                            Footer(
                                label="Finish",
                                on_click_action=CompleteAction(),
                            ),
                        ],
                    ),
                ),
            ],
        )
