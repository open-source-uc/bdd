def get_description(syllabus: str):
    "Extract description from program."
    if not syllabus:
        return None
    start_description = syllabus.find("DESCRIP")
    if start_description != -1:
        start_description = syllabus.find("\n", start_description)
        end_description = syllabus.find("II", start_description)
        return syllabus[start_description:end_description]
    else:
        return None
