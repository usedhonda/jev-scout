def reply(message, classify, generate, tools):
    label = classify(message, ["search", "calendar", "none"])
    context = tools[label](message) if label in tools else ""
    return generate(message, context)
