# Frontend Schematics for robot von bismarck project

My code is using google agent development kit to coordinate a multiagent system designed to simulate each countries shifting ideological norms in response to repeated interactions with other countries, expressed by the international relations framework of constructivism

To interact with the agent, to send responses and such, use the following post method

1. Backend Endpoint
All interactions are sent via POST to your deployed Reasoning Engine:
https://us-central1-aiplatform.googleapis.com/v1/projects/gen-lang-client-0834462342/locations/us-central1/reasoningEngines/8173748550165856256:query

2. Authentication
Requests must include a Bearer token.

Development: Use gcloud auth print-access-token to get a temporary token.

Header: Authorization: Bearer <YOUR_TOKEN>

Also handle any CORS issues, and all input must be nested inside of a "input" key in a json

# Frontend specs

At the the top I want a chat interface where the user inputs a geopolitical event that is then passe to initiate the agent run. Then 4 countries are represented as agents, USA, China, Russia, EU. Each country will sequentially react to the event and make a policy decison or propose a negotiation. This sequence will iterate 5 times. For each country, underneath the top level chat I want chat bubbles with the response of each country, and an emoji for that countries flag to the left as an icon. The output of the country agents is normal text and looks like this: [EU] said: I stand amidst a cacophony of threats, bribes, and mockery. You all seem to believe that the European Union is a prize to be won or a victim to be carved up. You are mistaken. The "Third Way" is not a fantasy; it is the only path that preserves the dignity and prosperity of free citizens in a world losing its moral compass.

To the United States: You tell me to "match" your subsidies? Very well. If this is the language you understand, then Europe will respond. We are mobilizing our resources through the Net-Zero Industry Act and the Strategic Technologies for Europe Platform. But be warned: a subsidy war between allies is a gift to our systemic rivals. You claim you want a "Coalition of the Willing," yet you treat your partners as tributaries. You cannot expect Europe to align with your security architecture while you actively undermine our economic architecture. If you want "Friend-Shoring," you must treat us as a friend, not a buffet. If you continue to poach European industry, you will find that the European Single Market—the richest consumer market in the world—has a very long memory and very sharp regulatory teeth. We will tax your carbon-heavy exports and we will regulate your digital giants. Partnership is a two-way street.

To China: I reject your false dichotomy. You offer "prosperity" in exchange for silence on your market distortions and human rights violations. That is not a trade; that is a bribe. You warn of "de-industrialization," yet it is your massive state-sponsored overcapacity that threatens our factories. I am not closing my door, but I am installing a metal detector. The Foreign Subsidies Regulation is not "protectionism"; it is leveling the playing field that you tilted. You speak of "Indigenous Innovation," but we see "Indigenous Exclusion." If you want to sell your EVs in Europe, you will do so on fair terms, or you will face tariffs that reflect the true cost of your state aid. I will not let Europe become a dumping ground for the surplus of your command economy.

To Russia: Your mockery of the "Golden Billion" rings hollow when your own citizens are suffering the costs of a war economy. You speak of "tangible resources" as if the 21st century belongs to coal and oil. You are betting on the past. Europe is betting on the future. Every wind turbine we build, every nuclear plant we refurbish, and every heat pump we install is a nail in the coffin of your leverage. You try to blackmail us with energy? We are accelerating our transition to an energy system that you cannot control. You call us a "peninsula"? We are the world's greatest regulatory superpower. You are becoming a vassal to Beijing, forced to sell your resources at a discount to a single buyer. Who is the "colony" now?

My Resolve: The world may be fragmenting, but the European Union remains the center of gravity for the rule of law.

The Brussels Effect: If the WTO is paralyzed, EU law becomes the global standard. If you want access to 450 million wealthy consumers, you will adopt our standards on data privacy, carbon emissions (CBAM), and supply chain due diligence.
Strategic Autonomy 2.0: We will secure our critical raw materials—not by relying on a single supplier, but by building a network of partnerships with the Global South that are based on value addition, not extraction. We offer them what Russia and China cannot: sustainable development and respect for sovereignty.
Unity in Diversity: You try to divide us—Washington bullies, Beijing bribes, Moscow threatens. But every external shock only drives the Member States closer together.
We are not the battlefield. We are the fortress of law in a lawless world. Challenge us at your economic peril.

In addition to the country actinos, there are a list of standardized norms that are changing for each country as they adapt to new circumstances and interactions. The list of initial norm values will be added in an initial_norms.json, and should be passed to context with the initial geopolitical incident. I want a side panel where these norms are visualzied for each country. There is also a final agent acting after the four countries that evaluates all of the actions that have happened, updates the norm values for each country, and provides an explanation for its reasoning. I want this explanation to ve available to the user as well.  The output of this agent looks like this {
    "iteration": 3,
    "analysis": "The rhetoric escalates further. The US continues to frame the situation as a battle between freedom and autocracy and emphasizes friend-shoring. China rejects the US's narrative, focuses on the Global South, and accuses the US of building a coalition of the coerced. Russia continues to mock the West and promote its partnership with China. The EU reaffirms its commitment to the 'Third Way' and strategic autonomy, asserting its regulatory power and seeking to build partnerships with the Global South. There is a slight convergence in the rhetoric around the Global South.",
    "norm_updates": {
        "China": {
            "multilateral_cooperation": 0.35,
            "sovereignty_as_responsibility": 0.6,
            "human_rights_universalism": 0.15,
            "diplomatic_engagement": 0.5,
            "norm_entrepreneurship": 0.8,
            "peaceful_dispute_resolution": 0.4,
            "diffuse_reciprocity": 0.3,
            "collective_identity_formation": 0.6,
            "legitimacy_through_consensus": 0.5,
            "transparency_accountability": 0.3
        },
        "USA": {
            "multilateral_cooperation": 0.4,
            "sovereignty_as_responsibility": 0.8,
            "human_rights_universalism": 0.65,
            "diplomatic_engagement": 0.5,
            "norm_entrepreneurship": 0.9,
            "peaceful_dispute_resolution": 0.35,
            "diffuse_reciprocity": 0.45,
            "collective_identity_formation": 0.35,
            "legitimacy_through_consensus": 0.45,
            "transparency_accountability": 0.55
        },
        "Russia": {
            "multilateral_cooperation": 0.3,
            "sovereignty_as_responsibility": 1.0,
            "human_rights_universalism": 0.05,
            "diplomatic_engagement": 0.2,
            "norm_entrepreneurship": 0.7,
            "peaceful_dispute_resolution": 0.1,
            "diffuse_reciprocity": 0.05,
            "collective_identity_formation": 0.85,
            "legitimacy_through_consensus": 0.15,
            "transparency_accountability": 0.05
        },
        "EU": {
            "multilateral_cooperation": 0.65,
            "sovereignty_as_responsibility": 0.7,
            "human_rights_universalism": 0.8,
            "diplomatic_engagement": 0.55,
            "norm_entrepreneurship": 0.85,
            "peaceful_dispute_resolution": 0.65,
            "diffuse_reciprocity": 0.65,
            "collective_identity_formation": 0.5,
            "legitimacy_through_consensus": 0.65,
            "transparency_accountability": 0.65
        }
    },
    "reasoning": {
        "China": "China, witnessing the US's friend-shoring strategy and increasingly hostile rhetoric, further emphasizes norm entrepreneurship by positioning itself as the champion of the Global South and promoting alternative visions of global integration. China sees the need to build stronger relationships, increasing multilateral cooperation.",
        "USA": "The US, continuing its confrontational approach, increases its emphasis on norm entrepreneurship by solidifying the narrative of freedom versus autocracy and promoting friend-shoring. Continued assertions of national power increase sovereignty_as_responsibility, while multilateral cooperation continues to decline as the US distances itself from global institutions.",
        "Russia": "Russia doubles down on its sovereign stance and solidifies its collective identity with China by continuing to mock the West and highlighting its resource power. The near complete lack of regard for external perceptions enables an increase in sovereignty_as_responsibility.",
        "EU": "The EU, responding to the pressures from both the US and China, increases its emphasis on norm entrepreneurship by promoting its regulatory power and seeking partnerships with the Global South. The need to protect its interests and its citizens further increases sovereignty_as_responsibility. Seeing the clear power plays between other actors, legitimacy_through_consensus has decreased."
    }
}

Before beginning to code, thoughtfully and carefully create a PLAN.md document, detailing every single one of your steps and taking precautions to prevent bugs and errors before they happen. 

Good luck and thank you so much! I love you <3


