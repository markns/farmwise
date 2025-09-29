from farmwise.schema import CourseData, Section, SectionList, SectionRow
from farmwise.whatsapp.flows.courses import push_pull

courses_section_list = SectionList(
    button_title="Select course",
    sections=[
        Section(
            title="Agronomy",
            rows=[
                SectionRow(
                    title="Push-pull technique",
                    callback_data=CourseData(title="The Push-Pull technique", name=push_pull.FLOW_NAME),
                ),
            ],
        ),
        Section(
            title="Reg Ag Practices",
            rows=[
                SectionRow(
                    title="Integrated Pest Management",
                    callback_data=CourseData(title="The Push-Pull technique", name=push_pull.FLOW_NAME),
                ),
                SectionRow(
                    title="Agroforestry (intro lesson)",
                    callback_data=CourseData(title="The Push-Pull technique", name=push_pull.FLOW_NAME),
                ),
                SectionRow(
                    title="Pruning", callback_data=CourseData(title="The Push-Pull technique", name=push_pull.FLOW_NAME)
                ),
                SectionRow(
                    title="Alley cropping",
                    callback_data=CourseData(title="The Push-Pull technique", name=push_pull.FLOW_NAME),
                ),
                SectionRow(
                    title="Conservation tillage",
                    callback_data=CourseData(title="The Push-Pull technique", name=push_pull.FLOW_NAME),
                ),
                SectionRow(
                    title="Composting",
                    callback_data=CourseData(title="The Push-Pull technique", name=push_pull.FLOW_NAME),
                ),
                SectionRow(
                    title="Crop-Livestock Integration (in review)",
                    callback_data=CourseData(title="The Push-Pull technique", name=push_pull.FLOW_NAME),
                ),
                SectionRow(
                    title="Intercropping",
                    callback_data=CourseData(title="The Push-Pull technique", name=push_pull.FLOW_NAME),
                ),
                SectionRow(
                    title="Crop rotation",
                    callback_data=CourseData(title="The Push-Pull technique", name=push_pull.FLOW_NAME),
                ),
            ],
        ),
        # Section(
        #     title="Financial literacy",
        #     rows=[],
        # ),
    ],
)
