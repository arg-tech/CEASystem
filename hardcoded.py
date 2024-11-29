article = """EU Bans ChatGPT's Advanced Voice Mode Over Non-Compliance with AI Act Regulations

The European Union has banned OpenAI’s ChatGPT Advanced Voice Mode, pointing to non-compliance with the recently enforced EU AI Act. This new regulatory framework, which aims to ensure responsible and transparent AI usage across Europe, has led to stricter scrutiny of AI applications, particularly those involving human-like interactions.

OpenAI CEO Sam Altman explained on X that the voice mode will remain inaccessible in the EU, due to regulatory compliance issues, acknowledging the difficult balance between innovation and adhering to global regulations. The company has been working to navigate the various legal frameworks around AI, but it appears the EU's strict guidelines are creating a significant roadblock for deploying that voice-enabled feature in Europe.

The EU's AI Act aims to ensure that AI systems are safe, ethical, and transparent. The regulation places particular emphasis on preventing AI technologies from misleading users or being used for manipulative purposes. This particularly in contexts where AI systems can infer human emotions, such as for the voice-based advanced system (cf. Recital 44).

While the EU's decision is seen as a necessary step toward safeguarding users, it has sparked a debate about the balance between regulation and innovation. Critics are numerous: as remarked by the Welsh politician Tom Giffard in a speech in the Welsh Parliament, overly stringent regulations could stifle important technological advancements such as the Advanced Voice Mode. 

Will the tradeoff between the AI potential and risks affect the future EU SMEs?"""

article_2 = """LATIF - News

EU Bans ChatGPT's Advanced Voice Mode Over Non-Compliance with AI Act Regulations\n\nThe European Union has banned OpenAI’s ChatGPT Advanced Voice Mode, pointing to non-compliance with the recently enforced EU AI Act.
 
This new regulatory framework, which aims to ensure responsible and transparent AI usage across Europe, has led to stricter scrutiny of AI applications, particularly those involving human-like interactions.
 
OpenAI CEO Sam Altman explained on X that the voice mode will remain inaccessible in the EU, due to regulatory compliance issues, acknowledging the difficult balance between innovation and adhering to global regulations.
 
The company has been working to navigate the various legal frameworks around AI, but it appears the EU's strict guidelines are creating a significant roadblock for deploying that voice-enabled feature in Europe."""


article_3 = """EU Bans ChatGPT's Advanced Voice Mode Over Non-Compliance with AI Act Regulations\n\nThe European Union has banned OpenAI’s ChatGPT Advanced Voice Mode, pointing to non-compliance with the recently enforced EU AI Act.
 
This new regulatory framework, which aims to ensure responsible and transparent AI usage across Europe, has led to stricter scrutiny of AI applications, particularly those involving human-like interactions.
 
OpenAI CEO Sam Altman explained on X that the voice mode will remain inaccessible in the EU, due to regulatory compliance issues, acknowledging the difficult balance between innovation and adhering to global regulations.
 
The company has been working to navigate the various legal frameworks around AI, but it appears the EU's strict guidelines are creating a significant roadblock for deploying that voice-enabled feature in Europe."""

article_2 = article_2.replace("\n", "").replace(" ", "").replace("\t", "")
article = article.replace("\n", "").replace(" ", "").replace("\t", "")
article_3 = article_3.replace("\n", "").replace(" ", "").replace("\t", "")

demo_utility_hardcoded_articles = {
        article: [
"EU Bans ChatGPT's Advanced Voice Mode Over Non-Compliance with AI Act Regulations",
"OpenAI CEO Sam Altman explained on X that the voice mode will remain inaccessible in the EU, due to regulatory compliance issues, acknowledging the difficult balance between innovation and adhering to global regulations.",
"This particularly in contexts where AI systems can infer human emotions, such as for the voice-based advanced system (cf. Recital 44).",
"Critics are numerous: as remarked by the Welsh politician Tom Giffard in a speech in the Welsh Parliament, overly stringent regulations could stifle important technological advancements such as the Advanced Voice Mode"
            ],

        article_2: [
        "EU Bans ChatGPT's Advanced Voice Mode Over Non-Compliance with AI Act Regulations",
        "OpenAI CEO Sam Altman explained on X that the voice mode will remain inaccessible in the EU, due to regulatory compliance issues, acknowledging the difficult balance between innovation and adhering to global regulations.",
        "This particularly in contexts where AI systems can infer human emotions, such as for the voice-based advanced system (cf. Recital 44).",
        "Critics are numerous: as remarked by the Welsh politician Tom Giffard in a speech in the Welsh Parliament, overly stringent regulations could stifle important technological advancements such as the Advanced Voice Mode"
        ],
        article_3: [
"EU Bans ChatGPT's Advanced Voice Mode Over Non-Compliance with AI Act Regulations",
"OpenAI CEO Sam Altman explained on X that the voice mode will remain inaccessible in the EU, due to regulatory compliance issues, acknowledging the difficult balance between innovation and adhering to global regulations.",
"This particularly in contexts where AI systems can infer human emotions, such as for the voice-based advanced system (cf. Recital 44).",
"Critics are numerous: as remarked by the Welsh politician Tom Giffard in a speech in the Welsh Parliament, overly stringent regulations could stifle important technological advancements such as the Advanced Voice Mode"
            ]
        }

